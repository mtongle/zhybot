import json
import os

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot

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
    init_config()

@driver.on_bot_connect
async def on_bot_connect(bot: Bot):
    init_bot(bot)

def set_config(self_id: str, **kwargs) -> bool:
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
        return set_config(self_id, **kwargs)

def get_config(self_id: str, key):
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)[self_id][key]
        except KeyError:
            return default[key]