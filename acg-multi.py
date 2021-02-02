import json
import random
import requests
from time import sleep
from pagermaid.listener import listener
from os import remove


@listener(is_plugin=True, outgoing=True, command="acgm",
          description="多网站随机获取二刺螈（bushi） ACG图片")
async def joke(context):
    await context.edit("获取中 . . .")
    status = False
    for _ in range (5): #最多重试5次
        website = random.randint(0, 6)
        filename = str(random.random()) + ".png"
        try:
            if website == 0:
                img = requests.get("https://api.lyiqk.cn/miku")
            elif website == 1:
                img = requests.get("https://api.lyiqk.cn/acgst")
            elif website == 2:
                img = requests.get("https://img.catct.cn/pixiv.php")
            elif website == 3:
                img = requests.get("https://acg.yanwz.cn/api.php")
            elif website == 4:
                img = requests.get("https://acg.yanwz.cn/wallpaper/api.php")
            elif website == 5:
                img = requests.get("https://api.ixiaowai.cn/mcapi/mcapi.php")
            if img.status_code == 200:
                if website == 6:
                    tmp = json.loads(img.content)
                    img = tmp['data'][0]['url']
                    img = requests.get(img)
                    if img.status_code != 200:
                        continue #如果返回不正常就赶紧下一回
                with open(filename, 'wb') as f:
                    await context.edit("上传中 . . .")
                    f.write(img.content)
                    await context.client.send_file(
                        context.chat_id,
                        filename,
                        reply_to=None,
                        caption=None
                    )
                try:
                    remove(filename)
                except:
                    pass
                status = True
                break #成功了就赶紧结束啦！
        except:
            continue
    if not status:
        await context.edit("出错了呜呜呜 ~ 试了好多好多次都无法访问到 API 服务器 。")
        sleep(2)
    await context.delete()
