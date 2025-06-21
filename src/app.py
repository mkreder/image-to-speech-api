import json
import base64
import boto3
import io
from PIL import Image

def lambda_handler(event, context):
    """
    Lambda function that handles image description requests.
    Routes to different handlers based on the HTTP path:
    - POST /describe/text - Returns text description
    - POST /describe/audio - Returns audio description
    """
    try:
        # Get the HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        # Route based on path
        if http_method == 'POST':
            if path.endswith('/describe/text'):
                return handle_text_description(event, context)
            elif path.endswith('/describe/audio'):
                return handle_audio_description(event, context)
            else:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Endpoint not found'})
                }
        elif http_method == 'OPTIONS':
            # Handle CORS preflight requests
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': ''
            }
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def handle_text_description(event, context):
    """
    Handle text description requests
    """
    try:
        # Parse the request body
        request_body = json.loads(event.get('body', '{}'))
        
        # Get the base64 encoded image
        if 'image' not in request_body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No image provided in the request'})
            }
        
        image_data = request_body['image']
        language = request_body.get('language', 'en').lower()  # Default to English
        
        # Validate language code (ISO 639-1)
        if not validate_language_code(language):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Invalid language code: {language}. Use ISO 639-1 two-letter codes (e.g., en, es, ja)'})
            }
        
        # Check if the image is base64 encoded
        if ',' in image_data:
            # Handle data URLs (e.g., "data:image/jpeg;base64,/9j/4AAQ...")
            image_data = image_data.split(',')[1]
        
        # Decode the base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Resize the image to optimize for inference costs while maintaining quality
        resized_image_bytes = resize_image(image_bytes)
        
        # Call Bedrock to describe the image in the specified language
        description = describe_image_with_bedrock(resized_image_bytes, language)
        
        # Return the description
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'description': description,
                'format': 'text',
                'language': language
            })
        }
    
    except Exception as e:
        print(f"Error in handle_text_description: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def handle_audio_description(event, context):
    """
    Handle audio description requests
    """
    try:
        # Parse the request body
        request_body = json.loads(event.get('body', '{}'))
        
        # Get the base64 encoded image
        if 'image' not in request_body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No image provided in the request'})
            }
        
        image_data = request_body['image']
        voice_id = request_body.get('voice', 'Joanna')  # Default voice
        language = request_body.get('language', 'en').lower()  # Default to English
        
        # Validate language code (ISO 639-1)
        if not validate_language_code(language):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Invalid language code: {language}. Use ISO 639-1 two-letter codes (e.g., en, es, ja)'})
            }
        
        # Get appropriate voice for language if default voice is used
        if voice_id == 'Joanna' and language != 'en':
            voice_id = get_default_voice_for_language(language)
        
        # Validate voice for language
        if not validate_voice_for_language(voice_id, language):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Voice {voice_id} is not available for language {language}'})
            }
        
        # Check if the image is base64 encoded
        if ',' in image_data:
            # Handle data URLs (e.g., "data:image/jpeg;base64,/9j/4AAQ...")
            image_data = image_data.split(',')[1]
        
        # Decode the base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Resize the image to optimize for inference costs while maintaining quality
        resized_image_bytes = resize_image(image_bytes)
        
        # Call Bedrock to describe the image in the specified language
        description = describe_image_with_bedrock(resized_image_bytes, language)
        
        # Convert text to speech using Amazon Polly
        audio_base64 = text_to_speech(description, voice_id, language)
        
        # Return the audio description
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'description': description,
                'audio': audio_base64,
                'format': 'audio',
                'voice': voice_id,
                'language': language
            })
        }
    
    except Exception as e:
        print(f"Error in handle_audio_description: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def resize_image(image_bytes, max_size=800):
    """
    Resize the image to reduce inference costs while maintaining quality
    """
    try:
        # Open the image using PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Calculate new dimensions while maintaining aspect ratio
        width, height = image.size
        if width > height:
            if width > max_size:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_width = width
                new_height = height
        else:
            if height > max_size:
                new_height = max_size
                new_width = int(width * (max_size / height))
            else:
                new_width = width
                new_height = height
        
        # Only resize if necessary
        if new_width != width or new_height != height:
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        else:
            resized_image = image
        
        # Convert back to bytes
        buffer = io.BytesIO()
        resized_image.save(buffer, format=image.format if image.format else 'JPEG')
        return buffer.getvalue()
    
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        # Return original image if resizing fails
        return image_bytes

def describe_image_with_bedrock(image_bytes, language='en'):
    """
    Call Bedrock's AI model to describe the image in the specified language
    """
    bedrock_runtime = boto3.client('bedrock-runtime')
    
    # Detect image format
    image_format = "jpeg"  # default
    if image_bytes.startswith(b'\x89PNG'):
        image_format = "png"
    elif image_bytes.startswith(b'\xff\xd8\xff'):
        image_format = "jpeg"
    elif image_bytes.startswith(b'GIF'):
        image_format = "gif"
    elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
        image_format = "webp"
    
    # Create language-specific prompt
    prompt = get_language_prompt(language)
    
    # Prepare the request payload for the AI model
    request_payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": image_format,
                            "source": {
                                "bytes": base64.b64encode(image_bytes).decode('utf-8')
                            }
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 300
        }
    }
    
    # Call Bedrock with the AI model
    response = bedrock_runtime.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=json.dumps(request_payload)
    )
    
    # Parse the response
    response_body = json.loads(response['body'].read().decode('utf-8'))
    
    # Extract the description from the response
    description = response_body['output']['message']['content'][0]['text']
    
    return description

