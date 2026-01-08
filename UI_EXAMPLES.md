# UI Examples

## Old UI (Before Changes)

```
┌────────────────────────────────────────────────┐
│ 🌐 EN → VI                                     │
│ ────────────────────────────────────────────   │
│ ### Xin chào, bạn khỏe không?                  │
│                                                 │
│ 📝 Original                                     │
│ ```                                             │
│ Hello, how are you?                             │
│ ```                                             │
│                                                 │
│ Bot by UserName                    [avatar]    │
└────────────────────────────────────────────────┘
```

**Issues with Old UI:**
- Too much spacing (markdown headers, code blocks)
- Yellow color (#F1C40F) doesn't match Discord theme
- "Bot by" wording is awkward
- Code block formatting for original text is excessive


## New UI (After Changes)

```
┌────────────────────────────────────────────────┐
│ **Xin chào, bạn khỏe không?**                  │
│                                                 │
│ 🔤 EN → VIETNAMESE                              │
│ Hello, how are you?                             │
│                                                 │
│ Translated for UserName            [avatar]    │
└────────────────────────────────────────────────┘
```

**Improvements in New UI:**
- Clean, compact design with bold translated text prominently displayed
- Discord blurple color (#5865F2) matches Discord's native theme
- Original text shown without code blocks for cleaner look
- Clearer language direction indicator
- More natural footer text
- Automatic truncation for very long messages (200 chars original, 500 chars translation)


## Command Examples

### Using the Vietnamese shortcut
```
User A: "Hello everyone, nice to meet you!"
User B: [Replies to User A's message] !vn

Bot: [Shows translation]
**Xin chào mọi người, rất vui được gặp bạn!**

🔤 EN → VIETNAMESE
Hello everyone, nice to meet you!

Translated for User B
```

### Using the Spanish shortcut
```
User A: "I love programming in Python!"
User B: [Replies to User A's message] !es

Bot: [Shows translation]
**¡Me encanta programar en Python!**

🔤 EN → SPANISH
I love programming in Python!

Translated for User B
```

### Using the help command
```
User: !languages

Bot: [Shows embed with all language codes]
🌍 Available Translation Commands

⭐ Popular Shortcuts
!vn → Vietnamese
!jp → Japanese
!cn → Chinese
!kr → Korean
!ua → Ukrainian

Languages (1-25)
!af Afrikaans
!sq Albanian
!am Amharic
...

Example: Reply to a message with !vn to translate to Vietnamese
```

## Feature Highlights

1. **90+ Language Support**: All Google Translate languages are supported
2. **Smart Shortcuts**: Popular language codes like `!vn` for Vietnamese
3. **Both Methods Work**: Use either `!vn` or `!vi` for Vietnamese
4. **Clean UI**: Compact embed design that looks professional
5. **Helpful Commands**: `!languages`, `!langs`, or `!help` to see all codes
6. **Reply-Based**: Just reply to any message with a language command
