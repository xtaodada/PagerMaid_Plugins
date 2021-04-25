import json
from requests import get
from pagermaid import bot, log
from pagermaid.listener import listener


@listener(is_plugin=True, outgoing=True, command="netease",
          description="随机一条网易云音乐评论。")
async def netease(context):
    await context.edit("获取中 . . .")
    try:
        req = get("https://api.66mz8.com/api/music.163.php?format=json")
    except:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")
        return
    if req.status_code == 200:
        data = json.loads(req.text)
        res = data['comments'] + '\n\n来自 @' + data[
            'nickname'] + ' 在鸽曲 <a href="' + str(data['music_url']) + '">' + \
              data['name'] + ' --by' + data['artists_name'] + '</a>' + ' 下方的评论。'
        await context.edit(res, parse_mode='html', link_preview=True)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")
