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
    for _ in range (20): #最多重试20次
        website = random.randint(0, 13)
        filename = "mz" + str(random.random())[2:] + ".png"
        try:
            if website == 0:
                img = get("https://mm.52.mk/img")
            elif website == 1:
                img = get("https://api.helloworld.la/xiezhen_xinggan.php")
            elif website == 2:
                img = get("https://api.66mz8.com/api/rand.tbimg.php")
            elif website == 3:
                img = get("https://api.nmb.show/xiaojiejie2.php")
            elif website == 4:
                img = get("https://uploadbeta.com/api/pictures/random/?key=%E5%A5%B3")
            elif website == 5:
                img = get("https://uploadbeta.com/api/pictures/random/?key=%E5%86%85%E8%A1%A3")
            elif website == 6:
                img = get("https://uploadbeta.com/api/pictures/random/?key=%E6%8E%A8%E5%A5%B3%E9%83%8E")
            elif website == 7:
                img = get("https://tvv.tw/xjj/meinv/img-ct.php")
            elif website == 8:
                img = get("https://api.diskgirl.com/image/api.php?t=xinggan&v=" + str(random.uniform(0, 100)))
            elif website == 9:
                img = get("https://api.lyiqk.cn/sexylady")
            elif website == 10:
                img = get("https://tvv.tw/xjj/meinv/img.php")
            elif website == 11:
                img = get("https://api.uomg.com/api/rand.img3")
            elif website == 12:
                img = get("https://api.nmb.show/xiaojiejie1.php")
            elif website == 13:
                img = get("https://uploadbeta.com/api/pictures/random/?key=%E6%80%A7%E6%84%9F")
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