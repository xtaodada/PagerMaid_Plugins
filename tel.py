import json
import os,sys,codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
from requests import get
from pagermaid.listener import listener
from pagermaid.utils import obtain_message

@listener(outgoing=True, command="tel",
          description="手机号码归属地等信息查询。")
async def whois(context):
    await context.edit("获取中 . . .")
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    req = get("https://tenapi.cn/tel?tel=" + message)
    if req.status_code == 200:
        data = json.loads(req.text)
        res = '电话号码：' + str(data['tel']) + '\n' + str(data['local']) + '\n' + str(data['duan']) + '\n' + str(data['type']) + '\n' + str(data['yys']) + '\n' + str(data['bz'])
        await context.edit(res)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")
