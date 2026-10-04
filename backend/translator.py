# translator.py
# Kaam: Multi-bhasha support — CACHED translation

from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
import streamlit as st
import time

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


@st.cache_data(ttl=3600)
def detect_lang(text):
    try:
        return detect(text[:500])
    except Exception:
        return "en"


def get_lang_name(code):
    return LANG_NAMES.get(code, code.upper())


@st.cache_data(ttl=3600)
def _translate_cached(text, target_lang):
    # Cached translation — same text dobara translate nahi hoga
    try:
        result = GoogleTranslator(source="auto", target=target_lang).translate(text)
        return result if result else text
    except Exception as e:
        if "TooManyRequests" in str(e):
            time.sleep(2)
            try:
                result = GoogleTranslator(source="auto", target=target_lang).translate(text)
                return result if result else text
            except Exception:
                return text
        return text


def translate(text, target_lang):
    # Text ko target language mein translate karta hai (CACHED)
    if not text or not target_lang:
        return text

    # Agar already same language hai to translate mat karo
    try:
        current = detect(text[:500])
        if current == target_lang:
            return text
    except Exception:
        pass

    # Chhote chunks mein todo (Google Translate limit)
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        translated = [_translate_cached(p, target_lang) for p in parts]
        return " ".join(translated)
    else:
        return _translate_cached(text, target_lang)