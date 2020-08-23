from random import randint
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove


@listener(is_plugin=True, outgoing=True, command="meizi",
          description="多网站随机获取性感（可能）的写真")
async def joke(context):
    await context.edit("获取中 . . .")
    status = False
    for _ in range (20): #最多重试20次
        website = randint(0, 7)
        if website == 0:
            img = get("https://mm.52.mk")
        elif website == 1:
            img = get("https://api.helloworld.la/xiezhen_xinggan.php")
        elif website == 2:
            img = get("https://api.helloworld.la/bizhi_meizi.php")
        elif website == 3:
            img = get("https://uploadbeta.com/api/pictures/random/?key=%E5%A4%A7%E5%B0%BA%E5%BA%A6")
        elif website == 4:
            img = get("https://cdn.seovx.com/?mom=302")
        elif website == 5:
            img = get("https://uploadbeta.com/api/pictures/random/?key=%E5%A6%B9%E5%AD%90")
        elif website == 6:
            img = get("https://uploadbeta.com/api/pictures/random/?key=%E6%8E%A8%E5%A5%B3%E9%83%8E")
        elif website == 7:
            img = get("https://uploadbeta.com/api/pictures/random/?key=%E5%A5%B3%E7%A5%9E")
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
