""" Pagermaid currency exchange rates plugin. Plugin by @fruitymelon and @xtaodada """

import sys
import urllib.request
from main import bot, reg_handler, des_handler, par_handler

imported = True
API = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
currencies = []
rates = {}


def init():
    with urllib.request.urlopen(API) as response:
        result = response.read()
        try:
            global rate_data, rates
            rate_data = xmltodict.parse(result)
            rate_data = rate_data['gesmes:Envelope']['Cube']['Cube']['Cube']
            for i in rate_data:
                currencies.append(i['@currency'])
                rates[i['@currency']] = float(i['@rate'])
            currencies.sort()
        except Exception as e:
            raise e


try:
    import xmltodict

    init()
except ImportError:
    imported = False


def logsync(message):
    sys.stdout.writelines(f"{message}\n")


logsync("rate: loading... If failed, please install xmltodict first.")


async def rate(message, args, origin_text):
    if not imported:
        await context.edit("请先安装依赖：`python3 -m pip install xmltodict`\n随后，请重启 pagermaid beta 。")
        return
    if len(message.text.split()) == 1:
        await message.edit(
            f"这是货币汇率插件\n\n使用方法: `-rate <FROM> <TO> <NB>`\n\n支持货币: \n{', '.join(currencies)}")
        return
    if len(message.text.split()) != 4:
        await message.edit(f"使用方法: `-rate <FROM> <TO> <NB>`\n\n支持货币: \n{', '.join(currencies)}")
        return
    FROM = message.text.split()[1].upper().strip()
    TO = message.text.split()[2].upper().strip()
    try:
        NB = float(message.text.split()[3].strip())
    except:
        NB = 1.0
    if currencies.count(FROM) == 0:
        await message.edit(
            f"{FROM}不是支持的货币. \n\n支持货币: \n{', '.join(currencies)}")
        return
    if currencies.count(TO) == 0:
        await message.edit(f"{TO}不是支持的货币. \n\n支持货币: \n{', '.join(currencies)}")
        return
    rate_num = round(rates[TO] / rates[FROM] * NB, 2)
    await message.edit(f'{FROM} : {TO} = {NB} : {rate_num}')


reg_handler('rate', rate)
des_handler('rate', '货币汇率。')
par_handler('rate', '<FROM> <TO> <NB>')
