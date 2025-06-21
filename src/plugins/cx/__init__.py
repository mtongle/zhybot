import time

import pymysql
from arclet.alconna import Alconna, Args, Option, Subcommand
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.log import logger
from nonebot.rule import to_me
from nonebot_plugin_alconna import on_alconna, Query, AlconnaMatch, Match

from src.plugins.utils import get_basemsg

cx = on_alconna(
    Alconna(
        "cx",
        Subcommand(
            "qq",
            Args["id", int]
        ),
        Subcommand(
            "phone",
            Args["id", int]
        )
        ),
    auto_send_output=True,
    # rule=to_me(),
)

db_host = "localhost"
db_port = 3306
db_user = "socialdb_admin"
db_passwd = "fuckrubbishapps"
db_name = "socialdb"

@cx.assign("qq")
async def qq2phone(event: GroupMessageEvent, query: Query[int] = Query("qq.id", 0)):
    qqid = query.result
    # logger.debug(f"qq2phone {qq}")
    basemsg = get_basemsg(event)

    db = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_passwd, db=db_name)
    # logger.debug(str(db))
    cursor = db.cursor()

    start_time = time.time()
    cursor.execute("select phone from qq8e where qq=%s;", [qqid])
    results = cursor.fetchall()
    used_time = str(time.time() - start_time)[:7]

    # logger.debug("database query results: " + str(results))
    phones = [str(result[0]) for result in results if result[0] is not None]
    # logger.debug("qq2phone results: " + str(phones))
    if len(phones) == 0:
        await cx.send(basemsg.extend([
            MessageSegment.text(f"DB query OK, {used_time}s used.\nNo datas found."),
        ]))
    else:
        await cx.send(basemsg.extend([
            MessageSegment.text(f"DB query OK, {used_time}s used.\n{len(phones)} datas found:\n"),
            MessageSegment.text("\n".join(phones)),
        ]))

    cursor.close()
    db.close()

@cx.assign("phone")
async def phone2qq(event: GroupMessageEvent, query: Query[int] = Query("phone.id")):
    phoneid = query.result
    basemsg = get_basemsg(event)

    db = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_passwd, db=db_name)
    cursor = db.cursor()

    start_time = time.time()
    cursor.execute("select qq from qq8e where qq=%s;", [phoneid])
    results = cursor.fetchall()
    used_time = str(time.time() - start_time)[:7]

    # logger.debug("database query results: " + str(results))
    qqs = [str(result[0]) for result in results if result[0] != 0]
    # logger.debug("phone2qq results: " + str(qqs))
    if len(qqs) == 0:
        await cx.send(basemsg.extend([
            MessageSegment.text(f"DB query OK, {used_time}s used.\nNo datas found."),
        ]))
    else:
        await cx.send(basemsg.extend([
            MessageSegment.text(f"DB query OK, {used_time}s used.\n{len(qqs)} datas found:\n"),
            MessageSegment.text("\n".join(qqs)),
        ]))

    cursor.close()
    db.close()