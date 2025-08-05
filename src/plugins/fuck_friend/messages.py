from nonebot.adapters.onebot.v11 import Message, MessageSegment

def get_message(target_id, target_name, is_first_blood, time_diff, essence_amount, total_essence, today_fucked_count, sender_name):
    """生成最终的输出消息"""
    at_target = MessageSegment.at(target_id)
    
    # 构建消息的第一部分
    if is_first_blood:
        # 第一次提及时使用@
        message = Message(f"恭喜{sender_name}拿到") + at_target + Message("今日一血!\n")
        # 第二次提及时使用文本名称
        message += Message(f"你草了群友{target_name}({target_id})\n")
    else:
        # 只有一次提及，使用@
        message = Message("你草了群友") + at_target + Message("\n")

    # 添加时间差信息
    if time_diff > 0:
        message += Message(f"距离上次被草{time_diff}分钟，\n")
    
    # 添加精华信息
    message += Message(f"注入了{essence_amount:.2f}ml的生命精华\n")
    message += Message(f"ta一共被注入了{total_essence:.2f}ml生命精华\n")
    
    # 添加保留精华信息和今日统计
    message += Message(f"目前保留{total_essence:.2f}ml生命精华\n")
    message += Message(f"你今天草了{today_fucked_count}次群友")
    
    return message

def get_no_suitable_member_message():
    """获取没有合适群成员时的提示消息"""
    return "群里没有可以草的群友哦~"

def get_unconscious_message(target_name):
    """获取昏迷消息"""
    return f"哎呀，{target_name}昏迷了！6个小时后再来吧！"

def get_already_unconscious_message(target_name):
    """获取目标已昏迷的消息"""
    return f"{target_name}已经昏迷了，让他好好休息吧！"

def get_no_conscious_member_message():
    """获取没有清醒成员的消息"""
    return "群里没有清醒的群友可以草了，明天再来吧！"
