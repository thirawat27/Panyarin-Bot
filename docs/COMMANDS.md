# Command Reference

All commands use Discord slash commands (`/`).

## Core

| Command | Description | Permission |
|---------|-------------|------------|
| `/ping` | Check bot latency | Everyone |
| `/help` | Show all available commands | Everyone |
| `/setlanguage <language>` | Set server language (`th` or `en`) | Manage Server |

## Server Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/kick <user> [reason]` | Kick a member | Kick Members |
| `/ban <user> [reason] [delete_days]` | Ban a member | Ban Members |
| `/unban <user_id>` | Unban a user by ID | Ban Members |
| `/timeout <user> <minutes> [reason]` | Timeout a member | Moderate Members |
| `/warn <user> <reason>` | Warn a member | Moderate Members |
| `/warnings <user>` | View a member's warnings | Moderate Members |
| `/purge <amount>` | Delete up to 100 messages | Manage Messages |
| `/slowmode <seconds>` | Set channel slowmode | Manage Channels |

## Music

| Command | Description | Permission |
|---------|-------------|------------|
| `/play <query>` | Play a song from YouTube | Everyone |
| `/pause` | Pause the current song | Everyone |
| `/resume` | Resume the current song | Everyone |
| `/skip` | Skip the current song | Everyone |
| `/queue` | Show the music queue | Everyone |
| `/nowplaying` | Show the current song | Everyone |
| `/volume <0-100>` | Set playback volume | Everyone |
| `/loop` | Toggle loop mode | Everyone |
| `/leave` | Disconnect from voice channel | Everyone |

## Entertainment

| Command | Description | Permission |
|---------|-------------|------------|
| `/dice [sides]` | Roll a dice | Everyone |
| `/coinflip` | Flip a coin | Everyone |
| `/8ball <question>` | Ask the magic 8-ball | Everyone |
| `/poll <question>` | Create a reaction poll | Everyone |
| `/ask <question>` | Ask a yes/no question | Everyone |

## Utility

| Command | Description | Permission |
|---------|-------------|------------|
| `/serverinfo` | Show server information | Everyone |
| `/userinfo [user]` | Show user information | Everyone |
| `/avatar [user]` | Show user avatar | Everyone |

## Text-to-Speech

| Command | Description | Permission |
|---------|-------------|------------|
| `/tts <message> [language] [voice_model]` | Speak text in a voice channel | Everyone |
| `/tts_voices [language]` | List available voice models | Everyone |
| `/tts_languages` | List supported languages | Everyone |
| `/tts_setlanguage <language>` | Set default TTS language | Manage Server |
| `/tts_setvoice <voice_model>` | Set default TTS voice model | Manage Server |

TTS is powered by [edge-tts](https://github.com/rany2/edge-tts). Examples:

- `/tts message:Hello world` (uses server default)
- `/tts message:สวัสดีครับ`
- `/tts message:Hello world language:en-US`
- `/tts message:สวัสดีครับ language:th-TH`
- `/tts_voices language:en-US`
- `/tts_setlanguage language:th-TH`
- `/tts_setvoice voice_model:th-TH-PremwadeeNeural`

**Note:** TTS cannot be used while music is playing.

## Welcome & Audit

| Command | Description | Permission |
|---------|-------------|------------|
| `/setwelcome <channel>` | Set welcome channel | Manage Server |
| `/setgoodbye <channel>` | Set goodbye channel | Manage Server |
| `/setaudit <channel>` | Set audit log channel | Manage Server |

## Auto-Moderation

| Command | Description | Permission |
|---------|-------------|------------|
| `/automod <enabled>` | Enable or disable auto-moderation | Manage Server |

Auto-moderation currently detects:

- Repeated identical messages within 10 seconds
- Messages with too many mentions

Thresholds can be configured in the database or extended in `cogs/automod.py`.
