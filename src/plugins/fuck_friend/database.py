import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

db_path = Path('src/plugins/fuck_friend/fuck_friend.db')

def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 被草记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuck_records (
            user_id INTEGER,
            group_id INTEGER,
            total_fucked INTEGER DEFAULT 0,
            today_fucked INTEGER DEFAULT 0,
            total_essence REAL DEFAULT 0,
            last_fucked DATE,
            last_fucked_time TIMESTAMP,
            is_unconscious INTEGER DEFAULT 0,
            unconscious_time TIMESTAMP,
            PRIMARY KEY (user_id, group_id)
        )
    ''')
    # 主动草人记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuck_actions (
            action_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            group_id INTEGER,
            target_id INTEGER,
            action_time TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def update_user_record(user_id, group_id, essence_amount):
    """
    更新用户被草的记录
    Returns:
        tuple: (is_first_blood, time_diff_minutes, total_essence, is_now_unconscious)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today = date.today()
    now = datetime.now()
    
    cursor.execute("SELECT * FROM fuck_records WHERE user_id=? AND group_id=?", (user_id, group_id))
    user_record = cursor.fetchone()
    
    is_first_blood = False
    time_diff_minutes = 0.0
    is_now_unconscious = False

    if user_record:
        last_fucked_date_str = user_record[5]
        last_fucked_time_str = user_record[6]
        today_fucked_db = user_record[3]
        
        if last_fucked_date_str != str(today):
            today_fucked = 0
            is_first_blood = True
        elif today_fucked_db == 0:
            is_first_blood = True
        else:
            today_fucked = today_fucked_db

        if last_fucked_time_str:
            last_fucked_time = datetime.fromisoformat(last_fucked_time_str)
            time_diff = now - last_fucked_time
            time_diff_minutes = round(time_diff.total_seconds() / 60, 2)

        total_fucked = user_record[2] + 1
        today_fucked += 1
        total_essence = user_record[4] + essence_amount

        if today_fucked >= 10:
            is_now_unconscious = True
            unconscious_time = now.isoformat()
        else:
            unconscious_time = user_record[8] # Keep existing unconscious time if not newly unconscious
        
        cursor.execute('''
            UPDATE fuck_records 
            SET total_fucked=?, today_fucked=?, total_essence=?, last_fucked=?, last_fucked_time=?, is_unconscious=?, unconscious_time=?
            WHERE user_id=? AND group_id=?
        ''', (total_fucked, today_fucked, total_essence, str(today), now.isoformat(), is_now_unconscious, unconscious_time, user_id, group_id))
    else:
        is_first_blood = True
        total_essence = essence_amount
        cursor.execute('''
            INSERT INTO fuck_records (user_id, group_id, total_fucked, today_fucked, total_essence, last_fucked, last_fucked_time)
            VALUES (?, ?, 1, 1, ?, ?, ?)
        ''', (user_id, group_id, essence_amount, str(today), now.isoformat()))

    conn.commit()
    conn.close()
    
    return is_first_blood, time_diff_minutes, total_essence, is_now_unconscious

def record_fuck_action(sender_id, group_id, target_id):
    """记录一次主动草人行为"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute('''
        INSERT INTO fuck_actions (sender_id, group_id, target_id, action_time)
        VALUES (?, ?, ?, ?)
    ''', (sender_id, group_id, target_id, now.isoformat()))
    conn.commit()
    conn.close()

def get_sender_stats(sender_id, group_id):
    """获取发送者今天主动草人的次数"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today_str = date.today().isoformat()
    
    cursor.execute('''
        SELECT COUNT(*) 
        FROM fuck_actions 
        WHERE sender_id=? AND group_id=? AND date(action_time) = ?
    ''', (sender_id, group_id, today_str))
    
    result = cursor.fetchone()
    conn.close()
    
    return {'today_fucked_count': result[0] if result else 0}

def is_user_unconscious(user_id, group_id):
    """检查用户是否处于昏迷状态，如果昏迷时间已到则自动唤醒"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT is_unconscious, unconscious_time FROM fuck_records WHERE user_id=? AND group_id=?", (user_id, group_id))
    result = cursor.fetchone()
    
    if result and result[0]:
        unconscious_time = datetime.fromisoformat(result[1])
        if datetime.now() < unconscious_time + timedelta(hours=6):
            conn.close()
            return True
        else:
            cursor.execute("UPDATE fuck_records SET is_unconscious=0, unconscious_time=NULL, today_fucked=0 WHERE user_id=? AND group_id=?", (user_id, group_id))
            conn.commit()
            conn.close()
            return False
            
    conn.close()
    return False
