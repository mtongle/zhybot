from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupDecreaseNoticeEvent
from nonebot.adapters.onebot.v11.event import GroupIncreaseNoticeEvent
from nonebot.log import logger

welcome = on_notice()

@welcome.handle()
async def handle_welcome(bot: Bot, event: GroupIncreaseNoticeEvent):
    user_id = event.user_id
    user_info = await bot.get_stranger_info(user_id=user_id)
    group_id = event.group_id
    group_info = await bot.get_group_info(group_id=group_id)
    # logger.debug(group_info)

    await welcome.finish(Message([
        MessageSegment.at(user_id),
        MessageSegment.image(user_info["avatar"]),
        MessageSegment.text(f"欢迎加入{group_info["group_name"]}的大家庭🥳🥳🥳!!!"),
    ]))


bye = on_notice()

@bye.handle()
async def handle_bye(bot: Bot, event: GroupDecreaseNoticeEvent):
    user_id = event.user_id
    user_info = await bot.get_stranger_info(user_id=user_id)
    # logger.debug(group_info)

    await bye.finish(Message([
        MessageSegment.at(user_id),
        MessageSegment.image(user_info["avatar"]),
        MessageSegment.text(f"欢迎下次再来光临😭!!!"),
    ]))
