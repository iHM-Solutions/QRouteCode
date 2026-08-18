#!/bin/bash

# 1. Capture the absolute path of this active project folder
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$(dirname "$PROJECT_DIR")"
FOLDER_NAME="$(basename "$PROJECT_DIR")"
ZIP_NAME="${FOLDER_NAME}_v1.0.0.zip"

echo "========================================="
echo "📦 QRouteCode Deployment Packager"
echo "========================================="
echo "Project Path: $PROJECT_DIR"
echo "Folder Identity: $FOLDER_NAME"

# 2. Step outside to the parent directory so the root folder is captured in the archive structure
cd "$PARENT_DIR" || exit

# 3. Clean up any stale legacy ZIP build profiles from the directory workspace
if [ -f "$PROJECT_DIR/$ZIP_NAME" ]; then
    rm "$PROJECT_DIR/$ZIP_NAME"
fi

echo "🧬 Compiling binary deployment state..."

# 4. Execute deep cleanup compression mapping across structural layers
zip -r "$PROJECT_DIR/releases/$ZIP_NAME" "$FOLDER_NAME" \
    -x "*.DS_Store" \
    -x "__MACOSX*" \
    -x ".gitignore" \
    -x "*/.git*" \
    -x "*/__pycache__*" \
    -x "*/test*" \
    -x "*/releases*" \
    -x "$FOLDER_NAME/*.sh" \
    -x "$FOLDER_NAME/*.OLD"

echo "========================================="
echo "✅ SUCCESS: Build package compiled safely!"
echo "File location: $PROJECT_DIR/$ZIP_NAME"
echo "========================================="
