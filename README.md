# QRouteCode 🗺️

[![QGIS Version](https://shields.io)](https://qgis.org)
[![License](https://shields.io)](LICENSE)
[![Publisher](https://shields.io)](https://ihm.solutions)

**QRouteCode** is a professional QGIS 4 plugin developed by **iHM Solutions** that instantly converts vector lines and polylines into optimized, high-contrast QR codes embedded with safe Google Maps Routing data. 

Scanning the generated QR code directly triggers the native Google Maps app on iOS or Android, generating a walking, driving, or bicycling itinerary traced directly from your spatial GIS data features.

---

## Key Features

* **True Vertex Extraction:** Bypasses dense line geometries to capture only the exact structural vertices/nodes plotted on your canvas.
* **Precise URL Encoding:** Uses strict cross-platform query string mapping to prevent coordinate string truncation or broken routes on mobile devices.
* **Smart Downsampling:** Automatically handles lines with complex vertex loops, clipping routes down gracefully to match Google Maps API threshold limits (maximum of 22 waypoints).
* **Native Painter Engine:** Rendered completely via `QPainter` and `QPixmap` vectors to remove bulky external library packages, avoiding cross-platform operating system crashes entirely.
* **Clean User Interface:** Features interactive inputs displaying layer data, active selection diagnostics, and a responsive collapsible code debug panel.

---

## How It Works (The Engine)

Unlike standard web browser slashes, mobile device systems require a strictly structured parameter schema to parse multi-point paths. The plugin takes your active vector geometry, transforms the spatial nodes to **WGS 84 (EPSG:4326)**, and maps them into an URL-safe query matrix:

```python
params = {
    "api": "1",
    "origin": f"{stops[0]['lat']},{stops[0]['lon']}",
    "destination": f"{stops[-1]['lat']},{stops[-1]['lon']}",
    "travelmode": mode,
}
if len(stops) > 2:
    params["waypoints"] = "|".join(f"{stop['lat']},{stop['lon']}" for stop in stops[1:-1])

url = "https://google.com?" + urlencode(params, safe="|,")
```

---

## Installation & Setup

### Method 1: Via QGIS Plugin Manager (Recommended)
Once published globally, you can install the plugin natively without leaving the application environment:
1. Open QGIS and navigate to the top menu: **Plugins** ➔ **Manage and Install Plugins...**
2. In the sidebar, select the **All** tab.
3. Type `QRouteCode` into the top search bar field.
4. Click on the plugin from the filtered results list and select **Install Plugin**.

### Method 2: Via Local ZIP Archive Deployment
If you downloaded the packaged production archive bundle directly:
1. Open QGIS and open the extension manager (**Plugins** ➔ **Manage and Install Plugins...**).
2. Select the **Install from ZIP** tab on the left sidebar menu.
3. Click the **Browse (...)** button and select your local **`QRouteCode.zip`** file archive.
4. Click **Install Plugin** to execute background extraction automatically.

### Method 3: Manual Folder Installation (Developers Only)
1. Download or clone this repository and compress the root contents as a `.zip` archive.
2. Extract the folder directory cleanly into your local QGIS 4 user profiles location:
   * **macOS:** `/Users/<username>/Library/Application Support/QGIS/QGIS4/profiles/default/python/plugins/`
   * **Windows:** `%APPDATA%\QGIS\QGIS4\profiles\default\python\plugins\`
3. Ensure your extracted directory folder name matches exactly: `qgisQRCodeItinerary`

---

## Step-by-Step Usage

1. Open a QGIS project and highlight your target **Polyline layer** inside the Layer List panel.
2. Select the native QGIS **Select Feature Tool** from the main top application dashboard bar.
3. Click on the specific line path feature map item you wish to translate.
4. Launch **QRouteCode** from your toolbar extension shortcut or via the *Plugins* drop-down menu layer.
5. Pick your travel method (**Walking**, **Driving**, or **Bicycling**).
6. Click **Generate & Preview** to generate your itinerary address.
7. Click the **Show Encoded URL Text** dropdown bar to inspect the raw query parameters output.
8. Click **Save PNG...** to write your high-resolution dark blue QR code out to your computer desktop!

---

## License

This plugin is open-source software licensed under the **GNU General Public License v3 (GPLv3)**—in full alignment with official QGIS Repository core publishing standards.

---

## Corporate Support & Maintenance

Developed, maintained, and supported by **iHM Solutions**. 

* **Official Website:** [ihm.solutions](https://ihm.solutions)
* **Technical Contact:** [dev@ihm.solutions](mailto:dev@ihm.solutions)
* **Bug Tracker:** Please open all incident tickets, tracebacks, and feature requests directly inside our [GitHub Issues Board](https://github.com).
