-- Panyari Bot SQLite schema

CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'th',
    welcome_channel_id INTEGER,
    goodbye_channel_id INTEGER,
    audit_log_channel_id INTEGER,
    automod_enabled INTEGER DEFAULT 0,
    automod_spam_threshold INTEGER DEFAULT 5,
    automod_max_mentions INTEGER DEFAULT 5,
    tts_language TEXT,
    tts_voice TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_warnings_guild_user ON warnings(guild_id, user_id);
