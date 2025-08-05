# 🤖 zhybot

[中文文档](README_zh.md) | English

A comprehensive QQ bot built on NoneBot2 framework with 12 powerful plugin modules!

---

## 📖 What is zhybot

Zhybot is a feature-rich QQ bot designed for group management and entertainment. Built on the powerful [Nonebot2 framework](https://nonebot.dev) with extensive plugin architecture for reliable messaging automation and advanced functionality.

---

## 🚀 Core Features

### 🤖 AI Chat Integration
> **Intelligent conversation system with OpenAI-compatible API**
- **Features:**
  - Natural conversation with thinking process display
  - Configurable AI models and prompts
  - Per-bot conversation history management
  - Admin commands for model/prompt adjustment
  - Multiple API key support with load balancing

### 🎵 Music Download Service
> **Automated music downloading from streaming platforms**
- **Features:**
  - Automatic NetEase Cloud Music link detection
  - High-quality MP3 downloads
  - VIP content handling
  - Direct file sharing to group chat
- **Supported Platforms:**
  - 🎧 Netease Music (music.163.com)

### 👍 Smart Like System
> **Intelligent auto-like functionality with scheduling**
- **Usage:**
  ```bash
  *我                # Send likes (reply with * + any word)
  定时赞 开/关       # Enable/disable scheduled auto-like
  ```
- **Features:**
  - Pattern-based like detection
  - Scheduled daily likes at 5 AM
  - Batch group operations
  - Configurable like counts and target lists

### 🔍 Database Search
> **Advanced user information lookup system**
- **Usage:**
  ```bash
  cx qq [id]     # Search phone number by QQ ID
  cx phone [id]  # Search QQ ID by phone number
  ```
- **Features:**
  - Bidirectional QQ-phone number lookup
  - MySQL database integration
  - Performance timing display

### 🛡️ Message Moderation
> **Automated content filtering and user management**
- **Features:**
  - Admin-controlled ban list management
  - Automatic message deletion
  - User auto-kick for banned content
  - Per-group ban configuration

### 💣 Message Bomber
> **Controlled message spam for testing purposes**
- **Usage:**
  ```bash
  bomb
      -m|--message             # Message to send
      -t|--times              # Number of times to send
      -s|--speed              # Speed (messages/minute)
      --enable-dangerous-mode # Required when speed >= 60
  ```
- **Safety:** Built-in rate limiting and dangerous mode protection

### 🎭 Meme Generation
> **Dynamic meme creation system**
- **Features:**
  - GIF frame extraction
  - Image processing capabilities
  - Cached meme storage

### 📚 Novel Recommendations
> **Random novel discovery from fanqie platform**
- **Command:** `来本小说` (Get a novel)
- **Features:**
  - Random book recommendations
  - Cover image display
  - Encoded content handling

### 🎉 Welcome System
> **Automated member greeting and management**
- **Features:**
  - New member welcome messages
  - Departure notifications
  - Avatar integration
  - Custom greeting templates

### 💻 System Command Interface
> **Remote command execution capability**
- **Usage:** `run [command]`
- **Features:**
  - Secure user isolation via sudo
  - Stdout/stderr capture
  - Superuser permission required

### ⚙️ Configuration Management
> **Centralized bot configuration system**
- **Features:**
  - JSON-based configuration storage
  - Per-bot and global settings
  - Auto-initialization with defaults
  - Type-safe configuration access

### 🔧 Utility Functions
> **Common helper functions and tools**
- **Features:**
  - Standard message formatting
  - Bot addressing detection
  - Selenium web automation utilities

### 👨‍👩‍👧‍👦 Fuck Group Members Game
> **Fun interactive game**
- **Usage:**
  ```bash
  草群友           # Randomly select a group member
  草群友 @someone  # Specify a target
  草群友 [reply]   # Reply to a specific user
  ```
- **Features:**
  - Random selection of suitable group members
  - Life essence system (value accumulation)
  - Unconsciousness mechanism (prevents over-interaction)
  - Data statistics and leaderboard functionality
  - Group member avatar display

---

## 🏗️ Technical Architecture

### Framework & Dependencies
- **Core Framework:** NoneBot2 with OneBot V11 adapter
- **Python Version:** 3.9+
- **Plugin System:** Modular architecture with 12 specialized plugins
- **Configuration:** Centralized JSON-based configuration management

### Plugin Architecture
```
src/plugins/
├── _aichat/          # AI conversation system
├── _dailythings/     # Novel recommendations
├── ban/              # Message moderation
├── bomb/             # Message bombing
├── config/           # Configuration management
├── cx/               # Database search
├── fuck_friend/      # Fuck group members game
├── gen_meme/         # Meme generation
├── likeme/           # Auto-like system
├── music/            # Music downloads
├── run/              # Command execution
├── utils/            # Utility functions
└── welcome/          # Member greeting
```

---

## 🚦 Installation & Setup

### Prerequisites
- Python 3.9+
- MySQL database (for cx plugin)
- Chrome/Chromium browser (for music plugin)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/zhybot.git
cd zhybot

# Install dependencies
pip install -r requirements.txt

# Configure your bot
cp config.json.example config.json
# Edit config.json with your settings

# Run the bot
python bot.py
```

---

## ⚙️ Configuration

The bot uses a centralized configuration system in `config.json`:

```json
{
  "default": {
    "openai_api_endpoint": "https://api.example.com/v1",
    "openai_api_keys": ["your-api-key"],
    "openai_model": "gpt-3.5-turbo",
    "like_times": 50,
    "like_users": [],
    "like_groups": []
  }
}
```

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests! 

### Development Guidelines
- Follow existing code patterns and conventions
- Test your changes thoroughly
- Update documentation for new features
- Ensure security best practices

---

## 📄 License

This project is open source and available under the [GPL-3.0 License](LICENSE).