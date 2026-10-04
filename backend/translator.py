# translator.py
# for: Multi-bhasha support — translate + language detect

from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0


LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "bn": "Bengali",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu"
}


def detect_lang(text):
    # Language detect karta hai
    try:
        return detect(text[:500])
    except Exception:
        return "en"


def get_lang_name(code):
    # Language code se naam deta hai
    return LANG_NAMES.get(code, code.upper())


def translate(text, target_lang):
    # Text ko target language mein translate karta hai
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        return text


# Test karne ke liye
if __name__ == "__main__":
    text = "Employee joined in January 2024"
    hindi = translate(text, "hi")
    print(f"English: {text}")
    print(f"Hindi: {hindi}")
    print(f"Detected: {detect_lang(hindi)}")