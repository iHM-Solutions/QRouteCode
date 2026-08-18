import os
import sys
import io
from urllib.parse import urlencode

# Tell Python to check your isolated subfolder for the third-party modules
current_dir = os.path.dirname(__file__)
vendor_path = os.path.join(current_dir, "vendor")

if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)


import qrcode


from qgis.core import QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsWkbTypes, QgsPointXY
from qgis.utils import iface
from qgis.PyQt.QtWidgets import (QFileDialog, QAction, QDialog, QVBoxLayout, QLabel, 
                                QPushButton, QHBoxLayout, QMessageBox, QComboBox, QTextEdit, QFrame, 
                                QGroupBox, QLineEdit)
from qgis.PyQt.QtGui import QPixmap, QIcon, QImage, QPainter, QColor
from qgis.PyQt.QtCore import Qt



class PolylineQRExporter:
    def __init__(self, iface):
        self.iface = iface
        self.action = None


    def initGui(self):
         # 1. Resolve the absolute path to your local icon.png file safely
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        
        # 2. Initialize the QAction button with the custom icon layout image
        self.action = QAction(QIcon(icon_path), "QRouteCode Exporter", self.iface.mainWindow())
        
        # Connect action to trigger window load execution parameters
        self.action.triggered.connect(self.run)
        
        # Adds the tool cleanly to the QGIS top dropdown menu structure and layout icon toolbar bars
        self.iface.addPluginToMenu("&QRouteCode Exporter", self.action)
        self.iface.addToolBarIcon(self.action)


    def unload(self):
        if self.action:
            self.iface.removePluginMenu("&QRouteCode Exporter", self.action)
            self.iface.removeToolBarIcon(self.action)


    def run(self):
        dialog = NewExporterGUIDialog(self.iface)
        dialog.exec()



