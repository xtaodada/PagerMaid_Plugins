import random
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove


@listener(is_plugin=True, outgoing=True, command="mz",
          description="多网站随机获取性感（可能）的写真")
async def mz(context):
    await context.edit("获取中 . . .")
    status = False
    for _ in range (5): #最多重试5次
        website = 0
        filename = "mz" + str(random.random())[2:] + ".png"
        try:
            if website == 0:
                img = get("https://api.lyiqk.cn/purelady")
            elif website == 1:
                img = get("https://api.lyiqk.cn/sexylady")
            if img.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(img.content)
                await context.edit("上传中 . . .")
                await context.client.send_file(context.chat_id,filename)
                status = True
                break #成功了就赶紧结束啦！
        except:
            try:
                remove(filename)
            except:
                pass
            continue
    try:
        remove(filename)
    except:
        pass
    try:
        await context.delete()
    except:
        pass
    if not status:
        await context.client.send_message(context.chat_id,"出错了呜呜呜 ~ 试了好多好多次都无法访问到服务器（没有妹子看啦！） 。")

@listener(is_plugin=True, outgoing=True, command="sp",
          description="随机获取妹子的视频")
async def sp(context):
    await context.edit("获取中 . . .")
    status = False
    for _ in range (20): #最多重试20次
        try:
            vid = get("https://mv.52.mk/video.php")
            filename = "sp" + str(random.random())[2:] + ".mp4"
            if vid.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(vid.content)
                await context.edit("上传中 . . .")
                await context.client.send_file(context.chat_id,filename)
                status = True
                break #成功了就赶紧结束啦！
        except:
            try:
                remove(filename)
            except:
                pass
            continue
    try:
        remove(filename)
    except:
        pass
    try:
        await context.delete()
    except:
        pass
    if not status:
        try:
            remove(filename)
        except:
            pass
        try:
            await context.delete()
        except:
            pass
        await context.client.send_message(context.chat_id,"出错了呜呜呜 ~ 试了好多好多次都无法访问到服务器（没有妹子视频看啦！） 。")