def text_to_speech(text, voice_id='Joanna', language='en'):
    """
    Convert text to speech using Amazon Polly with language support
    """
    try:
        polly_client = boto3.client('polly')
        
        # Get language code for Polly (some need specific format)
        polly_language_code = get_polly_language_code(language)
        
        # Call Amazon Polly to synthesize speech
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine='neural',  # Use neural engine for better quality
            LanguageCode=polly_language_code
        )
        
        # Read the audio stream
        audio_stream = response['AudioStream'].read()
        
        # Convert to base64 for JSON response
        audio_base64 = base64.b64encode(audio_stream).decode('utf-8')
        
        return audio_base64
    
    except Exception as e:
        print(f"Error in text_to_speech: {str(e)}")
        # Fallback to standard engine if neural fails
        try:
            response = polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine='standard',
                LanguageCode=polly_language_code
            )
            
            audio_stream = response['AudioStream'].read()
            audio_base64 = base64.b64encode(audio_stream).decode('utf-8')
            
            return audio_base64
        except Exception as fallback_error:
            print(f"Fallback error in text_to_speech: {str(fallback_error)}")
def validate_language_code(language):
    """
    Validate ISO 639-1 language code
    """
    supported_languages = {
        'en', 'es', 'ja', 'fr', 'de', 'it', 'pt', 'ru', 'ko', 'zh', 
        'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'is'
    }
    return language.lower() in supported_languages

def get_language_prompt(language):
    """
    Get language-specific prompt for image description
    """
    prompts = {
        'en': "Please describe what you see in this image in detail.",
        'es': "Por favor describe lo que ves en esta imagen en detalle.",
        'ja': "この画像に写っているものを詳しく説明してください。",
        'fr': "Veuillez décrire ce que vous voyez dans cette image en détail.",
        'de': "Bitte beschreiben Sie detailliert, was Sie in diesem Bild sehen.",
        'it': "Per favore descrivi in dettaglio quello che vedi in questa immagine.",
        'pt': "Por favor, descreva o que você vê nesta imagem em detalhes.",
        'ru': "Пожалуйста, подробно опишите то, что вы видите на этом изображении.",
        'ko': "이 이미지에서 보이는 것을 자세히 설명해 주세요.",
        'zh': "请详细描述您在这张图片中看到的内容。",
        'ar': "يرجى وصف ما تراه في هذه الصورة بالتفصيل.",
        'hi': "कृपया इस छवि में आप जो देख रहे हैं उसका विस्तार से वर्णन करें।",
        'tr': "Lütfen bu resimde gördüklerinizi ayrıntılı olarak açıklayın.",
        'pl': "Proszę szczegółowo opisać to, co widzisz na tym obrazie.",
        'nl': "Beschrijf alstublieft in detail wat u in deze afbeelding ziet.",
        'sv': "Vänligen beskriv i detalj vad du ser i denna bild.",
        'da': "Beskriv venligst i detaljer, hvad du ser i dette billede.",
        'no': "Vennligst beskriv i detalj hva du ser i dette bildet.",
        'fi': "Kuvaile yksityiskohtaisesti, mitä näet tässä kuvassa.",
        'is': "Vinsamlegast lýstu því sem þú sérð á þessari mynd í smáatriðum."
    }
    return prompts.get(language.lower(), prompts['en'])