class NewExporterGUIDialog(QDialog):


    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.generated_url = ""
        self.setWindowTitle("QRouteCode - Polyline to Google Maps QR")

        # SET THE DIALOG TITLE BAR ICON NATIVELY
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.setWindowIcon(QIcon(self.icon_path))

        self.setMinimumWidth(500)
        self.init_ui()


    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)

        # Create Input Group Box for Layer Selection
        input_group_layout = QGroupBox("")
        input_group_layout.setStyleSheet("QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 10px; margin-bottom: 20px;} QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }")
        input_group_box_layout = QVBoxLayout()

        # 2. MODO DE VIAJE Y BOTÓN HELP
        travel_mode_layout = QHBoxLayout()
        travel_mode_layout.addWidget(QLabel("<b>Travel Mode:</b>"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItem("Walking", "walking")
        self.combo_mode.addItem("Driving", "driving")
        self.combo_mode.addItem("Bicycling", "bicycling")
        travel_mode_layout.addWidget(self.combo_mode)
        
        self.btn_help = QPushButton("ℹ️ Help")
        self.btn_help.setFixedWidth(80)
        self.btn_help.clicked.connect(self.show_help_info)
        travel_mode_layout.addWidget(self.btn_help)
        input_group_box_layout.addLayout(travel_mode_layout)

        selected_polyline_layout = QHBoxLayout()
        selected_polyline_layout.addWidget(QLabel("<b>Selected Layer:</b>"))
        selected_layer = self.iface.activeLayer().name() if self.iface.activeLayer() else "None"
        widget_selected_layer = QLineEdit(selected_layer)
        widget_selected_layer.setReadOnly(True)
        selected_polyline_layout.addWidget(widget_selected_layer)        
        input_group_box_layout.addLayout(selected_polyline_layout)


        selected_polyline_layout = QHBoxLayout()
        selected_polyline_layout.addWidget(QLabel("<b>Selected Polyline:</b>"))
        selected_polyline = self.iface.activeLayer().selectedFeatures() if self.iface.activeLayer() else "None"
        widget_selected_poline = QLineEdit(str(len(selected_polyline)) )
        widget_selected_poline.setReadOnly(True)
        selected_polyline_layout.addWidget(widget_selected_poline)        
        input_group_box_layout.addLayout(selected_polyline_layout)

        input_group_layout.setLayout(input_group_box_layout)
        self.main_layout.addWidget(input_group_layout)

        # 3. VISTA PREVIA DEL QR GRANDE Y FIJA
        
        self.main_layout.addWidget(QLabel("<b>QR Code Live Preview:</b>"))
        self.lbl_qr_preview = QLabel()
        self.lbl_qr_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qr_preview.setStyleSheet("border:1px solid #cccccc; background-color:#ffffff; border-radius:4px;")
        self.lbl_qr_preview.setFixedSize(420, 420)
        self.main_layout.addWidget(self.lbl_qr_preview, alignment=Qt.AlignmentFlag.AlignCenter)

        # 4. PANEL COLAPSABLE PARA EL TEXTO DE LA URL
        self.btn_toggle_url = QPushButton("▶ Show Encoded URL Text")
        self.btn_toggle_url.setCheckable(True)
        self.btn_toggle_url.setChecked(False)
        self.btn_toggle_url.setStyleSheet("text-align:left; font-weight:bold; padding:4px;")
        self.btn_toggle_url.clicked.connect(self.toggle_url_panel)
        self.main_layout.addWidget(self.btn_toggle_url)

        self.url_panel = QFrame()
        url_layout = QVBoxLayout(self.url_panel)
        url_layout.setContentsMargins(0, 0, 0, 0)
        self.txt_debug = QTextEdit()
        self.txt_debug.setReadOnly(True)
        self.txt_debug.setFixedHeight(70)
        url_layout.addWidget(self.txt_debug)
        self.url_panel.setVisible(False)
        self.main_layout.addWidget(self.url_panel)

        # 5. BOTONES DE ACCIÓN INFERIORES
        btn_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Generate & Preview")
        self.btn_generate.clicked.connect(self.process_export)
        self.btn_save = QPushButton("Save PNG...")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_qr_image)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        btn_about = QPushButton("About")
        btn_about.clicked.connect(self.show_about)


        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(btn_about)
        btn_layout.addWidget(btn_close)
        self.main_layout.addLayout(btn_layout)

        self.setLayout(self.main_layout)



    def toggle_url_panel(self):
        is_visible = self.btn_toggle_url.isChecked()
        self.url_panel.setVisible(is_visible)
        self.btn_toggle_url.setText("▼ Hide Encoded URL Text" if is_visible else "▶ Show Encoded URL Text")
        self.adjustSize()



    def show_help_info(self):
        help_text = "<h3>Manual</h3><p>1. Select polyline layer.<br>2. Highlight a route feature.<br>3. Choose mode and click Generate.<br>4. Click Save PNG.</p>"
        QMessageBox.information(self, "Help", help_text)



    def show_about(self):
        about_text = "<h3>About QRouteCode</h3><p>Version 1.0<br>Author: JuanMa Romero Martin<br>Generates QR codes for Google Maps routes.</p>"
        QMessageBox.about(self, "About", about_text)


    def google_maps_url(self, stops: list, mode: str) -> str:
        params = {
            "api": "1",
            "origin": f"{stops[0]['lat']},{stops[0]['lon']}",
            "destination": f"{stops[-1]['lat']},{stops[-1]['lon']}",
            "travelmode": mode,
        }
        if len(stops) > 2:
            params["waypoints"] = "|".join(f"{stop['lat']},{stop['lon']}" for stop in stops[1:-1])
        return "https://www.google.com/maps/dir/?" + urlencode(params, safe="|,")



    def render_qr_to_pixmap(self, text_data, scale_size=10):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, border=2)
        qr.add_data(text_data)
        qr.make(fit=True)
        modules = qr.get_matrix()
        matrix_size = len(modules)
        img_size = matrix_size * scale_size
        qimage = QImage(img_size, img_size, QImage.Format.Format_RGB32)
        qimage.fill(QColor("white"))
        painter = QPainter(qimage)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1a365d"))
        for r, row in enumerate(modules):
            for c, cell in enumerate(row):
                if cell:
                    painter.drawRect(c * scale_size, r * scale_size, scale_size, scale_size)
        painter.end()
        return QPixmap.fromImage(qimage)
  


    def process_export(self):
        layer = self.iface.activeLayer()
        if not layer or len(layer.selectedFeatures()) == 0:
            QMessageBox.warning(self, "Selection Error", "Please select a polyline layer and feature.")
            return
        selected_features_list = layer.selectedFeatures()
        feature_item = selected_features_list[0]
        geom = feature_item.geometry()
        try:
            source_crs = layer.crs()
            dest_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            transform = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())
            geom.transform(transform)
            points = []
            vertex_iter = geom.vertices()
            while vertex_iter.hasNext():
                pt = vertex_iter.next()
                points.append(QgsPointXY(pt.x(), pt.y()))
            if len(points) < 2:
                QMessageBox.warning(self, "Geometry Error", "The line must contain at least 2 vertices.")
                return
            stops_list = [{"lat": f"{pt.y()}", "lon": f"{pt.x()}"} for pt in points]
            unique_stops = []
            for stop in stops_list:
                if not unique_stops or unique_stops[-1] != stop:
                    unique_stops.append(stop)
            if len(unique_stops) > 22:
                origin_stop = unique_stops[0]
                dest_stop = unique_stops[-1]
                mid_stops = unique_stops[1:-1]
                step = max(1, len(mid_stops) // 20)
                sampled_mid = mid_stops[::step][:20]
                final_stops = [origin_stop] + sampled_mid + [dest_stop]
            else:
                final_stops = unique_stops
            mode = self.combo_mode.currentData()
            self.generated_url = self.google_maps_url(final_stops, mode)
            self.txt_debug.setText(self.generated_url)
            pixmap = self.render_qr_to_pixmap(self.generated_url, scale_size=12)
            self.lbl_qr_preview.setPixmap(pixmap.scaled(400, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.btn_save.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Execution failed at runtime: {str(e)}")



    def save_qr_image(self):
        if not self.generated_url:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Save QR Code", os.path.expanduser("~"), "PNG Image (*.png)")
        if filename:
            try:
                pixmap = self.render_qr_to_pixmap(self.generated_url, scale_size=15)
                pixmap.save(filename, "PNG")
                QMessageBox.information(self, "Success", "QR Image saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))
