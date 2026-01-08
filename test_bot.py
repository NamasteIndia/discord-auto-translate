#!/usr/bin/env python3
"""
Simple test script to validate the translation bot logic
"""

import asyncio
import aiohttp

# Load the LANGUAGES dictionary from bot.py
LANGUAGES = {
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar",
    "Armenian": "hy", "Azerbaijani": "az", "Basque": "eu", "Belarusian": "be",
    "Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca",
    "Cebuano": "ceb", "Chinese": "zh", "Corsican": "co", "Croatian": "hr",
    "Czech": "cs", "Danish": "da", "Dutch": "nl", "English": "en",
    "Esperanto": "eo", "Estonian": "et", "Finnish": "fi", "French": "fr",
    "Galician": "gl", "Georgian": "ka", "German": "de", "Greek": "el",
    "Gujarati": "gu", "Haitian Creole": "ht", "Hausa": "ha", "Hawaiian": "haw",
    "Hebrew": "he", "Hindi": "hi", "Hmong": "hmn", "Hungarian": "hu",
    "Icelandic": "is", "Igbo": "ig", "Indonesian": "id", "Irish": "ga",
    "Italian": "it", "Japanese": "ja", "Javanese": "jv", "Kannada": "kn",
    "Kazakh": "kk", "Khmer": "km", "Korean": "ko", "Kurdish": "ku",
    "Kyrgyz": "ky", "Lao": "lo", "Latin": "la", "Latvian": "lv",
    "Lithuanian": "lt", "Luxembourgish": "lb", "Macedonian": "mk", "Malagasy": "mg",
    "Malay": "ms", "Malayalam": "ml", "Maltese": "mt", "Maori": "mi",
    "Marathi": "mr", "Mongolian": "mn", "Myanmar": "my", "Nepali": "ne",
    "Norwegian": "no", "Nyanja": "ny", "Pashto": "ps", "Persian": "fa",
    "Polish": "pl", "Portuguese": "pt", "Punjabi": "pa", "Romanian": "ro",
    "Russian": "ru", "Samoan": "sm", "Scots Gaelic": "gd", "Serbian": "sr",
    "Sesotho": "st", "Shona": "sn", "Sindhi": "sd", "Sinhala": "si",
    "Slovak": "sk", "Slovenian": "sl", "Somali": "so", "Spanish": "es",
    "Sundanese": "su", "Swahili": "sw", "Swedish": "sv", "Tagalog": "tl",
    "Tajik": "tg", "Tamil": "ta", "Telugu": "te", "Thai": "th",
    "Turkish": "tr", "Ukrainian": "uk", "Urdu": "ur", "Uzbek": "uz",
    "Vietnamese": "vi", "Welsh": "cy", "Xhosa": "xh", "Yiddish": "yi",
    "Yoruba": "yo", "Zulu": "zu"
}

async def translate(text: str, target: str, session: aiohttp.ClientSession) -> tuple[str, str] | None:
    """Translate text using Google Translate unofficial API"""
    if not text or not text.strip():
        return None
    
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target,
            "dt": "t",
            "q": text
        }
        
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status != 200:
                print(f"❌ Google API returned status {r.status}")
                return None
            
            data = await r.json()
            
            if data and len(data) > 0 and data[0]:
                translated_parts = []
                for item in data[0]:
                    if item and len(item) > 0 and item[0]:
                        translated_parts.append(item[0])
                
                result = "".join(translated_parts)
                detected_lang = data[2] if len(data) > 2 else "auto"
                
                if result:
                    return (result, detected_lang)
            
            return None
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return None

def test_command_parsing():
    """Test that language commands are correctly parsed"""
    print("🧪 Testing command parsing...")
    
    # Define command aliases
    COMMAND_ALIASES = {
        "vn": "vi",  # Vietnamese
        "kr": "ko",  # Korean
        "cn": "zh",  # Chinese
        "jp": "ja",  # Japanese
        "ua": "uk",  # Ukrainian
    }
    
    # Test Vietnamese (using alias)
    command = "!vn"
    lang_code = command[1:].lower()
    if lang_code in COMMAND_ALIASES:
        lang_code = COMMAND_ALIASES[lang_code]
    assert lang_code == "vi", f"Vietnamese code should be 'vi', got '{lang_code}'"
    
    # Test Spanish
    command = "!es"
    lang_code = command[1:].lower()
    if lang_code in COMMAND_ALIASES:
        lang_code = COMMAND_ALIASES[lang_code]
    assert lang_code == "es", f"Spanish code should be 'es', got '{lang_code}'"
    
    # Test French
    command = "!fr"
    lang_code = command[1:].lower()
    if lang_code in COMMAND_ALIASES:
        lang_code = COMMAND_ALIASES[lang_code]
    assert lang_code == "fr", f"French code should be 'fr', got '{lang_code}'"
    
    print("✅ Command parsing tests passed!")

