import json
import os,sys,codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
from requests import get
from pagermaid.listener import listener
from pagermaid.utils import obtain_message

@listener(outgoing=True, command="whois",
          description="查看域名是否已被注册、注册日期、过期日期、域名状态、DNS解析服务器等。")
async def whois(context):
    await context.edit("获取中 . . .")
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    req = get("https://tenapi.cn/whois/?url=" + message)
    if req.status_code == 200:
        data = json.loads(req.text)
        res = 'url： ' + data['data']['url'] + '\n注册商： ' + str(data['data']['注册商']) + '\n联系人： ' + str(data['data']['联系人']) + '\n联系邮箱： ' + str(data['data']['联系邮箱']) + '\n注册时间： ' + str(data['data']['注册时间']) + '\n过期时间： ' + str(data['data']['过期时间']) + '\nDNS： ' + str(data['data']['DNS'])
        await context.edit(res)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")
