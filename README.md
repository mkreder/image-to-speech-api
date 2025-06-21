# Multi-Language Image Description API

A serverless API built with AWS SAM that provides AI-powered image descriptions in 20+ languages with both text and audio output options.

## 🚀 Features

### 🌍 **Multi-Language Support**
- **20+ Languages**: English, Spanish, Japanese, French, German, Italian, Portuguese, Russian, Korean, Chinese, Arabic, Hindi, Turkish, Polish, Dutch, Swedish, Danish, Norwegian, Finnish, Icelandic
- **ISO 639-1 Codes**: Standard two-letter language codes (`en`, `es`, `ja`, etc.)
- **Case Insensitive**: `EN`, `en`, `Es` all work
- **Smart Defaults**: Auto-selects appropriate voices for each language

### 🎵 **Audio Descriptions**
- **Amazon Polly Integration**: Natural-sounding speech synthesis
- **50+ Voices**: Multiple voice options per language
- **Neural Engine**: High-quality voice synthesis
- **MP3 Output**: Base64-encoded audio data

### 🖼️ **Image Processing**
- **Multiple Formats**: JPEG, PNG, GIF, WebP
- **Auto-Resizing**: Cost optimization while maintaining quality
- **Format Detection**: Automatic image format recognition
- **Base64 Input**: Easy integration with web applications

## 🏗️ Architecture

- **API Gateway**: RESTful API with two specialized endpoints
- **Lambda**: Serverless compute (1024MB, 60s timeout)
- **Amazon Bedrock**: AI model for image analysis
- **Amazon Polly**: Text-to-speech synthesis
- **CloudWatch**: Comprehensive logging and monitoring

## 📋 API Endpoints

### 1. Text Descriptions
**POST** `/describe/text`

Get detailed text descriptions in any supported language.

#### Request
```json
{
  "image": "base64_encoded_image_data",
  "language": "es"  // Optional, defaults to "en"
}
```

#### Response
```json
{
  "description": "Una hermosa puesta de sol sobre un paisaje montañoso...",
  "format": "text",
  "language": "es"
}
```

### 2. Audio Descriptions
**POST** `/describe/audio`

Get descriptions as natural-sounding audio in any supported language.

#### Request
```json
{
  "image": "base64_encoded_image_data",
  "language": "ja",     // Optional, defaults to "en"
  "voice": "Mizuki"     // Optional, auto-selected based on language
}
```

#### Response
```json
{
  "description": "この画像には美しい夕日が山の風景に映っています...",
  "audio": "base64_encoded_mp3_data",
  "format": "audio",
  "voice": "Mizuki",
  "language": "ja"
}
```

## 🌐 Supported Languages & Voices

| Language | Code | Default Voice | Additional Voices |
|----------|------|---------------|-------------------|
| English | `en` | Joanna | Matthew, Amy, Brian, Emma, Olivia |
| Spanish | `es` | Lucia | Conchita, Enrique, Miguel |
| Japanese | `ja` | Mizuki | Takumi |
| French | `fr` | Celine | Lea, Mathieu |
| German | `de` | Marlene | Vicki, Hans |
| Italian | `it` | Carla | Bianca, Giorgio |
| Portuguese | `pt` | Camila | Vitoria, Ricardo |
| Russian | `ru` | Tatyana | Maxim |
| Korean | `ko` | Seoyeon | - |
| Chinese | `zh` | Zhiyu | - |
| *+10 more languages* | | | |

## 🚀 Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- SAM CLI installed
- Python 3.9+

### Quick Deploy
```bash
# Build the application
sam build

# Deploy to AWS
sam deploy --stack-name image-description-api \
           --capabilities CAPABILITY_IAM \
           --region us-east-1 \
           --resolve-s3
```

### Guided Deployment (First Time)
```bash
sam deploy --guided
```

## 🧪 Local Development

### Start API Locally
```bash
sam local start-api
```

### Test Individual Function
```bash
sam local invoke ImageDescriptionFunction --event events/event.json
```

### Test with Sample Data
```bash
# Test text endpoint
curl -X POST http://localhost:3000/describe/text \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_image_data", "language": "es"}'

# Test audio endpoint  
curl -X POST http://localhost:3000/describe/audio \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_image_data", "language": "ja", "voice": "Mizuki"}'
```

## 🔧 Configuration

### Environment Variables
- `AWS_REGION`: AWS region for deployment
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

### AWS Services Used
- **Amazon Bedrock**: AI model for image analysis
- **Amazon Polly**: Text-to-speech synthesis
- **CloudWatch Logs**: Application logging
- **API Gateway**: REST API management
- **Lambda**: Serverless compute

### Required IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow", 
      "Action": [
        "polly:SynthesizeSpeech"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream", 
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## 📊 Performance

- **Response Times**: 1.5-4 seconds depending on language complexity
- **Concurrent Requests**: Auto-scaling Lambda functions
- **Image Size Limit**: 10MB (auto-resized for optimization)
- **Timeout**: 60 seconds for audio processing, 30 seconds for text

## 🔍 Error Handling

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid image, language, or voice)
- `404`: Endpoint not found
- `405`: Method not allowed
- `500`: Internal server error

### Common Error Messages
```json
// Invalid language
{
  "error": "Invalid language code: xyz. Use ISO 639-1 two-letter codes (e.g., en, es, ja)"
}

// Missing image
{
  "error": "No image provided in the request"
}

// Voice not available for language
{
  "error": "Voice Matthew is not available for language ja"
}
```

## 🧪 Testing

### Run Test Suite
```bash
# Install test dependencies
pip install pytest requests

# Run comprehensive tests
python test_language_api.py
```

### Manual Testing
```bash
# Test multiple languages
curl -X POST https://your-api-url/describe/text \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_data", "language": "es"}'
```

## 📈 Monitoring

### CloudWatch Metrics
- Function duration
- Error rates
- Concurrent executions
- Memory utilization

### Custom Logs
- Request/response logging
- Language detection
- Voice selection
- Error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License 

## 🆘 Support

- **Issues**: Create GitHub issues for bugs
- **Features**: Submit feature requests via GitHub