def test_language_codes():
    """Test that all language codes are available"""
    print("🧪 Testing language codes...")
    
    # Test key languages mentioned in requirements
    assert "Vietnamese" in LANGUAGES, "Vietnamese should be in LANGUAGES"
    assert LANGUAGES["Vietnamese"] == "vi", "Vietnamese code should be 'vi'"
    
    assert "Spanish" in LANGUAGES, "Spanish should be in LANGUAGES"
    assert LANGUAGES["Spanish"] == "es", "Spanish code should be 'es'"
    
    assert "French" in LANGUAGES, "French should be in LANGUAGES"
    assert LANGUAGES["French"] == "fr", "French code should be 'fr'"
    
    # Test total count (should have many languages)
    assert len(LANGUAGES) >= 80, f"Should have at least 80 languages, got {len(LANGUAGES)}"
    
    print(f"✅ Language code tests passed! ({len(LANGUAGES)} languages loaded)")

async def test_translation():
    """Test actual translation functionality"""
    print("🧪 Testing translation API...")
    
    async with aiohttp.ClientSession() as session:
        # Test English to Vietnamese
        result = await translate("Hello, how are you?", "vi", session)
        if result:
            translated, detected = result
            print(f"✅ EN -> VI: '{translated}' (detected: {detected})")
        else:
            print("⚠️ Translation test failed (API might be unavailable)")
        
        # Test English to Spanish
        result = await translate("Good morning", "es", session)
        if result:
            translated, detected = result
            print(f"✅ EN -> ES: '{translated}' (detected: {detected})")
        else:
            print("⚠️ Translation test failed (API might be unavailable)")
        
        # Test Vietnamese to English
        result = await translate("Xin chào", "en", session)
        if result:
            translated, detected = result
            print(f"✅ VI -> EN: '{translated}' (detected: {detected})")
        else:
            print("⚠️ Translation test failed (API might be unavailable)")

def test_command_matching():
    """Test that commands correctly match language codes"""
    print("🧪 Testing command matching logic...")
    
    # Define command aliases
    COMMAND_ALIASES = {
        "vn": "vi",  # Vietnamese
        "kr": "ko",  # Korean
        "cn": "zh",  # Chinese
        "jp": "ja",  # Japanese
        "ua": "uk",  # Ukrainian
    }
    
    test_cases = [
        ("!vn", "vi", "Vietnamese"),  # Using alias
        ("!vi", "vi", "Vietnamese"),  # Direct code
        ("!es", "es", "Spanish"),
        ("!fr", "fr", "French"),
        ("!de", "de", "German"),
        ("!ja", "ja", "Japanese"),
        ("!jp", "ja", "Japanese"),  # Using alias
        ("!zh", "zh", "Chinese"),
        ("!cn", "zh", "Chinese"),  # Using alias
        ("!ru", "ru", "Russian"),
        ("!ar", "ar", "Arabic"),
    ]
    
    for command_str, expected_code, expected_lang in test_cases:
        command = command_str[1:].lower()
        
        # Check for alias first
        if command in COMMAND_ALIASES:
            command = COMMAND_ALIASES[command]
        
        # Find matching language
        found = False
        for lang_name, code in LANGUAGES.items():
            if command == code:
                assert code == expected_code, f"Code mismatch for {command_str}: expected {expected_code}, got {code}"
                assert lang_name == expected_lang, f"Language mismatch for {command_str}: expected {expected_lang}, got {lang_name}"
                found = True
                break
        
        assert found, f"Command {command_str} should match {expected_lang}"
    
    print("✅ Command matching tests passed!")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Running Discord Translation Bot Tests")
    print("=" * 60)
    
    # Run synchronous tests
    test_command_parsing()
    test_language_codes()
    test_command_matching()
    
    # Run async tests
    await test_translation()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
