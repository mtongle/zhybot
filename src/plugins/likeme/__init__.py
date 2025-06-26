import asyncio
import re

from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, MessageEvent
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command, on_regex
from nonebot.log import logger
from nonebot.rule import to_me

from src.plugins.config import _get_config, _set_config, BotConfig

from nonebot import require, get_bots

from src.plugins.utils import get_basemsg, is_calling_me

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler


# like_me = on_command("赞我")
#
# @like_me.handle()
# async def handle_like_me(bot: Bot, event: GroupMessageEvent):
#     user_id = int(event.get_user_id())
#     message_id = event.message_id
#     like_times = get_config(bot.self_id, "like_times")["like_times"]
#     lts_backup = like_times
#
#     while True:
#         if like_times >= 10:
#             await bot.send_like(user_id=user_id, times=10)
#             like_times -= 10
#         else:
#             await bot.send_like(user_id=user_id, times=like_times)
#             break
#         await asyncio.sleep(1.0)
#
#     await like_me.finish(Message(f"[CQ:reply,id={message_id}][CQ:at,qq={user_id}]\n已经赞了{lts_backup}次哦！\n请自行查看是否完成！\n如赞失败可能是达到上限"))

like_me = on_regex(r"^.{1,2}我$", flags=re.IGNORECASE, priority=50, rule=is_calling_me, block=True)

async def send_like(bot: Bot, user_id, like_times: int):
    while like_times >= 10:
        await bot.send_like(user_id=user_id, times=10)
        like_times -= 10
        await asyncio.sleep(0.5)
    if like_times > 0:
        await bot.send_like(user_id=user_id, times=like_times)

@like_me.handle()
async def handle_like_me(bot: Bot, event: GroupMessageEvent):
    user_id = int(event.get_user_id())
    message = event.get_message().extract_plain_text()
    command = re.findall(r"(.{1,2})我", string=message)[0]
    message_id = event.message_id
    config = BotConfig(bot)
    # like_times = _get_config(bot.self_id, "like_times")
    like_times = config.get("like_times")
    lts_backup = like_times

    await send_like(bot, user_id, like_times)

    await like_me.finish(
        Message(
            f"[CQ:reply,id={message_id}][CQ:at,qq={user_id}]\n已经{command}了{lts_backup}次哦！\n请自行查看是否完成！\n如{command}失败可能是达到上限"
        )
    )


set_like_times = on_command("设置赞次数", permission=SUPERUSER, priority=50, rule=is_calling_me, block=True)

