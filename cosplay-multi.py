from random import randint, random
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove


@listener(is_plugin=True, outgoing=True, command="cosm",
          description="多网站随机获取cosplay图片，会自动重试哦")
async def joke(context):
    await context.edit("获取中 . . .")
    status = False
    for _ in range (5): #最多重试5次
        website = randint(0, 6)
        filename = str(random()) + ".png"
        try:
            if website == 0:
                img = get("https://cdn.seovx.com/?mom=302")
            elif website == 1:
                img = get("https://api.ixxcc.com/cosplay.php?return=img")
            elif website == 2:
                img = get("https://api.helloworld.la/xiezhen_weimei.php", timeout=5)
            elif website == 3:
                img = get("https://xn--wcs142h.herokuapp.com/")
            if img.status_code == 200:
                if website == 3:
                    img = get(img.content)
                    if img.status_code != 200:
                        continue #再试一次
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
