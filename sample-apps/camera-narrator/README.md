# Camera Narrator

A Python application that continuously captures images from a USB camera, sends them to your deployed Image Description API, and plays back audio descriptions in real-time.

## Features

- 📷 **Live Camera Feed**: Continuous capture from USB camera
- 🎤 **Audio Descriptions**: Real-time AI-powered image descriptions with speech
- 🌍 **Multi-language Support**: Descriptions in 20+ languages
- 🔊 **Multiple Voices**: Choose from various Amazon Polly voices
- ⚡ **Configurable Intervals**: Set custom capture intervals
- 🖥️ **Visual Feedback**: Live preview with description overlay

## Prerequisites

- Python 3.7 or higher
- USB camera connected to your computer
- Deployed Image Description API (from the backend folder)

## Getting Started

### Get Your API Endpoints

First, get your deployed API endpoint:
```bash
cd ../../
sam list stack-outputs --stack-name image-description-api
```

Your endpoints will look like:
- **Base API**: `https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod`
- **Text Descriptions**: `https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod/describe/text`
- **Audio Descriptions**: `https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod/describe/audio`

### Quick Start

1. **Install dependencies**:
   ```bash
   python3 setup.py
   ```

2. **Run the camera narrator**:
   ```bash
   ./run_camera_narrator.sh https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod
   ```

## Usage

### Basic Usage
```bash
python camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod
```

### Advanced Options
```bash
python camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod \
  --interval 10 \
  --voice Matthew \
  --language es \
  --camera 1
```

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `api_endpoint` | - | Your API Gateway endpoint URL | Required |
| `--interval` | `-i` | Seconds between captures | 5 |
| `--voice` | `-v` | Amazon Polly voice | Joanna |
| `--language` | `-l` | Language code (ISO 639-1) | en |
| `--camera` | `-c` | Camera index | 0 |

### Alternative Ways to Run

#### Direct Python execution:
```bash
python3 camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod
```

#### With custom options:
```bash
python3 camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod \
  --interval 10 \
  --voice Matthew \
  --language en
```

#### Spanish narration:
```bash
python3 camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod \
  --voice Enrique \
  --language es \
  --interval 8
```

## Controls

While the application is running:
- **'q'** - Quit the application
- **'c'** - Capture and describe immediately
- **ESC** - Close camera window

## Supported Languages

Use ISO 639-1 two-letter codes:
- `en` - English
- `es` - Spanish  
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese
- And many more...

## Supported Voices

Popular Amazon Polly voices:
- **English**: Joanna, Matthew, Amy, Brian, Emma, Olivia
- **Spanish**: Lucia, Conchita, Enrique, Miguel, Penelope
- **French**: Celine, Lea, Mathieu
- **German**: Marlene, Vicki, Hans
- **Italian**: Carla, Bianca, Giorgio
- And many more...

## Examples

### Basic English narration every 5 seconds:
```bash
python camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod
```

### Spanish with male voice every 10 seconds  
```bash
python camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod \
  --interval 10 --voice Enrique --language es
```

### French with female voice every 7 seconds
```bash
python camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod \
  --interval 7 --voice Celine --language fr
```

### German narration
```bash
python camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod \
  --voice Marlene --language de
```

### Japanese narration
```bash
python camera_narrator.py https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/Prod \
  --voice Mizuki --language ja
```

## What It Does

1. **Captures images** from your USB camera every few seconds
2. **Sends images** to your deployed API for AI analysis
3. **Receives descriptions** in your chosen language
4. **Plays audio** descriptions using Amazon Polly voices
5. **Shows live preview** with description overlay

Perfect for accessibility, security monitoring, or just having fun with AI! 🎥🤖

## Troubleshooting

### Camera Issues
- **No camera detected**: Try different camera indices (0, 1, 2...)
- **Permission denied**: Grant camera access in system settings
- **Poor quality**: Ensure good lighting and camera positioning

### API Issues
- **Connection errors**: Check your internet connection and API endpoint
- **Authentication errors**: Ensure your API is publicly accessible
- **Timeout errors**: Increase timeout or check API performance

### Audio Issues
- **No sound**: Check system volume and audio output device
- **Audio lag**: This is normal due to API processing time
- **Distorted audio**: Check pygame installation

### Performance Tips
- Use shorter capture intervals for more responsive narration
- Ensure good lighting for better image recognition
- Position camera to capture clear, unobstructed views
- Close other applications to free up system resources

## Dependencies

- **opencv-python**: Camera capture and image processing
- **requests**: HTTP API communication
- **pygame**: Audio playback
- **Pillow**: Image format conversion

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Camera    │───▶│   Python     │───▶│    API      │
│   Capture   │    │ Application  │    │  Gateway    │
└─────────────┘    └──────────────┘    └─────────────┘
                           │                    │
                           ▼                    ▼
                   ┌──────────────┐    ┌─────────────┐
                   │    Audio     │    │   Lambda    │
                   │   Playback   │    │  Function   │
                   └──────────────┘    └─────────────┘
                                              │
                                              ▼
                                      ┌─────────────┐
                                      │   Bedrock   │
                                      │   & Polly   │
                                      └─────────────┘
```

## License

This project is part of the Image Description API open source project.

## Contributing

Feel free to submit issues and enhancement requests!
