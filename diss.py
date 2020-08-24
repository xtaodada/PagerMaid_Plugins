from requests import get
from pagermaid.listener import listener

@listener(is_plugin=True, outgoing=True, command="diss",
          description="儒雅随和版祖安语录。")
async def diss(context):
    await context.edit("获取中 . . .")
    req = get("https://nmsl.shadiao.app/api.php?level=min&from=tnt")
    if req.status_code == 200:
        res = req.text
        await context.edit(res, parse_mode='html', link_preview=False)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")

@listener(is_plugin=True, outgoing=True, command="biss",
          description="加带力度版祖安语录。")
async def biss(context):
    await context.edit("获取中 . . .")
    req = get("https://nmsl.shadiao.app/api.php?&from=tnt")
    if req.status_code == 200:
        res = req.text
        await context.edit(res, parse_mode='html', link_preview=False)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")