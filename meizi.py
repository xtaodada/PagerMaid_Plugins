from random import randint
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove


@listener(is_plugin=True, outgoing=True, command="meizi",
          description="多网站随机获取性感（可能）的写真")
async def meizi(context):
    await context.edit("获取中 . . .")
    status = False
    for _ in range (20): #最多重试20次
        website = randint(0, 13)
        if website == 0:
            img = get("https://mm.52.mk")
        elif website == 1:
            img = get("https://api.helloworld.la/xiezhen_xinggan.php")
        elif website == 2:
            img = get("https://api.qicaiyun.top/sjbz/api.php?lx=meizi")
        elif website == 3:
            img = get("http://api.btstu.cn/sjbz/?lx=meizi")
        elif website == 4:
            img = get("https://cdn.seovx.com/?mom=302")
        elif website == 5:
            img = get("https://uploadbeta.com/api/pictures/random/?key=%E5%A6%B9%E5%AD%90")
        elif website == 6:
            img = get("https://uploadbeta.com/api/pictures/random/?key=%E6%8E%A8%E5%A5%B3%E9%83%8E")
        elif website == 7:
            img = get("https://uploadbeta.com/api/pictures/random/?key=%E7%BE%8E%E5%A5%B3")
        elif website == 8:
            img = get("https://api.941ka.cn/api/mnxz")
        elif website == 9:
            img = get("https://api.lyiqk.cn/sexylady")
        elif website == 10:
            img = get("https://api.pingping6.com/tools/acg3/index.php")
        elif website == 11:
            img = get("https://api.pingping6.com/tools/acg3")
        elif website == 12:
            img = get("https://api.diskgirl.com/image/api.php?t=&v=0.9451485087333713")
        elif website == 13:
            img = get("https://api.diskgirl.com/image/api.php?t=&v=" + str(random.uniform(0, 100)))
        if img.status_code == 200:
            with open(r'tu.png', 'wb') as f:
                await context.edit("正在上传图片")
                f.write(img.content)
                await context.client.send_file(
                    context.chat_id,
                    "tu.png",
                    reply_to=None,
                    caption=None
                  )
            try:
                remove('tu.png')
            except:
                pass
            status = True
            break #成功了就赶紧结束啦！

    if not status:
        await context.edit("出错了呜呜呜 ~ 试了好多好多次都无法访问到 API 服务器（没有妹子看啦！） 。")
        sleep(2)
    await context.delete()
