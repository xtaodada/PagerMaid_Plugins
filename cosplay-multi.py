import json
import random
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove, popen


@listener(is_plugin=True, outgoing=True, command="cosm",
          description="多网站随机获取cosplay图片，会自动重试哦")
async def joke(context):
    await context.edit("获取中 . . .")
    status = False
    for i in range (20): #最多重试20次
        website = random.randint(0, 3)
        if website == 0:
            img = get("https://api.helloworld.la/xiezhen_cosplay.php")
        elif website == 1:
            img = get("https://api.vvhan.com/api/mobil.girl?type=json")
        elif website == 2:
            img = get("https://api.helloworld.la/xiezhen_weimei.php")
        elif website == 3:
            img = get("http://api.rosysun.cn/cos")
        if img.status_code == 200:
            if website == 3:
                img = get(img.content)
                if img.status_code != 200:
                    continue #再试一次
            with open(r'tu.png', 'wb') as f:
                await context.edit("正在上传图片")
                f.write(img.content)
                await context.client.send_file(
                context.chat_id,
                "tu.png",
             reply_to=None,
                 caption=None
             )
            remove('tu.png')
            status = True
            break #成功了就赶紧结束啦！

    if not status:
        await context.edit("出错了呜呜呜 ~ 试了好多好多次都无法访问到 API 服务器 。")
        sleep(2)
    await context.delete()
