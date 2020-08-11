import json
from requests import get
from pagermaid import bot, log
from pagermaid.listener import listener


@listener(is_plugin=True, outgoing=True, command="netease",
          description="随机一条网易云音乐评论。")
async def netease(context):
    await context.edit("获取中 . . .")
    req = get("https://api.oioweb.cn/api/wyypl.php")
    if req.status_code == 200:
        data = json.loads(req.text)
        res = data['Comment'] + '\n\n来自 @' + data[
            'UserName'] + ' 在鸽曲"<a href="http://music.163.com/song/media/outer/url?id=' + str(data['SongId']) + '.mp3">' + \
              data['SongName'] + '--by' + data['SongAutho'] + '</a>' + '</a>下方的评论\n\n该评论获得了' + str(data['likedCount']) + '个赞！'
        await context.edit(res, parse_mode='html', link_preview=True)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")
