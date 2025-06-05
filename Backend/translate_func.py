from deep_translator import GoogleTranslator
from langdetect import detect

def detect_language(text: str) -> str:
    """Detect language of input text"""
    try:
        return detect(text)
    except:
        return 'en'  

def translate_to_english(text: str, source_lang: str = None) -> str:
    """Translate text to English"""
    if not source_lang:
        source_lang = detect_language(text)
    
    if source_lang == 'en':
        return text
    
    try:
        return GoogleTranslator(source=source_lang, target='en').translate(text)
    except:
        # Fallback: try auto-detect
        return GoogleTranslator(source='auto', target='en').translate(text)

def translate_from_english(text: str, target_lang: str) -> str:
    """Translate from English to target language"""
    if target_lang == 'en':
        return text
    
    try:
        return GoogleTranslator(source='en', target=target_lang).translate(text)
    except:
        return text  
