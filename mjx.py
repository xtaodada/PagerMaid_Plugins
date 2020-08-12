import json
from requests import get
from pagermaid.listener import listener


@listener(is_plugin=True, outgoing=True, command="mjx",
          description="随机一个淘宝带图评价。")
async def mjx(context):
    await context.edit("获取中 . . .")
    req = get("http://api.vvhan.com/api/tao?type=json")
    if req.status_code == 200:
        data = json.loads(req.text)
        res = '<a href=' + data['pic'] + '>' + '随机tb买家秀：' + '</a>' + '\n买家评价：' + data['title']
        await context.edit(res, parse_mode='html', link_preview=True)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")


@listener(is_plugin=True, outgoing=True, command="sqmjx",
          description="一个淘宝涩气买家秀。")
async def sqmjx(context):
    await context.edit("获取中 . . .")
    req = get("http://api.uomg.com/api/rand.img3?format=json")
    if req.status_code == 200:
        data = json.loads(req.text)
        res = '<a href=' + data['imgurl'] + '>' + '随机tb涩气买家秀' + '</a>'
        await context.edit(res, parse_mode='html', link_preview=True)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")