def get_polly_language_code(language):
    """
    Convert ISO 639-1 to Polly language codes
    """
    polly_codes = {
        'en': 'en-US',
        'es': 'es-ES',
        'ja': 'ja-JP',
        'fr': 'fr-FR',
        'de': 'de-DE',
        'it': 'it-IT',
        'pt': 'pt-BR',
        'ru': 'ru-RU',
        'ko': 'ko-KR',
        'zh': 'cmn-CN',
        'ar': 'ar-AE',
        'hi': 'hi-IN',
        'tr': 'tr-TR',
        'pl': 'pl-PL',
        'nl': 'nl-NL',
        'sv': 'sv-SE',
        'da': 'da-DK',
        'no': 'nb-NO',
        'fi': 'fi-FI',
        'is': 'is-IS'
    }
    return polly_codes.get(language.lower(), 'en-US')

def get_default_voice_for_language(language):
    """
    Get default voice for each language
    """
    default_voices = {
        'en': 'Joanna',
        'es': 'Lucia',
        'ja': 'Mizuki',
        'fr': 'Celine',
        'de': 'Marlene',
        'it': 'Carla',
        'pt': 'Camila',
        'ru': 'Tatyana',
        'ko': 'Seoyeon',
        'zh': 'Zhiyu',
        'ar': 'Zeina',
        'hi': 'Aditi',
        'tr': 'Filiz',
        'pl': 'Ewa',
        'nl': 'Lotte',
        'sv': 'Astrid',
        'da': 'Naja',
        'no': 'Liv',
        'fi': 'Suvi',
        'is': 'Dora'
    }
    return default_voices.get(language.lower(), 'Joanna')

def validate_voice_for_language(voice_id, language):
    """
    Validate if voice is available for the specified language
    """
    language_voices = {
        'en': ['Joanna', 'Matthew', 'Ivy', 'Kendra', 'Kimberly', 'Salli', 'Joey', 'Justin', 'Kevin', 'Ruth', 'Amy', 'Brian', 'Emma', 'Olivia', 'Aria'],
        'es': ['Lucia', 'Conchita', 'Enrique', 'Miguel', 'Penelope', 'Lupe', 'Mia'],
        'ja': ['Mizuki', 'Takumi'],
        'fr': ['Celine', 'Lea', 'Mathieu'],
        'de': ['Marlene', 'Vicki', 'Hans'],
        'it': ['Carla', 'Bianca', 'Giorgio'],
        'pt': ['Camila', 'Vitoria', 'Ricardo'],
        'ru': ['Tatyana', 'Maxim'],
        'ko': ['Seoyeon'],
        'zh': ['Zhiyu'],
        'ar': ['Zeina'],
        'hi': ['Aditi', 'Raveena'],
        'tr': ['Filiz'],
        'pl': ['Ewa', 'Maja', 'Jacek', 'Jan'],
        'nl': ['Lotte', 'Ruben'],
        'sv': ['Astrid'],
        'da': ['Naja', 'Mads'],
        'no': ['Liv'],
        'fi': ['Suvi'],
        'is': ['Dora', 'Karl']
    }
    
    available_voices = language_voices.get(language.lower(), [])
    return voice_id in available_voices