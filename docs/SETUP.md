# Setup Guide

This guide covers how to set up and run Panyari Bot on your local machine or a cloud server.

## Requirements

- Python 3.11 or higher
- Java 17 or higher (required for Lavalink)
- FFmpeg (required for TTS and voice features)
- A Discord bot token
- Git (optional)

## 1. Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name.
3. Navigate to **Bot** in the left sidebar.
4. Click **Reset Token** and copy the token.
5. Enable the following Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent
6. Use the OAuth2 URL Generator to create an invite link with the `bot` and `applications.commands` scopes.
   - Recommended permissions: `Administrator` for full functionality, or manually select moderation, voice, and message management permissions.

## 2. Clone the Repository

```bash
git clone https://github.com/yourusername/panyari-bot.git
cd panyari-bot
```

## 3. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

For development, also install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

## 5. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
DISCORD_TOKEN=your_bot_token_here
DEFAULT_LANGUAGE=th
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
```

**Never commit `.env` to version control.** It is already listed in `.gitignore`.

## 6. Install FFmpeg

FFmpeg is required for the Text-to-Speech (TTS) feature and Discord voice playback.

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or install via `winget install FFmpeg`. Add it to your PATH.
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo dnf install ffmpeg` (Fedora)

Verify installation:

```bash
ffmpeg -version
```

## 7. Download and Start Lavalink

Lavalink is a separate Java server that handles audio playback.

### Automatic Download

```bash
python lavalink/start_lavalink.py
```

This downloads `Lavalink.jar` (about 60 MB) and starts the server.

### Manual Download

1. Download the latest `Lavalink.jar` from the [Lavalink releases page](https://github.com/lavalink-devs/Lavalink/releases).
2. Place it in the `lavalink/` directory.
3. Run:

```bash
cd lavalink
java -jar Lavalink.jar
```

### Verify Lavalink is Running

You should see `Lavalink is ready to accept connections.` in the terminal.

## 8. Start the Bot

Open a second terminal, activate the virtual environment, and run:

```bash
python run.py
```

If everything is configured correctly, you will see:

```text
Panyari Bot is ready | Logged in as Panyari Bot#1234
Synced N slash commands
```

## Optional: Start Lavalink and Bot Together

You can use a process manager like `pm2`, `systemd`, or Docker Compose to keep both services running. See the deployment notes in the main README.
