#!/bin/bash

# Upload sample images script
API_URL="http://localhost:8000/api/v1/images/upload"

echo "Uploading sample images for pagination testing..."

# Find PNG files and upload them
IMAGE_FILES=(
    "/System/Library/CoreServices/Dock.app/Contents/Resources/shadow-light-4px.png"
    "/System/Library/CoreServices/Dock.app/Contents/Resources/url@2x.png"
    "/System/Library/CoreServices/Dock.app/Contents/Resources/ecsb_arrow_bottom.png"
    "/System/Library/CoreServices/Dock.app/Contents/Resources/shadow-large-cartouche-dark.png"
    "/System/Library/CoreServices/Dock.app/Contents/Resources/SpacesBarClosePressed.png"
)

# Find additional PNG files
while IFS= read -r -d '' file; do
    IMAGE_FILES+=("$file")
done < <(find /System/Library/CoreServices -name "*.png" -type f -print0 | head -z -20)

counter=0
for image in "${IMAGE_FILES[@]}"; do
    if [[ -f "$image" && $counter -lt 15 ]]; then
        echo "Uploading image $((counter+1)): $(basename "$image")"
        curl -s -X POST "$API_URL" -F "file=@$image" -H "Content-Type: multipart/form-data" | head -1
        echo
        ((counter++))
        sleep 0.5  # Small delay to avoid overwhelming the server
    fi
done

echo "Uploaded $counter images total"