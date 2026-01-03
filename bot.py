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
LIBRE_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com/translate")
PORT = int(os.getenv("PORT", 8080))

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN missing")

LIBRE_BASE = LIBRE_URL.replace("/translate", "")

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
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            async with http_session.get(
                f"{LIBRE_BASE}/languages", 
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                data = await r.json()
                for lang in data:
                    LANGUAGES[lang["name"]] = lang["code"]
                print(f"✅ Loaded {len(LANGUAGES)} languages")
                return
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Failed to load languages (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"   Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print(f"❌ Could not connect to LibreTranslate after {max_retries} attempts")
                print(f"   Using public LibreTranslate instance")
                # Load a basic set of languages as fallback
                LANGUAGES.update({
                    "English": "en", "Spanish": "es", "French": "fr",
                    "German": "de", "Italian": "it", "Portuguese": "pt",
                    "Russian": "ru", "Japanese": "ja", "Chinese": "zh",
                    "Korean": "ko", "Arabic": "ar", "Hindi": "hi"
                })

# ---------------- TRANSLATE FUNCTION ----------------
async def translate(text: str, target: str) -> str | None:
    try:
        async with http_session.post(
            f"{LIBRE_BASE}/translate",
            json={
                "q": text,
                "source": "auto",
                "target": target,
                "format": "text"
            },
            timeout=aiohttp.ClientTimeout(total=20)
        ) as r:
            data = await r.json()
            return data.get("translatedText")
    except (asyncio.TimeoutError, aiohttp.ClientError):
        return None
    except Exception:
        return None

# ---------------- EMBED UI ----------------
def translation_embed(original, translated, language, author):
    embed = discord.Embed(
        title=f"🌐 iTranslator • {language}",
        description=f"**{translated}**",
        color=0xF1C40F
    )
    embed.add_field(
        name="📝 Original",
        value=f"> {original[:1000]}",
        inline=False
    )
    embed.set_footer(
        text=f"Requested by {author.display_name}",
        icon_url=author.display_avatar.url
    )
    return embed

# ---------------- READY ----------------
@bot.event
async def on_ready():
    global http_session
    http_session = aiohttp.ClientSession()
    
    print(f"🤖 Bot online as {bot.user}")
    print(f"🔗 Connecting to LibreTranslate at: {LIBRE_BASE}")
    
    # Start health check server
    await start_health_server()
    
    await load_languages()
    await bot.tree.sync()
    
    print(f"✅ Bot ready!")

# ---------------- AUTO ENGLISH ----------------
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if not LANGUAGES:
        await bot.process_commands(message)
        return

    translated = await translate(message.content, "en")

    if not translated:
        await bot.process_commands(message)
        return

    if translated.lower().strip() != message.content.lower().strip():
        await message.reply(
            embed=translation_embed(
                message.content,
                translated,
                "English",
                message.author
            ),
            mention_author=False
        )

    await bot.process_commands(message)

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
