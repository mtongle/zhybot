from nonebot import require
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from arclet.alconna import Alconna, Subcommand, Args, Option, Arparma
from asyncio import sleep

from src.plugins.utils import is_calling_me, get_basemsg

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import on_alconna

alc = Alconna(
    "bomb",
    Option("-m|--message", Args["message", str], default="BOMB!!!"),
    Option("-t|--times", Args["times", str], default=10),
    Option("-s|--speed", Args["speed", str], default=30),
    Option("--enable-dangerous-mode")
)

bomb = on_alconna(alc, priority=50, auto_send_output=True, rule=is_calling_me,)

@bomb.handle()
async def handle_bomb(event: GroupMessageEvent, result: Arparma):
    basemsg = get_basemsg(event)
    try:
        speed: int = int(result.query("speed"))
    except Exception:
        await bomb.finish(basemsg+[
                MessageSegment.text("错误的选项参数：speed")
            ])
    if speed >= 120:
        if result.find("--enable-dangerous-mode"):
            await bomb.finish(basemsg+[
                MessageSegment.text("你的速度过快（>=60）！\n如坚持使用此速度，请加入选项“危险模式”！")
            ])
        else:
            await bomb.send(basemsg+[
                MessageSegment.text("警告：危险模式开启！")
            ])

    try:
        times: int = result.query("times")
    except Exception:
        await bomb.finish(basemsg + [
            MessageSegment.text("错误的选项参数：times")
        ])
    message: str = result.query("message")

    await bomb.send(basemsg+[
        MessageSegment.text(f"开始消息轰炸！\n当前每分钟消息数：{speed}\n轰炸次数：{times}\n消息：{message}")
    ])

    await sleep(2.0)

    delay: float = 60/speed
    for _ in range(times):
        await bomb.send(message)
        await sleep(delay)

    await sleep(2.0)
    await bomb.finish(basemsg+[
        MessageSegment.text("轰炸完成！")
    ])
