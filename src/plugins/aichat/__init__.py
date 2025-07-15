import json
import os
import random
import tempfile
import shutil
import asyncio
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta

from nonebot import on_message, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command
from nonebot.rule import to_me
from openai import OpenAI, OpenAIError

from src.plugins.config import BotConfig
from src.plugins.utils import is_calling_me

# AI chat handler
ai_chat = on_message(priority=100, rule=to_me())

class HistoryManager:
    """改进的聊天历史管理器"""
    
    def __init__(self, history_dir: str = "chat_history"):
        self.history_dir = Path(history_dir)
        self.history_file = self.history_dir / "history.json"
        self.backup_dir = self.history_dir / "backups"
        self.lock = asyncio.Lock()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录结构存在"""
        self.history_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        if not self.history_file.exists():
            self._atomic_write({})
    
    def _atomic_write(self, data: dict):
        """原子性写入文件"""
        try:
            # 写入临时文件
            with tempfile.NamedTemporaryFile(
                mode='w', 
                encoding='utf-8', 
                dir=self.history_dir,
                delete=False,
                suffix='.tmp'
            ) as tmp_file:
                json.dump(data, tmp_file, ensure_ascii=False, indent=2)
                tmp_path = tmp_file.name
            
            # 原子性替换
            shutil.move(tmp_path, self.history_file)
            logger.debug(f"历史文件已原子性更新: {self.history_file}")
            
        except Exception as e:
            logger.error(f"原子性写入失败: {e}")
            # 清理临时文件
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
    
    def _load_history(self) -> dict:
        """安全加载历史文件"""
        if not self.history_file.exists():
            return {}
        
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"历史文件损坏: {e}")
            # 尝试从备份恢复
            if backup_data := self._try_restore_from_backup():
                logger.info("从备份恢复历史数据")
                return backup_data
            logger.warning("无法恢复历史数据，返回空历史")
            return {}
        except Exception as e:
            logger.error(f"读取历史文件失败: {e}")
            return {}
    
    def _try_restore_from_backup(self) -> dict:
        """尝试从备份恢复"""
        backup_files = sorted(
            self.backup_dir.glob("history_backup_*.json"),
            key=os.path.getmtime,
            reverse=True
        )
        
        for backup_file in backup_files[:3]:  # 尝试最近的3个备份
            try:
                with open(backup_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"从备份文件恢复: {backup_file}")
                    return data
            except Exception as e:
                logger.warning(f"备份文件 {backup_file} 也损坏: {e}")
                continue
        
        return {}
    
    def _create_backup(self):
        """创建备份文件"""
        try:
            if not self.history_file.exists():
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"history_backup_{timestamp}.json"
            
            shutil.copy2(self.history_file, backup_path)
            logger.debug(f"创建备份: {backup_path}")
            
            # 清理旧备份 (保留最近10个)
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.warning(f"创建备份失败: {e}")
    
    def _cleanup_old_backups(self):
        """清理旧备份文件"""
        try:
            backup_files = sorted(
                self.backup_dir.glob("history_backup_*.json"),
                key=os.path.getmtime,
                reverse=True
            )
            
            # 删除超过10个的旧备份
            for old_backup in backup_files[10:]:
                old_backup.unlink()
                logger.debug(f"删除旧备份: {old_backup}")
                
        except Exception as e:
            logger.warning(f"清理旧备份失败: {e}")
    
    def _trim_history(self, history: List[Dict], max_size: int) -> List[Dict]:
        """智能修剪历史记录"""
        if len(history) <= max_size:
            return history
        
        # 保留最近的对话，但确保成对出现
        trimmed = history[-max_size:]
        
        # 确保第一条是user消息，保持对话完整性
        while trimmed and trimmed[0].get("role") != "user":
            trimmed.pop(0)
        
        logger.debug(f"历史记录已修剪: {len(history)} -> {len(trimmed)}")
        return trimmed
    
    async def get_history(self, bot_id: str) -> List[Dict]:
        """异步获取聊天历史"""
        async with self.lock:
            all_history = self._load_history()
            history = all_history.get(bot_id, [])
            
            # 验证历史记录格式
            valid_history = []
            for item in history:
                if isinstance(item, dict) and "role" in item and "content" in item:
                    valid_history.append(item)
                else:
                    logger.warning(f"发现无效的历史记录项: {item}")
            
            return valid_history
    
    async def save_history(self, bot_id: str, history: List[Dict]):
        """异步保存聊天历史"""
        async with self.lock:
            # 每次保存前创建备份
            self._create_backup()
            
            all_history = self._load_history()
            all_history[bot_id] = history
            
            # 添加元数据
            all_history["_metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "version": "2.0"
            }
            
            self._atomic_write(all_history)
    
    async def clear_history(self, bot_id: str):
        """异步清理历史记录"""
        async with self.lock:
            self._create_backup()
            
            all_history = self._load_history()
            all_history[bot_id] = []
            
            all_history["_metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "version": "2.0"
            }
            
            self._atomic_write(all_history)
    
    async def get_statistics(self) -> dict:
        """获取历史记录统计信息"""
        async with self.lock:
            all_history = self._load_history()
            stats = {
                "total_bots": len([k for k in all_history.keys() if not k.startswith("_")]),
                "total_messages": 0,
                "file_size": self.history_file.stat().st_size if self.history_file.exists() else 0,
                "last_backup": None
            }
            
            for bot_id, history in all_history.items():
                if not bot_id.startswith("_") and isinstance(history, list):
                    stats["total_messages"] += len(history)
            
            # 获取最新备份时间
            backup_files = list(self.backup_dir.glob("history_backup_*.json"))
            if backup_files:
                latest_backup = max(backup_files, key=os.path.getmtime)
                stats["last_backup"] = datetime.fromtimestamp(
                    latest_backup.stat().st_mtime
                ).isoformat()
            
            return stats

# 初始化历史管理器
history_manager = HistoryManager()

def clear_whitespace(content: str) -> str:
    """移除开头的空白字符"""
    while content.startswith(("\n", " ")):
        content = content[1:]
    return content

@ai_chat.handle()
async def handle_ai_chat(bot: Bot, event: GroupMessageEvent):
    """处理AI聊天"""
    config = BotConfig(bot)
    bot_id = bot.self_id
    
    # 获取消息内容
    message = event.get_message().extract_plain_text()
    if not message:
        await ai_chat.finish()
    
    # 获取配置
    api_keys = config.get("openai_api_keys")
    if not api_keys:
        await ai_chat.finish("❌ 未配置API密钥")
    
    # 创建OpenAI客户端
    try:
        client = OpenAI(
            base_url=config.get("openai_api_endpoint"),
            api_key=random.choice(api_keys)
        )
    except Exception as e:
        await ai_chat.finish(f"❌ 初始化AI客户端失败: {e}")
    
    # 获取历史记录
    history = await history_manager.get_history(bot_id)
    max_history = config.get("openai_max_history")
    if len(history) >= max_history:
        history = history[-max_history:]
    
    # 构建消息
    messages = [
        {"role": "system", "content": config.get("openai_prompt")},
        *history,
        {"role": "user", "content": message}
    ]
    
    try:
        # 发送API请求
        stream = client.chat.completions.create(
            model=config.get("openai_model"),
            messages=messages,
            stream=True,
            temperature=1.3,
        )
        
        # 解析响应
        thinking = ""
        response = ""
        mode = "response"
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                word = chunk.choices[0].delta.content
                
                if word == "<think>":
                    mode = "thinking"
                    thinking = ""
                    logger.debug("开始思考...")
                elif word == "</think>":
                    mode = "response"
                    logger.debug("思考结束")
                else:
                    if mode == "thinking":
                        thinking += word
                    else:
                        response += word
        
        # 清理空白字符
        thinking = clear_whitespace(thinking)
        response = clear_whitespace(response)
        
        # 构建完整回复用于保存历史
        if thinking:
            full_response = f"<think>\n{thinking}\n</think>\n{response}"
        else:
            full_response = response
        
        # 更新历史记录
        history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": full_response}
        ])
        await history_manager.save_history(bot_id, history)
        
        # 发送回复
        if thinking:
            # 有思考内容时使用转发消息
            await bot.send_group_forward_msg(
                group_id=event.group_id,
                messages=[
                    {
                        "type": "node",
                        "data": {
                            "user_id": bot_id,
                            "nickname": "思考内容",
                            "content": Message([MessageSegment.text(thinking)])
                        }
                    },
                    {
                        "type": "node",
                        "data": {
                            "user_id": bot_id,
                            "nickname": "输出结果", 
                            "content": Message([MessageSegment.text(response)])
                        }
                    }
                ]
            )
        else:
            # 直接回复
            await ai_chat.send(Message([
                MessageSegment.reply(event.message_id),
                MessageSegment.text(response)
            ]))
            
    except OpenAIError as e:
        await ai_chat.finish(f"❌ 生成回答时出错了！\n原因：{e}")
    except Exception as e:
        logger.error(f"AI聊天处理错误: {e}")
        await ai_chat.finish("❌ 处理消息时发生错误，请稍后重试")

# 更改模型命令
change_model = on_command("更改模型为", permission=SUPERUSER, priority=50, rule=is_calling_me, block=True)

@change_model.handle()
async def handle_change_model(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    config = BotConfig(bot)
    
    if model := args.extract_plain_text():
        config.set("openai_model", model)
        await change_model.send(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text(f"\n✅ 已将模型设置为: {model}")
        ]))
    else:
        await change_model.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text("\n❌ 未提供模型名称！")
        ]))

# 更改提示词命令  
change_prompt = on_command("更改提示词为", permission=SUPERUSER, priority=50, rule=is_calling_me, block=True)

@change_prompt.handle()
async def handle_change_prompt(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    config = BotConfig(bot)
    
    if prompt := args.extract_plain_text():
        config.set("openai_prompt", prompt)
        await change_prompt.send(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text(f"\n✅ 已将提示词设置为: {prompt}")
        ]))
    else:
        await change_prompt.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text("\n❌ 未提供提示词！")
        ]))

# 清理历史记录命令
clear_history_cmd = on_command("清理历史聊天记录", priority=50, rule=is_calling_me, block=True)

@clear_history_cmd.handle()
async def handle_clear_history(bot: Bot, event: GroupMessageEvent):
    try:
        await history_manager.save_history(bot.self_id, [])
        await clear_history_cmd.send(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text("\n✅ 历史聊天记录清理完成！")
        ]))
    except Exception as e:
        await clear_history_cmd.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text(f"\n❌ 清理失败: {e}")
        ]))