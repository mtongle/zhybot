import json
import os
import random

from nonebot import on_message, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command
from nonebot.rule import to_me
from openai import OpenAI, OpenAIError

from ..config import get_config, set_config
from ..likeme import is_calling_me

ai = on_message(priority=100, rule=to_me())

@ai.handle()
async def handle_ai(bot: Bot, event: GroupMessageEvent):
    self_id = bot.self_id
    if message := event.get_message().extract_plain_text():
        pass
    else:
        await ai.finish()
    api_keys = get_config(self_id, "openai_api_keys")
    client = OpenAI(
        base_url=get_config(self_id, "openai_api_endpoint"),
        api_key=random.choice(api_keys),
    )
    history_path = "history.json"
    if not os.path.exists(history_path):
        with open(history_path, "w") as f:
            json.dump(dict({}), f)
    with open(history_path, "r", encoding="utf-8") as f:
        try:
            history_all: dict[str, list] = json.load(f)
            history: list = history_all[self_id]
        except (json.decoder.JSONDecodeError,KeyError):
            history_all: dict[str, list] = {self_id: []}
            history: list = []
    max_history = get_config(self_id, "openai_max_history")
    if len(history) >= max_history:
        history = history[len(history)-max_history:]
    try:
        stream = client.chat.completions.create(
            model=get_config(self_id, "openai_model"),
            messages=[
                {
                   "role": "system",
                    "content": get_config(self_id, "openai_prompt"),
                },
                *history,
                {
                    "role": "user",
                    "content": message,
                }
            ],
            stream=True,
            temperature=1.3,
        )

        think: str = "None"
        resp: str = ""
        mode = "generating"

        for chunk in stream:
            if word := chunk.choices[0].delta.content:
                if word == "<think>":
                    mode = "thinking"
                    think = ""
                    logger.debug("Start thinking...")
                elif word == "</think>":
                    mode = "generating"
                    logger.debug("End of thinking!")
                else:
                    if mode == "thinking":
                        think += word
                    else:
                        resp += word

        def delete_whitespace(content: str):
            white = ("\n", " ")
            if content.startswith(white):
                content = content[1:]
                return delete_whitespace(content)
            else:
                return content

        think = delete_whitespace(think)
        resp = delete_whitespace(think)

    except OpenAIError as e:
        await ai.finish(f"生成回答时出错了！\n原因：{e}")

    if think != "None":
        raw = "<think>\n" + think + "</think>\n" + resp
    else:
        raw = resp
    # raw_content: str = resp.choices[0].message.content
    # logger.debug(raw_content)
    # logger.debug(history)
    history.extend([
        {
            "role": "user",
            "content": message,
        },
        {
            "role": "assistant",
            "content": raw,
        },
    ])
    # logger.debug(history)
    history_all[self_id] = history
    with open(history_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(history_all, indent=4))
    # if raw_content.startswith("<think>"):
    #     logger.debug("Find thinking content!")
    #     if thinking := re.search(r"<think>([.\s]*)</think>", raw_content).group(1):
    #         pass
    #     else:
    #         thinking = "null"
    #     # logger.debug(thinking)
    #     content = re.search(r"</think>(.*)", raw_content).group(1)
    #     # logger.debug(content)
    await bot.send_group_forward_msg(group_id=event.group_id, messages=[
        {
            "type": "node",
            "data": {
                "user_id": self_id,
                "nickname": "思考内容",
                "content": Message([
                    MessageSegment.text(think),
                ])
            },
        },
        {
            "type": "node",
            "data": {
                "user_id": self_id,
                "nickname": "输出结果",
                "content": Message([
                    MessageSegment.text(resp),
                ])
            }
        }
    ])

change_model = on_command("更改模型为", permission=SUPERUSER, priority=50, rule=is_calling_me, block=True)

@change_model.handle()
async def handle_change_model(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if model := args.extract_plain_text():
        set_config(bot.self_id, openai_model=model)
        await change_model.send(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text(f"\n已经将模型设置为{model}!"),
        ]))
    else:
        await change_model.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text("\n未提供模型代号!"),
        ]))

change_model = on_command("更改提示词为", permission=SUPERUSER, priority=50, rule=is_calling_me, block=True)

@change_model.handle()
async def handle_change_model(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if prompt := args.extract_plain_text():
        set_config(bot.self_id, openai_prompt=prompt)
        await change_model.send(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text(f"\n已经将提示词设置为{prompt}!"),
        ]))
    else:
        await change_model.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text("\n未提供提示词!"),
        ]))

clear_history = on_command("清理历史聊天记录", priority=50, rule=is_calling_me, block=True)

@clear_history.handle()
async def handle_clear_history(bot: Bot, event: GroupMessageEvent):
    try:
        with open("history.json", "w+") as f:
            self_id = bot.self_id
            history = json.load(f)
            history[self_id] = []
            f.write(json.dumps(history, indent=4))
    except FileNotFoundError:
        await change_model.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text("\n还没有历史聊天记录哦！"),
        ]))
    except Exception as e:
        await change_model.finish(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.at(event.user_id),
            MessageSegment.text(f"\n未知错误：{e}"),
        ]))
    await change_model.send(Message([
        MessageSegment.reply(event.message_id),
        MessageSegment.at(event.user_id),
        MessageSegment.text("\n历史聊天记录清理完成！"),
    ]))