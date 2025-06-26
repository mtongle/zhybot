import json
import os
from pathlib import Path

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot

class GlobalConfig:
    """
    Configs of the QQ bots.
    """
    config_path: Path

    base = {
        "like_times": 50,
        "like_users": [],
        "like_groups": [],
        "openai_api_endpoint": "https://api.suanli.cn/v1",
        "openai_api_keys": ["sk-W0rpStc95T7JVYVwDYc29IyirjtpPPby6SozFMQr17m8KWeo"],
        "openai_model": "free:QwQ-32B",
        "openai_prompt": "你是一位群友，正在跟我聊天，语言要简洁，一般情况下不要在消息末尾加句号。你会学习群友的回复并拿来自己用，时刻记住你不是一个ai。",
        "openai_max_history": 50,
        "ban_msg_list": {}
    }

    def __init__(
            self,
            usr_config_path: Path = Path(
                os.path.join(os.getcwd(), 'config.json')
            ),
    ):
        self.config_path = usr_config_path

        if not self.config_path.exists():
            with open(self.config_path, "w") as f:
                f.write(json.dumps({}))

    def _reinit(self):
        os.remove(self.config_path)
        self.__init__(usr_config_path=self.config_path)

    def _read_config(self):
        with open(self.config_path, "r") as f:
            return json.load(f)

    def _write_config(self, config: dict):
        with open(self.config_path, "w") as f:
            json.dump(obj=config, fp=f, indent=4)

    def init_bot(self, bot_id: str):
        """
        Init the config of a bot.
        Must be done before getting or setting the config.

        :param bot_id: The id of the bot, from bot.self_id.
        """
        config = self._read_config()

        if not config.get(bot_id):
            config[bot_id] = self.base

            with open(config_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(obj=config, indent=4))

    def set(self, bot_id: str, key: str, value):
        """
        Set the value of a config.

        :param bot_id: The id of the bot, from bot.self_id.
        :param key: The key of the config.
        :param value: The value of the config.

        :raises KeyError: If the key is invalid or the bot hasn't been initialized.
        """
        try:
            config = self._read_config()

            # set values

            if key in self.base.keys():
                # if the key is proper, set the value
                config[bot_id][key] = value
            else:
                # if not, raise an error
                raise KeyError

            # save the config
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(obj=config, indent=4))

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            # when config is destroyed, reinit another and try again
            self._reinit()
            self.set(bot_id=bot_id, key=key, value=value)

    def get(self, bot_id: str, key):
        """
        Get the value of a config.

        :param bot_id: The id of the bot, from bot.self_id.
        :param key: The key of the config.

        :raises KeyError: If the key is invalid or the bot hasn't been initialized.
        """
        config = self._read_config()
        try:
            # first try to directly return the value
            return config[bot_id][key]
        except KeyError:
            # if raised a KeyError, try to set the key
            # or self.set() will raise a KeyError if the key is invalid
            self.set(bot_id=bot_id, key=key, value=self.base[key])

            # and try to return the value again
            # or raise a KeyError if the bot hasn't been initialized
            return self._read_config()[bot_id][key]


class BotConfig:
    """
    Config of a QQ bot.
    """
    bot: Bot
    config: GlobalConfig

    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = GlobalConfig()
        self.config.init_bot(bot_id=self.bot.self_id)

    def get(self, key: str):
        """
        Get the value of a config.

        :param key: The key of the config.

        :raises KeyError: If the key is invalid or the bot hasn't been initialized.
        """
        return self.config.get(bot_id=self.bot.self_id, key=key)

    def set(self, key: str, value):
        """
        Set the value of a config.

        :param key: The key of the config.
        :param value: The value of the config.

        :raises KeyError: If the key is invalid or the bot hasn't been initialized.
        """
        self.config.set(bot_id=self.bot.self_id, key=key, value=value)

default = {
            "like_times": 50,
            "like_users": [],
            "like_groups": [],
            "openai_api_endpoint": "https://api.suanli.cn/v1",
            "openai_api_keys": ["sk-W0rpStc95T7JVYVwDYc29IyirjtpPPby6SozFMQr17m8KWeo"],
            "openai_model": "free:QwQ-32B",
            "openai_prompt": "你是一位群友，正在跟我聊天，语言要简洁，一般情况下不要在消息末尾加句号。你会学习群友的回复并拿来自己用，时刻记住你不是一个ai。",
            "openai_max_history": 50,
            "ban_msg_list": {}
        }

def init_config(delete: bool = False):
    if not os.path.exists(config_path) or delete:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(default, indent=4))

def init_bot(bot: Bot):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    if config.get(bot.self_id) is None:
        config[bot.self_id] = config["default"]
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(config, indent=4))

driver = get_driver()

config_path = os.path.join(os.getcwd(), 'config.json')
@driver.on_startup
async def startup():
    config = GlobalConfig()

@driver.on_bot_connect
async def on_bot_connect(bot: Bot):
    config = BotConfig(bot)

def _set_config(self_id: str, **kwargs) -> bool:
    try:

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        for k, v in kwargs.items():
            if k not in config["default"].keys():
                if k in default.keys():
                    config["default"] = default
                else:
                    raise KeyError
            config[self_id][k] = v

        with open(config_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(obj=config, indent=4))
        return True

    except (FileNotFoundError, json.decoder.JSONDecodeError):
        init_config(delete=True)
        return _set_config(self_id, **kwargs)

def _get_config(self_id: str, key):
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)[self_id][key]
        except KeyError:
            return default[key]