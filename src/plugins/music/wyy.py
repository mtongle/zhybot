import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from lxml import etree
from nonebot import logger
from nonebot.plugin.on import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.rule import to_me
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService

from src.plugins.utils import get_basemsg
from src.plugins.utils.selemium import new_driver, find_element_by_css_selector

wwy = on_regex(
    pattern=r"(https?://)?.*163(cn)?\.\w+/.+",
    flags=re.IGNORECASE,
    priority=50,
    block=True,
    # rule=to_me()
)

def short_to_real(short_id) -> str:
    url = "http://163cn.tv/{}".format(short_id)
    # resp = requests.get(url)
    # resp.raise_for_status()
    #
    # html = etree.HTML(resp.text)
    # real_id = html.xpath(r'//*[@id="content-operation"]/a[1]')[0].get("data-res-id")

    driver = new_driver()
    driver.set_page_load_timeout(3)
    try:
        driver.get(url)
    except TimeoutException:
        pass

    driver.switch_to.frame(0)
    real_id = find_element_by_css_selector(driver, ".btn[data-action='orpheus']").get_attribute("data-id")

    driver.quit()
    return real_id

def get_song_info(song_id: str) -> dict[str, str]:
    url = "https://music.163.com/#/song?id={}".format(song_id)
    # referer = "http://music.163.com"
    # cookie = r"NTES_P_UTID=B24p8RG5fT6AKKCvyAosAb61QBIm7h7R|1747916679; P_INFO=zhaotongle2010@163.com|1747916679|1|mail163|00&99|CN&1727910430&mail163#jis&320100#10#0#0|&0||zhaotongle2010@163.com; timing_user_id=time_pc3Dm8j6O3; _ga=GA1.1.652821201.1751968598; _clck=1kus0n3%7C2%7Cfxf%7C0%7C2015; _ga_C6TGHFPQ1H=GS2.1.s1751968597$o1$g1$t1751968691$j60$l0$h0; _iuqxldmzr_=32; _ntes_nnid=89557e2f5dbaec9b895e9ac06fa21ade,1752125640015; _ntes_nuid=89557e2f5dbaec9b895e9ac06fa21ade; NMTID=00ObtldxhcsMZRlTUSJk4fAGPILtpQAAAGX8tOOMg; WM_NI=ENqPzM34D7cth6xVWLkxLV%2FLQQS35eG7e5IGD3dhzmT8v7bzjbZw0yANGT4EWbdZdsefxgYJ9dvU4v3g8sCFbM8wFD%2B6wSEPowozfpPkcTloZhlNcDHE%2F3gpy5cNkL0gNng%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eed8c6478eaa968ce64bba9e8aa2c44f878f8e82c748e9ac82d6b4258c89fcacd42af0fea7c3b92a8792bfb1f947f1ec8cd8e280aceab8b7d648a9a884b7ae48938f9dd4b86f85e9abd6cc4d88edac89f96798e8bad8e172aabe9698b373839289b5b74f95beacbbe779a7bab888dc42fbbcbab6b77ef1b9f894c24ea293f898c550e9eab9b4c85cada9a19be57c94b5adb5ef659ab8a4afe2508c9be1d4e67cbbebadafea48f4b9828fe637e2a3; WM_TID=TQCyjMTdcoZAQUFFEEaDfq5N916DH8PV; WEVNSM=1.0.0; WNMCID=bowbwg.1752125674499.01.0; __snaker__id=MrBu0cWKTBhQTzKx; gdxidpyhxdE=TAtL6KpQCzLNhLWXlvsOK5owwjxJNAfvbCEcIZPJPS8MLt%2FX%2BmBLuZLx1rGi6%2FEe7JJk1mZMe4PC9AhP%2FrzauwrVoGTMD8W0x%5CDao8rVjQ%2BXZSlqyL%2F7t8v3sXHY4151%5ClazMGUTry32D72vNsxBdvwcOeL%2FS0xD%2BmlBIUW96M%2BvLa5v%3A1752126610738; ntes_utid=tid._.qehB44OQf9hBRxERVAfXeq9N43Ge39%252B%252F._.0; sDeviceId=YD-squxap4z7k5BA1ARVQaGar8N9mXOzs7u; _ntes_origin_from=google; JSESSIONID-WYYY=bPDeid5ezIcMRXhluub5KlegyAVqs%2BWe1BN%2BDP52PM7Fl3H5Q0nAo9JlYuGWrwM%2BPnKX5eeeodS3Yswp%2FoqvA9yC%2BGUivq5aBCiGESEurSVcYgmqPXt2%2BIuKP48dg88mURxnporMJuORn3sclZfzbuiMMGBBWN2hqdlX%2FU9MNDc%5Cahv%5C%3A1752136146034"
    # user_agent = r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    # accept_encoding = "gzip, deflate, br, zstd"
    # accept_language = "zh-CN,zh;q=0.9,en;q=0.8"
    # sec_ch_ua_platform = '"Linux"'
    # accept = r"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    # headers = {
    #     "Referer": referer,
    #     "Cookie": cookie,
    #     "User-Agent": user_agent,
    #     # "accept": accept,
    #     # "accept-encoding": accept_encoding,
    #     # "accept-language": accept_language,
    #     # "sec-ch-ua-platform": sec_ch_ua_platform,
    # }
    #
    # resp = requests.get(url, headers=headers)
    # resp.raise_for_status()

    driver = new_driver()
    driver.set_page_load_timeout(3)
    try:
        driver.get(url)
    except TimeoutException:
        pass

    # with open("log.html", "w+") as f:
    #     f.write(driver.page_source)

    driver.switch_to.frame(0)
    name = find_element_by_css_selector(
        driver=driver,
        css_selector="em.f-ff2"
    ).text
    author = find_element_by_css_selector(
        driver=driver,
        css_selector="span a.s-fc7"
    ).text
    cover_url = find_element_by_css_selector(
        driver=driver,
        css_selector="img.j-img"
    ).get_attribute("src")

    # name = soup.find("body > div.g-bd4.f-cb > div.g-mn4 > div > div > div.m-lycifo > div.f-cb > div.cnt > div.hd > div > em").text
    # author = soup.find("body > div.g-bd4.f-cb > div.g-mn4 > div > div > div.m-lycifo > div.f-cb > div.cnt > p:nth-child(2) > span > a").text
    # cover_url = soup.find("body > div.g-bd4.f-cb > div.g-mn4 > div > div > div.m-lycifo > div.f-cb > div.cvrwrap.f-cb.f-pr > div.u-cover.u-cover-6.f-fl > img").get("src")

    driver.quit()
    return {
        "name": name,
        "author": author,
        "cover_url": cover_url,
    }

