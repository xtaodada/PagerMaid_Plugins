import json
from random import randint
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove


@listener(is_plugin=True, outgoing=True, command="acgm",
          description="多网站随机获取二刺螈（bushi） ACG图片")
async def joke(context):
    await context.edit("获取中 . . .")
    status = False
    for _ in range (20): #最多重试20次
        website = randint(0, 9)
        if website == 0:
            img = get("http://api.btstu.cn/sjbz/?lx=m_dongman")
        elif website == 1:
            img = get("https://acg.yanwz.cn/api.php")
        elif website == 2:
            img = get("https://img.xjh.me/random_img.php?type=bg&ctype=acg&return=302&device=mobile")
        elif website == 3:
            img = get("https://www.yunboys.cn/sjbz/api.php?method=mobile&lx=dongman")
        elif website == 4:
            img = get("http://www.dmoe.cc/random.php")
        elif website == 5:
            img = get("https://api.vvhan.com/api/acgimg")
        elif website == 6:
            img = get("http://api.mtyqx.cn/api/random.php")
        elif website == 7:
            img = get("http://random.firefliestudio.com/")
        elif website == 8:
            img = get("https://api.mmcee.cn/acgimg/acgurl.php")
        elif website == 9:
            img = get('https://api.lolicon.app/setu/?r18=0')
        if img.status_code == 200:
            if website == 9:
                tmp = json.loads(img.content)
                img = tmp['data'][0]['url']
                img = get(img)
                if img.status_code != 200:
                    continue #如果返回不正常就赶紧下一回
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
        await context.edit("出错了呜呜呜 ~ 试了好多好多次都无法访问到 API 服务器 。")
        sleep(2)
    await context.delete()
