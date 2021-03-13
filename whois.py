import json
import os,sys,codecs

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
        data = json.loads(req.text)['data']
        res = '域名： `' + data['url'] + '`\n注册商： `' + str(data['registrar']) + '`\n联系人： `' + str(data['registrant']) + '`\n联系邮箱： `' + str(data['mail']) + '`\n注册时间： `' + str(data['registration']) + '`\n过期时间： `' + str(data['expiration']) + '`\nDNS： ' + str(data['dns']).replace('<br/>', '\n')
        await context.edit(res)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")
