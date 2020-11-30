""" Pagermaid currency exchange rates plugin. Plugin by @fruitymelon """

import asyncio, json
from json.decoder import JSONDecodeError
import urllib.request
from pagermaid.listener import listener

API = "https://api.exchangeratesapi.io/latest"
currencies = []
data = {}

inited = False


def init():
    with urllib.request.urlopen(API) as response:
        result = response.read()
        try:
            global data
            data = json.loads(result)
            data["rates"][data["base"]] = 1.0
            for key in list(enumerate(data["rates"])):
                currencies.append(key[1])
            currencies.sort()
        except JSONDecodeError as e:
            raise e
        global inited
        inited = True


init()


@listener(is_plugin=True, outgoing=True, command="rate",
          description="货币汇率插件",
          parameters="<FROM> <TO> <NB>")
async def rate(context):
    while not inited:
        await asyncio.sleep(1)
    if not context.parameter:
        await context.edit(
            f"这是货币汇率插件\n\n使用方法: `-rate <FROM> <TO> <NB>`\n\n支持货币: \n{', '.join(currencies)}")
        return
    if len(context.parameter) != 3:
        await context.edit(f"使用方法: `-rate <FROM> <TO> <NB>`\n\n支持货币: \n{', '.join(currencies)}")
        return
    FROM = context.parameter[0].upper().strip()
    TO = context.parameter[1].upper().strip()
    try:
        NB = float(context.parameter[2].strip())
    except:
        NB = 1.0
    if currencies.count(FROM) == 0:
        await context.edit(
            f"{FROM}不是支持的货币. \n\n支持货币: \n{', '.join(currencies)}")
        return
    if currencies.count(TO) == 0:
        await context.edit(f"{TO}不是支持的货币. \n\n支持货币: \n{', '.join(currencies)}")
        return
    await context.edit(f'{FROM} : {TO} = {NB} : {round(data["rates"][TO]/data["rates"][FROM]*NB,2)}')
