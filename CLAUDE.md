# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

zhybot is a comprehensive QQ bot built on the NoneBot2 framework with a modular plugin architecture. The bot provides 12 specialized plugins for group management, entertainment, and automation.

## Development Commands

### Running the Bot
```bash
nb run
```

### Testing and Linting
No specific test or lint commands are configured in this project. When adding testing or linting tools, update this section.

## Architecture

### Core Framework
- **Framework**: NoneBot2 with OneBot V11 adapter
- **Python Version**: 3.9+
- **Entry Point**: `bot.py` - Simple initialization script that loads plugins from `pyproject.toml`
- **Configuration**: Centralized JSON-based system in `config.json`

### Plugin System
All plugins are located in `src/plugins/` with the following structure:

#### Core Plugins
- **`config/`** - Centralized configuration management with per-bot settings
- **`utils/`** - Common utilities including message formatting, bot addressing detection, and Selenium helpers
- **`aichat/`** - AI conversation system with OpenAI API integration, chat history management, and streaming responses

#### Feature Plugins
- **`music/`** - Music download service from NetEase Cloud Music using Selenium web automation
- **`likeme/`** - Smart auto-like system with scheduling and pattern-based detection
- **`cx/`** - Database search for QQ-phone number lookup with MySQL integration
- **`ban/`** - Message moderation with automated content filtering and user management
- **`bomb/`** - Controlled message spam testing with rate limiting and safety features
- **`gen_meme/`** - Dynamic meme generation with GIF processing and caching
- **`dailythings/`** - Novel recommendations from fanqie platform with encoding handling
- **`welcome/`** - Automated member greeting system
- **`run/`** - Remote command execution with security isolation

### Configuration System
The bot uses a sophisticated configuration system (`src/plugins/config/__init__.py`):

- **GlobalConfig**: Manages JSON configuration file with per-bot settings
- **BotConfig**: Bot-specific configuration wrapper
- **Default Configuration**: Includes OpenAI API settings, like system parameters, and ban lists
- **Auto-initialization**: Creates default configs for new bots on first connection

### Key Components

#### AI Chat System (`src/plugins/aichat/__init__.py`)
- **HistoryManager**: Robust chat history management with atomic file operations, backup system, and corruption recovery
- **Streaming Responses**: Real-time response streaming with thinking/response separation
- **Configuration**: Supports multiple API keys, custom models, and conversation history limits

#### Utility Functions (`src/plugins/utils/__init__.py`)
- `get_basemsg()`: Generates standard reply messages with mentions
- `is_calling_me()`: Detects if the bot is being addressed
- `weighted_random()`: Weighted random number generation

#### Plugin Communication
Plugins import utilities and configuration using relative imports:
```python
from src.plugins.config import BotConfig
from src.plugins.utils import is_calling_me
```

## Configuration Management

### Structure
- **File**: `config.json` in project root
- **Format**: Per-bot configuration with fallback to "default" section
- **Bot IDs**: Configuration sections keyed by `bot.self_id`

### Key Configuration Keys
- `openai_api_endpoint`: API endpoint URL
- `openai_api_keys`: List of API keys for load balancing
- `openai_model`: Model name (e.g., "free:QwQ-32B")
- `openai_prompt`: System prompt for AI conversations
- `openai_max_history`: Maximum conversation history length
- `like_times`: Number of likes to send
- `like_users`: List of users to auto-like
- `like_groups`: List of groups for auto-like
- `ban_msg_list`: Banned message patterns per group

## Development Patterns

### Plugin Structure
Each plugin follows this pattern:
```python
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from src.plugins.config import BotConfig
from src.plugins.utils import is_calling_me

# Define handlers
handler = on_command("command", rule=is_calling_me)

@handler.handle()
async def handle_function(bot: Bot, event: GroupMessageEvent):
    config = BotConfig(bot)
    # Plugin logic here
```

### Message Handling
- Use `is_calling_me` rule for bot-specific commands
- Access configuration through `BotConfig(bot)`
- Generate reply messages with `get_basemsg(event)`
- Handle errors gracefully with try/catch blocks

### File Operations
- Use atomic file operations for configuration updates
- Implement backup systems for critical data (see HistoryManager)
- Handle file corruption with recovery mechanisms

## Dependencies

### Core Dependencies (from pyproject.toml)
- `nonebot2` - Main bot framework
- `nonebot-adapter-onebot` - OneBot V11 adapter
- `nonebot-plugin-alconna` - Command parsing

### Additional Dependencies (inferred from code)
- `openai` - OpenAI API client
- `selenium` - Web automation for music downloads
- Standard library: `json`, `asyncio`, `pathlib`, `tempfile`, `shutil`