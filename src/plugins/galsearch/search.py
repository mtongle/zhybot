import json
from typing import no_type_check

import requests

from nonebot import get_plugin_config
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.exception import FinishedException, ActionFailed
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent

from .config import Config

from nonebot import on_command
from nonebot.params import CommandArg

config = get_plugin_config(Config)

search = on_command("gal", priority=5, rule=to_me(), block=True)

def translate_tags(tags: list[str]):
    """
    翻译源的属性词条
    """
    translated_tags: list[str] = []
    for tag in tags:
        translated_tags.append(config.api_tags.get(tag, "未知属性"))
    # logger.debug("Translated origin tags: {}".format(translated_tags))
    return translated_tags


# 建议在函数外或配置加载时执行一次，避免重复计算
# PRECOMPUTED_RECOMMEND = [set(sub) for sub in config.api_recommend]

def is_recommend_api(tags: list[str]) -> bool:
    """
    判断源的所有词条是否匹配推荐的标准
    逻辑：tags 必须包含 recommended_tags 中每一个子列表里的至少一个元素
    """
    # 如果推荐配置本身为空，返回 False
    recommended_tags: list[list[str]] = config.api_recommend
    if not recommended_tags:
        return False

    target_tags = set(tags)

    # 直接对子项进行 set 转换（或使用预处理后的）
    # 利用集合交集的布尔特性
    return all(bool(target_tags & set(sub)) for sub in recommended_tags)

def is_not_recommend_api(tags: list[str]) -> bool:
    """
    判断源的词条是否含有不推荐的词条
    """
    # 如果不推荐配置本身为空，返回 False
    not_recommended_tags: list[str] = config.api_not_recommend
    if not not_recommended_tags:
        return False

    target_tags = set(tags)

    # 直接对子项进行 set 转换（或使用预处理后的）
    # 利用集合交集的布尔特性
    return any(sub in target_tags for sub in not_recommended_tags)

def is_warned_api(tags: list[str]) -> bool:
    """
    判断源的词条是否含有警告的词条
    """
    # 如果不推荐配置本身为空，返回 False
    warned_tags: list[str] = config.api_warned
    if not warned_tags:
        return False

    target_tags = set(tags)

    # 直接对子项进行 set 转换（或使用预处理后的）
    # 利用集合交集的布尔特性
    return any(sub in target_tags for sub in warned_tags)

def get_origin_name(result: dict) -> str:
    """
    从返回的result中生成源的名称
    """
    tags = result.get("tags", [])
    name = result.get("name", "未知源")

    # 判断是否是推荐/不推荐的源
    if is_not_recommend_api(tags):
        return "🔴不推荐：" + name
    elif is_warned_api(tags):
        return "🟠需注意：" + name
    elif is_recommend_api(tags):
        return "🟢推荐：" + name
    else:
        return name


@search.handle()
async def handle_search_gal(
        bot: Bot,
        event: GroupMessageEvent,
        args: Message = CommandArg()
):
    # logger.debug("Search Gal Begin")

    # 获取元数据
    user_id = event.user_id
    message_id = event.message_id
    bot_id = int(bot.self_id)

    # 解码命令
    keyword = args.extract_plain_text().strip()
    if not keyword:
        await search.finish(Message([
            MessageSegment.reply(message_id),
            MessageSegment.at(user_id),
            MessageSegment.text("\n请输入查询关键词！")
        ]))

    await search.send(Message([
        MessageSegment.reply(message_id),
        MessageSegment.at(user_id),
        MessageSegment.text("\n开始查询：" + keyword)
    ]))

    # 发送请求
    resp = requests.post(
        url=config.api_base_url,
        data={"game": keyword},
        stream=True,
        headers={
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "origin": "https://searchgal.top",
            "priority": "u=1, i",
            "referer": "https://searchgal.top/",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}
    )

    # 生成一个源的合并转发消息
    def generate_message(origin_result: dict):
        # 1. 获取并限制结果数量
        items = origin_result.get("items", [])
        items = items[:config.api_max_show]

        # 2. 安全检查：如果没有结果，直接返回 None，外层循环记得 skip 掉 None
        if not items:
            return None

        # 3. 准备头部信息
        tags_str = "，".join(translate_tags(origin_result.get('tags', [])))
        header = (
            f"🏷️ 标签：{tags_str}\n"
            f"————————————————\n"
            f"以下是来自本源的搜索结果："
        )

        # 4. 准备结果列表 (每个条目前的 \n 是关键)
        # 使用 f"\n\n" 开头确保第一条结果与 header 之间有清晰空行
        body = "\n\n".join([
            f"🎮 名称：{item.get('name', '未知')}\n"
            f"🔗 链接：{item.get('url', '未知')}"
            for item in items
        ])

        # 5. 组合最终字符串
        full_content = f"{header}\n\n{body}"

        return MessageSegment.node_custom(
            user_id=bot_id,
            nickname=get_origin_name(origin_result),
            content=full_content
        )

    # 初始化合并转发消息
    messages = []

    try:
        # 解码SSE
        for line in resp.iter_lines():
            if line:
                # 解码字节流
                decoded_line = line.decode('utf-8')

                # logger.debug("Search Gal Line: {}".format(line))

                # # 过滤并提取内容
                # # 去掉 'data:' 前缀并清理空格
                # content = decoded_line[5:].strip()
                data: dict = json.loads(decoded_line)
                # 处理返回的源计数
                if total := data.get("total"):
                    await search.send(Message([
                        MessageSegment.reply(message_id),
                        MessageSegment.at(user_id),
                        MessageSegment.text(f"\n已找到{total}个搜索源，开始搜索，请耐心等待......")
                    ]))
                # 处理返回的完成标志
                if data.get("done"):
                    await search.finish(Message([
                        MessageSegment.text(f"已完成搜索！以下是搜索到的结果：")
                    ]))
                # 处理每一个源的结果
                if result := data.get("result"):
                    messages.append(generate_message(result))
    except FinishedException:
        pass

    # 只保留 content 不为空的节点
    messages = [m for m in messages if m is not None and m.data.get("content")]
    # ------------------

    # 如果所有源都没有结果，直接结束
    if not messages:
        await search.finish("未找到任何有效结果。")

    result_count = len(messages)

    # 后处理合并转发消息，加入提示等
    messages.insert(0, MessageSegment.node_custom(
        user_id=bot_id,
        nickname="⚠️提示",
        content=f"成功搜索到{result_count}个源的结果！\n"
                f"注意：最好使用带有“推荐”注释的下载源\n"
                f"请将链接复制后粘贴到浏览器地址栏打开！"
    ))

    # logger.debug("Search Gal Ended: {}".format(messages))

    try:
        # 执行发送
        await bot.call_api(
            api="send_group_forward_msg",
            group_id=event.group_id,
            messages=messages,
        )
    except ActionFailed:
        await search.finish(Message([
            MessageSegment.reply(message_id),
            MessageSegment.at(user_id),
            MessageSegment.text("\n发送结果失败！请更换关键词重试!")
        ]))