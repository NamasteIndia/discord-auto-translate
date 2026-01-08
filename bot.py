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
COMMAND_ALIASES = {}
LANGUAGES_PER_FIELD = 25  # Number of languages to show per field in help command
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
    global LANGUAGES, COMMAND_ALIASES
    
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
    
    # Command aliases for common shortcuts
    COMMAND_ALIASES = {
        "vn": "vi",  # Vietnamese
        "kr": "ko",  # Korean
        "cn": "zh",  # Chinese
        "jp": "ja",  # Japanese
        "ua": "uk",  # Ukrainian
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
    """Create a compact and friendly translation embed"""
    # Limit text length for cleaner display
    MAX_ORIGINAL = 200
    MAX_TRANSLATED = 500
    
    # Truncate if too long
    display_original = original if len(original) <= MAX_ORIGINAL else original[:MAX_ORIGINAL] + "..."
    display_translated = translated if len(translated) <= MAX_TRANSLATED else translated[:MAX_TRANSLATED] + "..."
    
    embed = discord.Embed(
        description=f"**{display_translated}**",
        color=0x5865F2  # Discord blurple
    )
    
    # Add original text if it exists and is meaningful
    if display_original and display_original.strip():
        embed.add_field(
            name=f"🔤 {source_lang.upper()} → {target_lang.upper()}",
            value=display_original,
            inline=False
        )
    
    embed.set_footer(
        text=f"Translated for {author.display_name}",
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

# ---------------- MANUAL TRANSLATION COMMANDS ----------------
@bot.event
async def on_message(message: discord.Message):
    # Ignore bot messages
    if message.author.bot:
        return
    
    # Check for manual translation commands (e.g., !vn, !fr, !es)
    if message.content and message.content.startswith('!') and message.reference:
        parts = message.content.split()
        if not parts or len(parts[0]) <= 1:  # Handle edge cases
            await bot.process_commands(message)
            return
        
        command = parts[0][1:].lower()  # Get command without '!'
        
        # Check if command matches a language code or alias
        lang_code = None
        target_lang_name = None
        
        # Check for command alias first (e.g., vn -> vi)
        if command in COMMAND_ALIASES:
            command = COMMAND_ALIASES[command]
        
        # Direct match with language code
        for lang_name, code in LANGUAGES.items():
            if command == code:
                lang_code = code
                target_lang_name = lang_name
                break
        
        if lang_code and target_lang_name:
            try:
                # Get the replied message
                referenced_message = await message.channel.fetch_message(message.reference.message_id)
                
                if not referenced_message.content or not referenced_message.content.strip():
                    await message.reply("⚠️ The message you replied to has no text to translate.", mention_author=False)
                    return
                
                # Translate the message
                result = await translate(referenced_message.content, lang_code)
                
                if not result:
                    await message.reply("⚠️ Translation failed. Please try again.", mention_author=False)
                    return
                
                translated, source_lang = result
                
                # Send translation
                await message.reply(
                    embed=translation_embed(
                        referenced_message.content,
                        translated,
                        source_lang,
                        target_lang_name,
                        message.author
                    ),
                    mention_author=False
                )
                return
            except Exception as e:
                print(f"❌ Manual translation error: {e}")
                await message.reply("⚠️ Error processing translation command.", mention_author=False)
                return
    
    # Process other commands
    await bot.process_commands(message)

    # Skip processing for automatic translation if:
    # - Empty messages or commands
    # - Messages starting with ! or / (commands)
    # - Very short messages
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

# ---------------- HELP COMMAND ----------------
@bot.command(name='languages', aliases=['langs', 'guide'])
async def languages_help(ctx):
    """Show all available language commands"""
    embed = discord.Embed(
        title="🌍 Available Translation Commands",
        description="Reply to any message with these commands to translate it!",
        color=0x5865F2
    )
    
    # Add popular shortcuts first
    if COMMAND_ALIASES:
        shortcuts = []
        for alias, code in COMMAND_ALIASES.items():
            # Find the language name
            for name, lang_code in LANGUAGES.items():
                if lang_code == code:
                    shortcuts.append(f"`!{alias}` → {name}")
                    break
        
        if shortcuts:
            embed.add_field(
                name="⭐ Popular Shortcuts",
                value="\n".join(shortcuts),
                inline=False
            )
    
    # Group languages for better readability
    lang_list = []
    for name, code in sorted(LANGUAGES.items()):
        lang_list.append(f"`!{code}` {name}")
    
    # Split into chunks for multiple fields
    for i in range(0, len(lang_list), LANGUAGES_PER_FIELD):
        chunk = lang_list[i:i+LANGUAGES_PER_FIELD]
        field_name = f"Languages ({i+1}-{min(i+LANGUAGES_PER_FIELD, len(lang_list))})"
        embed.add_field(name=field_name, value="\n".join(chunk), inline=True)
    
    embed.set_footer(text="Example: Reply to a message with !vn to translate to Vietnamese")
    await ctx.send(embed=embed)

@bot.command(name='translate')
async def translate_prefix_cmd(ctx, lang: str = None):
    """Translate a replied message using prefix command"""
    if not ctx.message.reference:
        await ctx.reply("⚠️ Please reply to a message you want to translate!", mention_author=False)
        return
    
    if not lang:
        await ctx.reply("⚠️ Please specify a language code! Use `!languages` to see all codes.", mention_author=False)
        return
    
    # Find the language
    lang_code = None
    target_lang_name = None
    
    # Normalize the language input
    lang_lower = lang.lower()
    
    # Check for command alias first (e.g., vn -> vi)
    if lang_lower in COMMAND_ALIASES:
        lang_lower = COMMAND_ALIASES[lang_lower]
    
    # Check if it's a language code or name
    for lang_name, code in LANGUAGES.items():
        if lang_lower == code or lang_lower == lang_name.lower():
            lang_code = code
            target_lang_name = lang_name
            break
    
    if not lang_code:
        await ctx.reply(f"⚠️ Unknown language: `{lang}`. Use `!languages` to see all codes.", mention_author=False)
        return
    
    try:
        # Get the replied message
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        
        if not referenced_message.content or not referenced_message.content.strip():
            await ctx.reply("⚠️ The message you replied to has no text to translate.", mention_author=False)
            return
        
        # Translate the message
        result = await translate(referenced_message.content, lang_code)
        
        if not result:
            await ctx.reply("⚠️ Translation failed. Please try again.", mention_author=False)
            return
        
        translated, source_lang = result
        
        # Send translation
        await ctx.reply(
            embed=translation_embed(
                referenced_message.content,
                translated,
                source_lang,
                target_lang_name,
                ctx.author
            ),
            mention_author=False
        )
    except Exception as e:
        print(f"❌ Translation error: {e}")
        await ctx.reply("⚠️ Error processing translation.", mention_author=False)

# ---------------- SHUTDOWN CLEANUP ----------------
@bot.event
async def on_close():
    if http_session:
        await http_session.close()

# ---------------- START ----------------
bot.run(TOKEN)
