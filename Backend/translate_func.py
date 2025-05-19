from deep_translator import GoogleTranslator

def translate_to_english(text: str) -> str:
    return GoogleTranslator(source='id', target='en').translate(text)

def translate_to_indonesian(text: str) -> str:
    return GoogleTranslator(source='en', target='id').translate(text)