@set_like_times.handle()
async def handle_set_like_times(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = int(event.get_user_id())
    message_id = event.message_id
    config = BotConfig(bot)
    try:
        like_times = int(args.extract_plain_text())
    except ValueError:
        await set_like_times.finish(Message(f"[CQ:reply,id={message_id}][CQ:at,qq={user_id}]\n无效的值！]"))

    # result = _set_config(bot.self_id, like_times=like_times)
    config.set(key="like_times", value=like_times)

    await set_like_times.finish(
        Message(
            f"[CQ:reply,id={message_id}][CQ:at,qq={user_id}]\n已经成功将一次赞的次数设置为{like_times}！"
        )
    )


switch_daily_like = on_command("定时赞", priority=50, rule=is_calling_me, block=True)

@switch_daily_like.handle()
async def handle_switch_daily_like(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    basemsg = get_basemsg(event)

    self_id = bot.self_id
    user_id = event.user_id
    group_id = event.group_id
    config = BotConfig(bot)
    # like_users: list = _get_config(self_id, "like_users")
    like_users = config.get("like_users")

    action = args.extract_plain_text()

    ON = ["开", "开启", "打开", "启用"]
    OFF = ["关", "关闭", "关上", "停用"]

    user_config = {
        "user_id": user_id,
        "group_id": group_id,
    }

    if action in ON:
        if finded_dict := next(
        (user_dict for user_dict in like_users
         if user_dict['user_id'] == user_id),None):  # 找不到时返回None
            like_users.remove(finded_dict)
        like_users.append(user_config)
        # _set_config(self_id, like_users=like_users)
        config.set(key="like_users", value=like_users)
        await switch_daily_like.finish(basemsg + [
            MessageSegment.text("成功开启每日5点定时赞！\n情况将汇报在群聊"+str(group_id))
        ])
    elif action in OFF:
        like_users.remove(user_config)
        # _set_config(self_id, like_groups=like_users)
        config.set(key="like_users", value=like_users)
        await switch_daily_like.finish(basemsg + [
            MessageSegment.text("成功关闭每日定时赞！")
        ])
    else:
        await switch_daily_like.finish(basemsg+[
            MessageSegment.text("不支持的操作："+action)
        ])


switch_group_daily_like = on_command("群定时赞", priority=50, rule=is_calling_me, block=True, permission=SUPERUSER)


@switch_group_daily_like.handle()
async def handle_switch_group_daily_like(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    basemsg = get_basemsg(event)

    self_id = bot.self_id
    # user_id = event.user_id
    group_id = event.group_id
    config = BotConfig(bot)
    # like_groups: list[int] = _get_config(self_id, "like_groups")
    like_groups = config.get("like_groups")

    action = args.extract_plain_text()

    ON = ["开", "开启", "打开", "启用"]
    OFF = ["关", "关闭", "关上", "停用"]

    if action in ON:
        if finded_group := next(
                (group for group in like_groups
                 if group == group_id), None):  # 找不到时返回None
            like_groups.remove(finded_group)
        like_groups.append(group_id)
        # _set_config(self_id, like_groups=like_groups)
        config.set(key="like_groups", value=like_groups)
        await switch_daily_like.finish(basemsg + [
            MessageSegment.text("成功开启每日5点全群成员定时赞在群聊" + str(group_id) + "!!!")
        ])
    elif action in OFF:
        like_groups.remove(group_id)
        # _set_config(self_id, like_groups=like_groups)
        config.set(key="like_groups", value=like_groups)
        await switch_daily_like.finish(basemsg + [
            MessageSegment.text("成功关闭每日全群成员定时赞！")
        ])
    else:
        await switch_daily_like.finish(basemsg + [
            MessageSegment.text("不支持的操作：" + action)
        ])

async def like_users(bot: Bot, like_times: int, user_ids: list):
    succeeded = []

    for user in user_ids:
        try:
            # operate sending like
            await send_like(bot, user, like_times)
            succeeded.append(user) # record succeeded
        except Exception:
            pass # if an error happened, don't record it and pass

    return succeeded

async def report_status(bot: Bot, group_id: int, user_ids: list):
    message = Message()
    if len(user_ids) <= 10:
        for user_id in user_ids:
            message.append(MessageSegment.at(user_id))
        message.append(MessageSegment.text("\n今天已经自动给你们赞过50下啦！记得回哦！"))
        await bot.send_group_msg(group_id=group_id, message=message)
    else:
        forward_message = [
        {
            "type": "node",
            "data": {
                "user_id": bot.self_id,
                "nickname": "SUCCESS",
                "content": [
                    MessageSegment.text(f"Successfully liked {len(user_ids)} users below."),
                ],
            }
        },
        {
            "type": "node",
            "data": {
                "user_id": bot.self_id,
                "nickname": "INFO",
                "content": [],
            }
        },
    ]
        count = 1
        node = 1
        for user_id in user_ids:
            count += 1
            if count > 30:
                node += 1
                count = 1
                forward_message.append({
                    "type": "node",
                    "data": {
                        "user_id": bot.self_id,
                        "nickname": "INFO",
                        "content": [],
                    }
                })

            forward_message[node]["data"]["content"].extend([MessageSegment.at(user_id), MessageSegment.text("\n")])

        await bot.send_group_msg(group_id=group_id, message=Message(f"今天已经自动给你们{len(user_ids)}成员赞过50下啦！记得回哦！"))
        await bot.send_group_forward_msg(group_id=group_id, messages=forward_message)


test = on_command("dailylike-test", priority=50, rule=to_me(), block=True)

async def bot_daily_like(self_id: str, bot: Bot):
    logger.debug("Start dailylike on bot " + self_id)

    # get configs
    config = BotConfig(bot)
    # like_times: int = _get_config(self_id, "like_times")
    # like_users_info: list[dict[str, int]] = _get_config(self_id, "like_users")
    # like_groups: list[int] = _get_config(self_id, "like_groups")
    like_times: int = config.get("like_times")
    like_users_info: list[dict[str, int]] = config.get("like_users")
    like_groups: list[int] = config.get("like_groups")

    logger.debug("Read config")

    # first operate liking groups
    result = {}
    logger.debug("Start liking groups")
    for group in like_groups:
        member_list = await bot.get_group_member_list(group_id=group)
        user_id_list = [user["user_id"] for user in member_list]
        succeeded = await like_users(bot, like_times, user_id_list)
        result[group] = succeeded
    logger.debug("Done liking groups")

    logger.debug("report groups status")
    for (group, succeeded) in result.items():
        await report_status(bot, group, succeeded)
    logger.debug("Done report groups status")

    # then operate liking users
    succeeded = await like_users(bot, like_times,
                                 [user["user_id"] for user in like_users_info if user["group_id"] not in like_groups])
    logger.debug("Done liking users")

    to_report: dict[int, list[int]] = {}
    for user in like_users_info:
        to_report.setdefault(user["group_id"], []).append(user["user_id"])

    for (group, succeeded) in to_report.items():
        if group not in like_groups:
            await report_status(bot, group, succeeded)
    logger.debug("Done reporting users status")

    logger.debug("Finished dailylike on bot " + self_id)

@test.handle()
@scheduler.scheduled_job("cron", id="daily_like", day="*", hour="5")
async def daily_like():
    logger.debug("Starting daily_like......")
    bots = get_bots()
    logger.debug(bots.keys())

    tasks = [bot_daily_like(self_id=self_id, bot=bot) for (self_id, bot) in bots.items()]
    await asyncio.gather(*tasks)

    logger.success("Finished dailylike on all bots!")
