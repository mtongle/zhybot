import re

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER, GROUP_MEMBER, GroupMessageEvent, Bot, Message, \
    MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_message

from src.plugins.config import _get_config, _set_config, BotConfig
from src.plugins.utils import get_basemsg

ban = on_command("ban", priority=50, permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER)

@ban.handle()
async def handle_ban(bot: Bot, event: GroupMessageEvent):
    config = BotConfig(bot)
    # ban_msg_list = _get_config(self_id=bot.self_id, key='ban_msg_list')
    ban_msg_list = config.get("ban_msg_list")
    reply_id = re.search(pattern=r"\[reply:id=(\d)]", string=event.raw_message).group(1)
    ban_msg = await bot.get_msg(message_id=reply_id)

    if ban_msg not in ban_msg_list:
        ban_msg_list.append(ban_msg)
    # _set_config(self_id=bot.self_id, ban_msg_list=ban_msg_list)
    config.set("ban_msg_list", ban_msg_list)
    await ban.finish(
        Message(get_basemsg(event).append(
            MessageSegment.text("成功将此消息列入自动处决列表")
        )),
    )
    # logger.debug("BAN received: " + str([msg for msg in event.get_message()]))

autoban = on_message(permission=GROUP_MEMBER, priority=1)

@autoban.handle()
async def handle_autoban(bot: Bot, event: GroupMessageEvent):
    config = BotConfig(bot)
    # group_ban_msg_list = _get_config(self_id=bot.self_id, key='ban_msg_list').get(event.group_id) or []
    group_ban_msg_list = config.get("ban_msg_list").get(event.group_id) or []
    msg_list = event.message
    if [msg_segment for msg_segment in msg_list if msg_segment in group_ban_msg_list]:
        await bot.delete_msg(message_id=event.message_id)
        await bot.set_group_kick(group_id=event.group_id, user_id=event.user_id)
        await autoban.finish(
            Message(get_basemsg(event).append(
                MessageSegment.text("该用户触犯了管理员设置的违禁消息列表，被自动处决"),
            )),
        )