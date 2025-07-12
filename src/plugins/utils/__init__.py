from nonebot.adapters.onebot.v11 import MessageSegment, Message, GroupMessageEvent
from nonebot.log import logger

def get_basemsg(event: GroupMessageEvent) -> Message:
    # basemsg = Message(f"[CQ:reply,id={event.message_id}][CQ:at,qq={event.user_id}]\n")
    basemsg = Message(f"[CQ:reply,id={event.message_id}][CQ:at,qq={event.user_id}]")
    logger.debug("basemsg generated: " + str(basemsg))
    return basemsg

async def is_calling_me(event: GroupMessageEvent) -> bool:
    return (not event.message.has("at")) or (MessageSegment.at(user_id=event.user_id) in event.get_message())