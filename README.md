# Panyari Bot

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Panyari Bot is a feature-rich, open-source Discord bot built with Python. It provides a complete server management toolkit, high-quality music playback through Lavalink, entertainment commands, and bilingual support (Thai/English).

## Features

- **Slash Commands** - Modern Discord interactions with `/` commands
- **Music Playback** - Play YouTube audio via Lavalink with queue, loop, volume, and playback controls
- **Server Management** - Kick, ban, timeout, warn, purge, slowmode, and audit logs
- **Welcome/Goodbye Messages** - Configurable join/leave announcements
- **Auto-Moderation** - Basic spam and mass-mention detection
- **Entertainment** - Dice, coin flip, magic 8-ball, polls, and Q&A
- **Utility** - Server info, user info, avatar lookup
- **Text-to-Speech** - Multi-language, multi-voice TTS in voice channels (powered by edge-tts)
- **Bilingual** - Switch between Thai and English per server
- **SQLite Persistence** - Per-guild settings and warning history

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Discord Library | [discord.py](https://github.com/Rapptz/discord.py) 2.5+ |
| Music | [wavelink](https://github.com/PythonistaGuild/Wavelink) + [Lavalink](https://github.com/lavalink-devs/Lavalink) |
| TTS | [edge-tts](https://github.com/rany2/edge-tts) |
| Config | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| Database | SQLite (stdlib) |
| HTTP | aiohttp |

## Quick Start

For a detailed setup guide, see [docs/SETUP.md](docs/SETUP.md).

### Prerequisites

- Python 3.11 or higher
- Java 17 or higher (for Lavalink)
- FFmpeg (for TTS and voice features)
- A Discord bot token

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/panyari-bot.git
cd panyari-bot

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env` and add your Discord bot token:

```ini
DISCORD_TOKEN=your_bot_token_here
DEFAULT_LANGUAGE=th
```

### Start Lavalink

```bash
python lavalink/start_lavalink.py
```

### Start the Bot

Open a second terminal and run:

```bash
python run.py
```

## Commands

See the full command list in [docs/COMMANDS.md](docs/COMMANDS.md).

## Project Structure

```text
Panyari-DisBot/
├── cogs/                 # Command modules
│   ├── core.py           # ping, help, setlanguage
│   ├── moderation.py     # kick, ban, timeout, warn, purge
│   ├── music.py          # Lavalink music commands
│   ├── tts.py            # text-to-speech commands
│   ├── fun.py            # entertainment commands
│   ├── utility.py        # server/user info
│   ├── welcome.py        # join/leave settings
│   ├── automod.py        # anti-spam
│   └── events.py         # global error handler
├── db/                   # SQLite schema and helpers
├── locales/              # Translation files (th/en)
├── lavalink/             # Lavalink config and launcher
├── utils/                # Shared helpers
├── tests/                # Unit tests
├── docs/                 # Documentation
├── run.py                # Bot entry point
├── config.py             # Configuration loader
└── requirements.txt      # Python dependencies
```

## Development

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

Run linting and formatting:

```bash
ruff check .
black .
isort .
```

## Deployment Notes

Panyari Bot is designed to be self-hosted or deployed to a cloud VPS.

- Keep `.env` secure and never commit it.
- Run Lavalink and the bot as separate processes.
- Use a process manager such as `pm2`, `systemd`, or `supervisord`.
- For containerized deployments, run Lavalink in one container and the bot in another.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run `ruff check .` and `pytest` before submitting
4. Open a pull request with a clear description

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py)
- [Wavelink](https://github.com/PythonistaGuild/Wavelink)
- [Lavalink](https://github.com/lavalink-devs/Lavalink)
