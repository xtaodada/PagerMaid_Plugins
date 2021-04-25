import json
from random import randint, choice
from time import sleep
from requests import get
from pagermaid.listener import listener


def get_api(num):
    api = ['https://api.ghser.com/saohua/?type=json',
           'https://api.lovelive.tools/api/SweetNothings/?type=json',
           f'https://api.lovelive.tools/api/SweetNothing/Keyword/{randint(1, 20)}',
           'https://api.muxiaoguo.cn/api/tiangourj',
           'https://xiaojieapi.com/api/v1/get/security',
           'https://api.muxiaoguo.cn/api/Gushici'
           ]
    name = ['骚话', '情话', '渣男语录', '舔狗语录', '保安日记', '古诗词']
    return api[num], name[num]


def process_web_data(num, req):
    data = json.loads(req.text)
    if num == 0:
        res = data['ishan']
    elif num == 1 or num == 2:
        if len(data['returnObj']) == 0:
            res = "出错了呜呜呜 ~ API 服务器 返回了空数据。"
        else:
            res = choice(data['returnObj'])
    elif num == 3:
        res = data['data']['comment']
    elif num == 4:
        res = f"{data['date']} {data['week']} {data['weather']}\n{data['msg']}"
    else:
        poet = data['data']['Poet']
        if poet == 'null':
            poet = '未知'
        res = f"{data['data']['Poetry']}  ——《{data['data']['Poem_title']}》（{poet}）"
    return res


@listener(is_plugin=True, outgoing=True, command="diy",
          description="多个随机api。",
          parameters="<'sao', 'qh', 'zn', 'tg', 'ba', 'gs'> (可选，用于自定义 api)")
async def diy(context):
    short_name = ['sao', 'qh', 'zn', 'tg', 'ba', 'gs']
    try:
        if not len(context.parameter) == 0:
            api = context.parameter[0]
            if api in short_name:
                num = short_name.index(api)
                api_url, name = get_api(num)
                text = "正在编" + name
            else:
                await context.edit("正在掷🎲 . . .")
                num = randint(0, 5)
                api_url, name = get_api(num)
                text = f"🎲点数为 `{str(num) + 1}` 正在编{name}"
        else:
            await context.edit("正在掷🎲 . . .")
            num = randint(0, 5)
            api_url, name = get_api(num)
            text = f"🎲点数为 `{str(num) + 1}` 正在编{name}"
    except:
        await context.edit("正在掷🎲 . . .")
        num = randint(0, 5)
        api_url, name = get_api(num)
        text = f"🎲点数为 `{str(num) + 1}` 正在编{name}"
    await context.edit(text)
    status = False
    for _ in range(20):  # 最多尝试20次
        req = get(api_url)
        if req.status_code == 200:
            try:
                await context.edit(process_web_data(num, req), parse_mode='html', link_preview=False)
            except:
                pass
            status = True
            break
        else:
            continue
    if not status:
        await context.edit("出错了呜呜呜 ~ 试了好多好多次都无法访问到 API 服务器 。")
        sleep(2)
        await context.delete()
