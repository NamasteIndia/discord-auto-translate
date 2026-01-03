import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from aiohttp import web

# ---------------- LOAD ENV ----------------
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 8080))

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN missing")

print(f"🌐 Using Google Translate (unofficial API)")

# ---------------- BOT SETUP ----------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

LANGUAGES = {}
http_session: aiohttp.ClientSession | None = None
health_app = web.Application()

# ---------------- HEALTH CHECK SERVER ----------------
async def health_check(request):
    """Koyeb health check endpoint"""
    status = {
        "status": "healthy",
        "bot_ready": bot.is_ready(),
        "languages_loaded": len(LANGUAGES),
        "service": "discord-translate-bot"
    }
    return web.json_response(status)

async def root_handler(request):
    """Root endpoint"""
    return web.Response(text="Discord Translation Bot is running!")

health_app.router.add_get('/health', health_check)
health_app.router.add_get('/', root_handler)

async def start_health_server():
    """Start health check server for Koyeb"""
    runner = web.AppRunner(health_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🏥 Health check server running on port {PORT}")

# ---------------- LOAD LANGUAGES ----------------
async def load_languages():
    """Load supported languages for Google Translate"""
    global LANGUAGES
    
    # Google Translate supported languages
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
    print(f"✅ Loaded {len(LANGUAGES)} languages (Google Translate)")

# ---------------- TRANSLATE FUNCTION ----------------
# ---------------- TRANSLATE FUNCTION ----------------
async def translate(text: str, target: str) -> tuple[str, str] | None:
    """Translate text using Google Translate unofficial API
    Returns: (translated_text, detected_source_language) or None
    """
    if not text or not text.strip():
        return None
    
    try:
        # Google Translate unofficial endpoint
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",  # source language (auto-detect)
            "tl": target,   # target language
            "dt": "t",      # return translation
            "q": text
        }
        
        async with http_session.get(
            url, 
            params=params,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            if r.status != 200:
                print(f"❌ Google API returned status {r.status}")
                return None
            
            data = await r.json()
            
            # Parse the response - it's a nested array
            # data[0] contains translation, data[2] contains detected language
            if data and len(data) > 0 and data[0]:
                translated_parts = []
                for item in data[0]:
                    if item and len(item) > 0 and item[0]:
                        translated_parts.append(item[0])
                
                result = "".join(translated_parts)
                
                # Get detected source language (if available)
                detected_lang = data[2] if len(data) > 2 else "auto"
                
                if result:
                    print(f"✅ Translation: {detected_lang} -> {target}: {result[:100]}")
                    return (result, detected_lang)
            
            return None
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return None

# ---------------- EMBED UI ----------------
def translation_embed(original, translated, source_lang, target_lang, author):
    source_flag = get_flag(source_lang)
    target_flag = get_flag(target_lang)
    
    embed = discord.Embed(
        title=f"{source_flag} {source_lang.upper()} → {target_flag} {target_lang.upper()}",
        description=f"### {translated}",
        color=0xF1C40F  # Yellow border
    )
    embed.add_field(
        name=f"{source_flag} Original",
        value=f"```{original[:1000]}```",
        inline=False
    )
    embed.set_footer(
        text=f"Bot by {author.display_name}",
        icon_url=author.display_avatar.url
    )
    return embed

# ---------------- READY ----------------
@bot.event
async def on_ready():
    global http_session
    http_session = aiohttp.ClientSession()
    
    print(f"🤖 Bot online as {bot.user}")
    print(f"🌐 Using Google Translate (unofficial API)")
    
    # Start health check server
    await start_health_server()
    
    await load_languages()
    await bot.tree.sync()
    
    print(f"✅ Bot ready!")

# ---------------- AUTO ENGLISH ----------------
@bot.event
async def on_message(message: discord.Message):
    # Process commands first
    await bot.process_commands(message)
    
    # Ignore bot messages
    if message.author.bot:
        return

    # Skip empty messages or commands
    if not message.content or len(message.content.strip()) < 2 or message.content.startswith('!') or message.content.startswith('/'):
        return

    # Skip if languages not loaded
    if not LANGUAGES:
        print("⚠️ Languages not loaded, skipping translation")
        return

    # Translate to English
    try:
        print(f"🔄 Attempting to translate: '{message.content[:50]}...'")
        result = await translate(message.content, "en")
        
        if not result:
            print(f"❌ Translation failed or returned None")
            return
        
        translated, source_lang = result
        print(f"✅ Translation result: '{translated[:50]}...'")
        
        # Only reply if translation is different from original
        if translated.lower().strip() != message.content.lower().strip():
            # Check if the difference is significant (not just punctuation)
            original_words = message.content.lower().strip().replace(".", "").replace(",", "").replace("!", "").replace("?", "").replace("¿", "").replace("¡", "")
            translated_words = translated.lower().strip().replace(".", "").replace(",", "").replace("!", "").replace("?", "").replace("¿", "").replace("¡", "")
            
            if original_words != translated_words:
                print(f"📤 Sending translation reply")
                await message.reply(
                    embed=translation_embed(
                        message.content,
                        translated,
                        source_lang,
                        "en",
                        message.author
                    ),
                    mention_author=False
                )
            else:
                print(f"⏭️ Skipping - only punctuation difference")
        else:
            print(f"⏭️ Skipping - already in English or no change")
    except Exception as e:
        print(f"❌ Translation error: {e}")
        import traceback
        traceback.print_exc()

# ---------------- /TRANSLATE ----------------
@bot.tree.command(name="translate", description="Translate replied message")
@app_commands.describe(language="Target language")
async def translate_cmd(interaction: discord.Interaction, language: str):
    
    if not LANGUAGES:
        await interaction.response.send_message(
            "⚠️ Translation service is unavailable. Please try again later.",
            ephemeral=True
        )
        return

    resolved = interaction.data.get("resolved", {}).get("messages")
    if not resolved:
        await interaction.response.send_message(
            "Reply to a message and use `/translate`.",
            ephemeral=True
        )
        return

    msg_id = list(resolved.keys())[0]
    msg = await interaction.channel.fetch_message(int(msg_id))

    lang_code = LANGUAGES.get(language)
    if not lang_code:
        await interaction.response.send_message("Unknown language.", ephemeral=True)
        return

    translated = await translate(msg.content, lang_code)
    if not translated:
        await interaction.response.send_message(
            "⚠️ Translation service is busy. Try again.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        embed=translation_embed(
            msg.content,
            translated,
            language,
            interaction.user
        )
    )

# ---------------- AUTOCOMPLETE ----------------
@translate_cmd.autocomplete("language")
async def language_autocomplete(interaction, current):
    return [
        app_commands.Choice(name=name, value=name)
        for name in LANGUAGES
        if current.lower() in name.lower()
    ][:25]

# ---------------- SHUTDOWN CLEANUP ----------------
@bot.event
async def on_close():
    if http_session:
        await http_session.close()

# ---------------- START ----------------
bot.run(TOKEN)
