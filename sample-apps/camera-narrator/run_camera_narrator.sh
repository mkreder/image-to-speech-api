#!/bin/bash

# Camera Narrator Launcher Script

echo "🎥 Camera Narrator Launcher"
echo "=========================="

# Check if API endpoint is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: API endpoint required"
    echo ""
    echo "Usage: $0 YOUR_API_ENDPOINT [OPTIONS]"
    echo ""
    echo "Example:"
    echo "  $0 https://abc123.execute-api.us-east-1.amazonaws.com/Prod"
    echo ""
    echo "With options:"
    echo "  $0 https://abc123.execute-api.us-east-1.amazonaws.com/Prod --interval 10 --voice Matthew"
    echo ""
    echo "To get your API endpoint, run:"
    echo "  cd ../../ && sam list stack-outputs --stack-name image-description-api"
    exit 1
fi

API_ENDPOINT=$1
shift  # Remove first argument, keep the rest as options

echo "🚀 Starting Camera Narrator..."
echo "Press 'q' in the camera window to quit"
echo "Press 'c' to capture immediately"
echo ""
python3 camera_narrator.py "$API_ENDPOINT" "$@"
