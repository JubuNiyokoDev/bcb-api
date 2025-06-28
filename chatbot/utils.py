from langdetect import detect


def detect_language(text):
    try:
        lang = detect(text)
        if lang in ["fr", "en", "rn"]:
            return lang
        return "fr"  # fallback
    except:
        return "fr"
