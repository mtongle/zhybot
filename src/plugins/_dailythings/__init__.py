import random
import requests

from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from nonebot.log import logger
from nonebot.plugin.on import on_command

from bs4 import BeautifulSoup, Tag

daily_novel = on_command("来本小说", priority=50)

headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.55")
    }

def fix_content(content):
    """
    修复给定标的内容。内容应为字符串，每个字符串都是一段文本。

    该函数遍历内容中的每个字符，检查它是否在特殊字符范围内，如果是，则将其替换为CHAR_SET列表中对应的字符。

    :param content: 一段文本
    :return: 一段已修复的文本
    """
    # 定义特殊字符集和对应的替换字符
    CHAR_SET = [
    'D', '在', '主', '特', '家', '军', '然', '表', '场', '4', '要', '只', 'v', '和', '?', '6', '别', '还', 'g',
    '现', '儿', '岁', '?', '?', '此', '象', '月', '3', '出', '战', '工', '相', 'o', '男', '首', '失', '世', 'F',
    '都', '平', '文', '什', 'V', 'O', '将', '真', 'T', '那', '当', '?', '会', '立', '些', 'u', '是', '十', '张',
    '学', '气', '大', '爱', '两', '命', '全', '后', '东', '性', '通', '被', '1', '它', '乐', '接', '而', '感',
    '车', '山', '公', '了', '常', '以', '何', '可', '话', '先', 'p', 'i', '叫', '轻', 'M', '士', 'w', '着', '变',
    '尔', '快', 'l', '个', '说', '少', '色', '里', '安', '花', '远', '7', '难', '师', '放', 't', '报', '认',
    '面', '道', 'S', '?', '克', '地', '度', 'I', '好', '机', 'U', '民', '写', '把', '万', '同', '水', '新', '没',
    '书', '电', '吃', '像', '斯', '5', '为', 'y', '白', '几', '日', '教', '看', '但', '第', '加', '候', '作',
    '上', '拉', '住', '有', '法', 'r', '事', '应', '位', '利', '你', '声', '身', '国', '问', '马', '女', '他',
    'Y', '比', '父', 'x', 'A', 'H', 'N', 's', 'X', '边', '美', '对', '所', '金', '活', '回', '意', '到', 'z',
    '从', 'j', '知', '又', '内', '因', '点', 'Q', '三', '定', '8', 'R', 'b', '正', '或', '夫', '向', '德', '听',
    '更', '?', '得', '告', '并', '本', 'q', '过', '记', 'L', '让', '打', 'f', '人', '就', '者', '去', '原', '满',
    '体', '做', '经', 'K', '走', '如', '孩', 'c', 'G', '给', '使', '物', '?', '最', '笑', '部', '?', '员', '等',
    '受', 'k', '行', '一', '条', '果', '动', '光', '门', '头', '见', '往', '自', '解', '成', '处', '天', '能',
    '于', '名', '其', '发', '总', '母', '的', '死', '手', '入', '路', '进', '心', '来', 'h', '时', '力', '多',
    '开', '己', '许', 'd', '至', '由', '很', '界', 'n', '小', '与', 'Z', '想', '代', '么', '分', '生', '口',
    '再', '妈', '望', '次', '西', '风', '种', '带', 'J', '?', '实', '情', '才', '这', '?', 'E', '我', '神', '格',
    '长', '觉', '间', '年', '眼', '无', '不', '亲', '关', '结', '0', '友', '信', '下', '却', '重', '己', '老',
    '2', '音', '字', 'm', '呢', '明', '之', '前', '高', 'P', 'B', '目', '太', 'e', '9', '起', '稜', '她', '也',
    'W', '用', '方', '子', '英', '每', '理', '便', '西', '数', '期', '中', 'C', '外', '样', 'a', '海', '们',
    '任']
    # 定义特殊字符的起始和结束Unicode码
    CODE_ST = 58344
    CODE_ED = 58715

    def interpreter(cc: int):
        """
        将Unicode码转换为对应的字符。如果字符在CHAR_SET中是'?'，则返回其Unicode码对应的字符；否则返回CHAR_SET中对应的字符。

        :param cc: Unicode码
        :return: 对应的字符
        """
        # 计算字符在CHAR_SET中的索引
        bias = cc - CODE_ST
        # 如果CHAR_SET中对应的字符是'?'，则返回其Unicode码对应的字符
        if CHAR_SET[bias] == "?":
            return chr(cc)
        # 否则返回CHAR_SET中对应的字符
        else:
            return CHAR_SET[bias]

    content_list = []
    fixed = ''
    # 遍历段落中的每个字符
    for char in content:
        # 获取字符的Unicode码
        cc = ord(char)
        # 如果Unicode码在特殊字符范围内
        if CODE_ST <= cc <= CODE_ED:
            # 使用interpreter函数将Unicode码转换为对应的字符
            ch = interpreter(cc)
            # 将转换后的字符添加到para中
            fixed += ch
        # 否则直接将字符添加到para中
        else:
            fixed += char
    # 返回修复后的文本
    return fixed

@daily_novel.handle()
async def handle_daily_novel(event: GroupMessageEvent):
    user_id = int(event.get_user_id())
    message_id = event.message_id
    page = random.randint(1,99)
    url = f"https://fanqienovel.com/library/all/page_{page}?sort=hottes"
    logger.debug(url)
    result = requests.get(url=url, headers=headers)
    if result.status_code != 200:
        await daily_novel.finish(f"[CQ:reply,id={message_id}][CQ:at,qq={user_id}]\n获取失败！\n错误的状态码：{result.status_code}")
    soup = BeautifulSoup(result.content, "lxml")
    logger.debug(soup.prettify())
    book_tags = soup.find("div", {"class": "stack-book-item"})
    book_tag = random.choice(book_tags)
    cover_url = book_tag.find("img", {"class": "book-cover-img  loaded"}).attrs["src"]
    raw_book_name = book_tag.find("img",{"class":"book-cover-img  loaded"}).text
    book_name = fix_content(raw_book_name)
    await daily_novel.finish(f"[CQ:reply,id={message_id}][CQ:at,qq={user_id}]\n{book_name}[CQ:image,file={cover_url},subType=0]")