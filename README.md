# Discord Auto-Translate Bot 🌍

A Discord bot that automatically translates messages to English and provides manual translation commands for 90+ languages.

## Features

### 🤖 Automatic Translation
- Automatically translates non-English messages to English
- Smart detection to avoid translating already-English content
- Clean, compact embed UI

### 💬 Manual Translation Commands
Translate any message by replying to it with a language command!

**Popular Shortcuts:**
- `!vn` - Translate to Vietnamese (alias for `!vi`)
- `!jp` - Translate to Japanese (alias for `!ja`)
- `!cn` - Translate to Chinese (alias for `!zh`)
- `!kr` - Translate to Korean (alias for `!ko`)
- `!ua` - Translate to Ukrainian (alias for `!uk`)

**Direct Language Codes:**
- `!es` - Spanish
- `!fr` - French
- `!de` - German
- `!it` - Italian
- `!pt` - Portuguese
- `!ru` - Russian
- `!ar` - Arabic
- `!hi` - Hindi
- And 80+ more languages!

**How to use:**
1. Reply to any message you want to translate
2. Type `!<language-code>` (e.g., `!vn` for Vietnamese or `!vi`)
3. The bot will instantly translate the message for you!

### 📚 View All Languages
- `!languages` or `!langs` or `!help` - Shows all available language commands
- `!translate <language-code>` - Alternative way to translate a replied message

### 🌐 Supported Languages (90+)

| Code | Language | Code | Language | Code | Language |
|------|----------|------|----------|------|----------|
| af | Afrikaans | sq | Albanian | am | Amharic |
| ar | Arabic | hy | Armenian | az | Azerbaijani |
| eu | Basque | be | Belarusian | bn | Bengali |
| bs | Bosnian | bg | Bulgarian | ca | Catalan |
| ceb | Cebuano | zh | Chinese | co | Corsican |
| hr | Croatian | cs | Czech | da | Danish |
| nl | Dutch | en | English | eo | Esperanto |
| et | Estonian | fi | Finnish | fr | French |
| gl | Galician | ka | Georgian | de | German |
| el | Greek | gu | Gujarati | ht | Haitian Creole |
| ha | Hausa | haw | Hawaiian | he | Hebrew |
| hi | Hindi | hmn | Hmong | hu | Hungarian |
| is | Icelandic | ig | Igbo | id | Indonesian |
| ga | Irish | it | Italian | ja | Japanese |
| jv | Javanese | kn | Kannada | kk | Kazakh |
| km | Khmer | ko | Korean | ku | Kurdish |
| ky | Kyrgyz | lo | Lao | la | Latin |
| lv | Latvian | lt | Lithuanian | lb | Luxembourgish |
| mk | Macedonian | mg | Malagasy | ms | Malay |
| ml | Malayalam | mt | Maltese | mi | Maori |
| mr | Marathi | mn | Mongolian | my | Myanmar |
| ne | Nepali | no | Norwegian | ny | Nyanja |
| ps | Pashto | fa | Persian | pl | Polish |
| pt | Portuguese | pa | Punjabi | ro | Romanian |
| ru | Russian | sm | Samoan | gd | Scots Gaelic |
| sr | Serbian | st | Sesotho | sn | Shona |
| sd | Sindhi | si | Sinhala | sk | Slovak |
| sl | Slovenian | so | Somali | es | Spanish |
| su | Sundanese | sw | Swahili | sv | Swedish |
| tl | Tagalog | tg | Tajik | ta | Tamil |
| te | Telugu | th | Thai | tr | Turkish |
| uk | Ukrainian | ur | Urdu | uz | Uzbek |
| vi | Vietnamese | cy | Welsh | xh | Xhosa |
| yi | Yiddish | yo | Yoruba | zu | Zulu |

## Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/NamasteIndia/discord-auto-translate.git
cd discord-auto-translate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Discord token:
```
DISCORD_TOKEN=your_discord_bot_token_here
PORT=8080
```

4. Run the bot:
```bash
python bot.py
```

## Deployment

### Docker
```bash
docker build -t discord-translate-bot .
docker run -e DISCORD_TOKEN=your_token discord-translate-bot
```

### Koyeb
The bot includes health check endpoints for Koyeb deployment. Simply connect your repository and set the `DISCORD_TOKEN` environment variable.

## Translation Service

This bot uses Google Translate's unofficial API for translations. It supports:
- Automatic language detection
- 90+ languages
- Fast and reliable translations

## UI Design

The bot features a clean, compact embed design:
- **Bold translated text** prominently displayed
- Original text shown below with language direction indicator
- User attribution in footer
- Discord blurple color scheme
- Automatic text truncation for long messages

## Examples

### Manual Translation
```
User: *replies to "Hello, how are you?" and types: !es*
Bot: **Hola, ¿cómo estás?**
     🔤 EN → ES
     Hello, how are you?
     Translated for User
```

### Viewing Languages
```
User: !languages
Bot: *Shows embed with all 90+ language commands organized by category*
```

## Contributing

Feel free to submit issues and pull requests!

## License

MIT License
