import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message

from .database import (
    init_database, 
    update_user_record, 
    get_sender_stats, 
    is_user_unconscious,
    record_fuck_action
)
from .messages import (
    get_message, 
    get_no_suitable_member_message, 
    get_unconscious_message, 
    get_already_unconscious_message,
    get_no_conscious_member_message
)
from .member_selector import filter_suitable_members, filter_conscious_members
from src.plugins.utils import get_basemsg

fuck_friend = on_command("草群友", priority=50)

@fuck_friend.handle()
async def handle_fuck_friend(bot: Bot, event: GroupMessageEvent):
    init_database()
    
    group_id = event.group_id
    sender_id = event.user_id
    sender_info = await bot.get_group_member_info(group_id=group_id, user_id=sender_id)
    sender_name = sender_info.get('card') or sender_info.get('nickname', '')

    target_member = None
    # 检查@和回复
    if event.message:
        for seg in event.message:
            if seg.type == "at":
                target_id = int(seg.data["qq"])
                if is_user_unconscious(target_id, group_id):
                    info = await bot.get_group_member_info(group_id=group_id, user_id=target_id)
                    name = info.get('card') or info.get('nickname', '')
                    await fuck_friend.finish(get_already_unconscious_message(name))
                
                try:
                    target_member_info = await bot.get_group_member_info(group_id=group_id, user_id=target_id)
                    target_member = {'user_id': target_id, 'nickname': target_member_info.get('card') or target_member_info.get('nickname', '')}
                except: pass
                break
    if not target_member and event.reply:
        target_id = event.reply.sender.user_id
        if is_user_unconscious(target_id, group_id):
            info = await bot.get_group_member_info(group_id=group_id, user_id=target_id)
            name = info.get('card') or info.get('nickname', '')
            await fuck_friend.finish(get_already_unconscious_message(name))
        try:
            target_member_info = await bot.get_group_member_info(group_id=group_id, user_id=target_id)
            target_member = {'user_id': target_id, 'nickname': target_member_info.get('card') or target_member_info.get('nickname', '')}
        except: pass

    # 随机选择
    if not target_member:
        member_list = await bot.get_group_member_list(group_id=group_id)
        suitable_members = filter_suitable_members(member_list, event.self_id)
        
        if not suitable_members:
            await fuck_friend.finish(get_no_suitable_member_message())
        
        conscious_members = filter_conscious_members(suitable_members, group_id)
        if not conscious_members:
            await fuck_friend.finish(get_no_conscious_member_message())

        target_member = random.choice(conscious_members)
    
    target_id = target_member.get('user_id')
    target_name = target_member.get('nickname')

    # 记录主动行为
    record_fuck_action(sender_id, group_id, target_id)

    essence_amount = round(random.uniform(5.0, 20.0), 2)
    
    is_first_blood, time_diff, total_essence, is_now_unconscious = update_user_record(target_id, group_id, essence_amount)
    
    sender_stats = get_sender_stats(sender_id, group_id)
    today_fucked_count = sender_stats.get('today_fucked_count', 0)

    target_avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={target_id}&s=640"
    
    # 获取消息，现在是Message对象
    message_obj = get_message(
        target_id, target_name, is_first_blood, time_diff,
        essence_amount, total_essence, today_fucked_count, sender_name
    )
    
    base_msg = get_basemsg(event)
    await fuck_friend.send(base_msg + message_obj + MessageSegment.image(target_avatar_url))

    if is_now_unconscious:
        await fuck_friend.finish(get_unconscious_message(target_name))