class VipNeededError(Exception):
    pass

def save_song(song_id: str) -> Path:
    url = "https://music.163.com/song/media/outer/url?id={}".format(song_id)
    resp = requests.get(url)
    resp.raise_for_status()

    if resp.text.startswith("<!DOCTYPE html>"):
        raise VipNeededError

    file_path = Path(f"/home/tongle/Music/网易云下载/{song_id}.mp3")
    with open(file_path, "wb") as f:
        f.write(resp.content)

    return file_path


@wwy.handle()
async def handle_wwy(bot: Bot, event: GroupMessageEvent):
    basemsg = get_basemsg(event)
    message = event.message.extract_plain_text().strip()

    song_id = re.findall(r'\d{8,}', message)[0]
    if not song_id:
        short_id = re.findall(r'[^:/.?&=%#@_-]{6,}', message)[0]
        song_id = short_to_real(short_id)

        if not song_id:
            await wwy.finish(basemsg
                + MessageSegment.text("抱歉，没找到歌曲id！")
            )

    try:
        song_info = get_song_info(song_id)
    except Exception as e:
        await wwy.finish(basemsg
            + MessageSegment.text(f"啊呀，获取歌曲信息出错啦！\n错误详情：{e.__class__.__name__}")
        )

    resp = await wwy.send(basemsg
        + MessageSegment.text(f"发现歌曲！\n歌曲名称：{song_info["name"]}\n歌曲作者：{song_info["author"]}\n正在努力下载，稍安勿躁哦......")
        + MessageSegment.image(song_info["cover_url"])
    )

    try:
        song_path = save_song(song_id)
    except VipNeededError:
        message_id = resp["data"]["message_id"]
        await bot.delete_msg(message_id=message_id)
        await wwy.finish(basemsg
            + MessageSegment.text(f"这首歌是VIP专属，无法下载哦！\n（或者你也可以赞助我VIP）\n歌曲名称：{song_info["name"]}\n歌曲作者：{song_info["author"]}")
            + MessageSegment.image(song_info["cover_url"])
        )

    # os.rename(song_path, f"{song_info["name"]}.mp3")
    pretty_path = Path(f"/home/tongle/Music/网易云下载/{song_info["name"]}.mp3")
    song_path.rename(pretty_path)

    logger.debug(str(pretty_path))
    await bot.upload_group_file(group_id=event.group_id, file=str(pretty_path), name=f"{song_info['name']}.mp3")
