import subprocess

from arclet.alconna import Alconna
from nonebot import require, logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from src.plugins.utils import get_basemsg

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import on_alconna, Query, Args

run = on_alconna(
    Alconna(
        "run",
        Args["command", str],
    ),
    permission=SUPERUSER,
    priority=50,
    # rule=to_me(),
)

password = "tonglebot"

@run.handle()
async def handle_run(event: GroupMessageEvent, query: Query[str] = Query("command", "test")):
    user_command = query.result
    command = f"""sudo -u botexec {user_command}"""

    task = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    message = get_basemsg(event)
    text = ""
    if (stdout := task.stdout) and (output := stdout.read().decode()):
        text += "Stdout:\n" + output + "\n----------------\n"
    if (stderr := task.stderr) and (output := stderr.read().decode()):
        text += "Stderr:\n" + output

    while text.endswith("-") or text.endswith("\n"):
        text = text[:-1]
    # logger.debug(text)

    await run.finish(message=message.append(MessageSegment.text(text)))