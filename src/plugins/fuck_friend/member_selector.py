from .database import is_user_unconscious

def filter_suitable_members(member_list, self_id):
    """筛选合适的群成员（排除自己）"""
    return [
        member for member in member_list
        if member['user_id'] != self_id
    ]

def filter_conscious_members(member_list, group_id):
    """筛选清醒的群成员"""
    conscious_members = []
    for member in member_list:
        if not is_user_unconscious(member['user_id'], group_id):
            conscious_members.append(member)
    return conscious_members
