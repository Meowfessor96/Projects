#!/bin/bash

cd /home/thequietkid106/Desktop/Projects || {
    echo "Directory not found!"
    exit 1
}

# Add all changes
git add .

# Commit with timestamp
git commit -m "Auto update: $(date '+%Y-%m-%d %H:%M:%S')"

# Push to origin
git push origin main
