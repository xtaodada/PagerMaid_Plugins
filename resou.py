import json
from requests import get
from pagermaid import bot, log
from pagermaid.listener import listener


@listener(is_plugin=True, outgoing=True, command="zhrs",
          description="知乎热搜。")
async def netease(context):
    await context.edit("获取中 . . .")
    req = get("https://tenapi.cn/zhihuresou")
    if req.status_code == 200:
        data = json.loads(req.text)
        res = '知乎实时热搜榜：' + '\n\n1.' + '「<a href=' + data['list']['1']['url'] + '>' + data['list']['1']['query']  + '</a>」' + '\n2.' + '「<a href=' + data['list']['2']['url'] + '>' + data['list']['2']['query']  + '</a>」' + '\n3.' + '「<a href=' + data['list']['3']['url'] + '>' + data['list']['3']['query']  + '</a>」' + '\n4.' + '「<a href=' + data['list']['4']['url'] + '>' + data['list']['4']['query']  + '</a>」' + '\n5.' + '「<a href=' + data['list']['5']['url'] + '>' + data['list']['5']['query']  + '</a>」' + '\n6.' + '「<a href=' + data['list']['6']['url'] + '>' + data['list']['6']['query']  + '</a>」' + '\n7.' + '「<a href=' + data['list']['7']['url'] + '>' + data['list']['7']['query']  + '</a>」' + '\n8.' + '「<a href=' + data['list']['8']['url'] + '>' + data['list']['8']['query']  + '</a>」' + '\n9.' + '「<a href=' + data['list']['9']['url'] + '>' + data['list']['9']['query']  + '</a>」' + '\n10.' + '「<a href=' + data['list']['10']['url'] + '>' + data['list']['10']['query']  + '</a>」'
        await context.edit(res, parse_mode='html', link_preview=False)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")


@listener(is_plugin=True, outgoing=True, command="wbrs",
          description="微博热搜。")
async def netease(context):
    await context.edit("获取中 . . .")
    req = get("https://tenapi.cn/resou")
    if req.status_code == 200:
        data = json.loads(req.text)
        res = '微博实时热搜榜：' + '\n\n1.' + '「<a href=' + data['list']['1']['url'] + '>' + data['list']['1']['name']  + '</a>」' + '  热度：' + data['list']['1']['hot'] + '\n2.' + '「<a href=' + data['list']['2']['url'] + '>' + data['list']['2']['name']  + '</a>」' + '  热度：' + data['list']['2']['hot'] + '\n3.' + '「<a href=' + data['list']['3']['url'] + '>' + data['list']['3']['name']  + '</a>」' + '   热度：' + data['list']['3']['hot'] + '\n4.' + '「<a href=' + data['list']['4']['url'] + '>' + data['list']['4']['name']  + '</a>」' + '  热度：' + data['list']['4']['hot'] + '\n5.' + '「<a href=' + data['list']['5']['url'] + '>' + data['list']['5']['name']  + '</a>」' + '  热度：' + data['list']['5']['hot'] + '\n6.' + '「<a href=' + data['list']['6']['url'] + '>' + data['list']['6']['name']  + '</a>」' + '  热度：' + data['list']['6']['hot'] + '\n7.' + '「<a href=' + data['list']['7']['url'] + '>' + data['list']['7']['name']  + '</a>」' + '  热度：' + data['list']['7']['hot'] + '\n8.' + '「<a href=' + data['list']['8']['url'] + '>' + data['list']['8']['name']  + '</a>」' + '  热度：' + data['list']['8']['hot'] + '\n9.' + '「<a href=' + data['list']['9']['url'] + '>' + data['list']['9']['name']  + '</a>」' + '  热度：' + data['list']['9']['hot'] + '\n10.' + '「<a href=' + data['list']['10']['url'] + '>' + data['list']['10']['name']  + '</a>」' + '  热度：' + data['list']['10']['hot']
        await context.edit(res, parse_mode='html', link_preview=True)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")


@listener(is_plugin=True, outgoing=True, command="dyrs",
          description="抖音热搜。")
async def netease(context):
    await context.edit("获取中 . . .")
    req = get("https://tenapi.cn/douyinresou")
    if req.status_code == 200:
        data = json.loads(req.text)
        res = '抖音实时热搜榜：' + '\n\n1.' + data['list']['1']['name'] + '  热度：' + str(data['list']['1']['hot']) + '\n2.' + data['list']['2']['name'] + '  热度：' + str(data['list']['2']['hot']) + '\n3.' + data['list']['3']['name'] + '   热度：' + str (data['list']['3']['hot']) + '\n4.' + data['list']['4']['name'] + '  热度：' + str(data['list']['4']['hot']) + '\n5.' + data['list']['5']['name'] + '  热度：' + str(data['list']['5']['hot']) + '\n6.' + data['list']['6']['name'] + '  热度：' + str(data['list']['6']['hot']) + '\n7.' + data['list']['7']['name'] + '  热度：' + str(data['list']['7']['hot']) + '\n8.' + data['list']['8']['name'] + '  热度：' + str(data['list']['8']['hot']) + '\n9.' + data['list']['9']['name'] + '  热度：' + str(data['list']['9']['hot']) + '\n10.' + data['list']['10']['name'] + '  热度：' + str(data['list']['10']['hot'])
        await context.edit(res, parse_mode='html', link_preview=True)
    else:
        await context.edit("出错了呜呜呜 ~ 无法访问到 API 服务器 。")
