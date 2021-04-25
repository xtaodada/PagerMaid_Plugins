""" Pagermaid currency exchange rates plugin. Plugin by @fruitymelon and @xtaodada"""

import asyncio, json, time
from json.decoder import JSONDecodeError
import urllib.request
from pagermaid.listener import listener, config
from pagermaid import log

# i18n 
## 默认语言
lang_rate = {"des": "货币汇率插件", "arg": "<FROM> <TO> <NUM>", "help": "这是货币汇率插件\n\n使用方法: `-rate <FROM> <TO> <NUM>，其中 <NUM> 是可省略的`\n\n支持货币: \n", "nc": "不是支持的货币. \n\n支持货币: \n", "notice": "数据每日更新，建议使用 bc 插件查看加密货币汇率", "warning": "数据每日更新"}
## 其他语言
if config["application_language"] == "en":
    lang_rate = {"des": "Currency exchange rate plugin", "arg": "<FROM> <TO> <NUM>", "help": "Currency exchange rate plugin\n\nUsage: `-rate <FROM> <TO> <NUM> where <NUM> is optional`\n\nAvailable currencies: \n", "nc": "is not available.\n\nAvailable currencies: \n", "notice": "Data are updated daily, for encrypted currencies we recommend to use the `bc` plugin.", "warning": "Data are updated daily"}


API = "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies.json"
currencies = []
data = {}

inited = False


def init():
  with urllib.request.urlopen(API) as response:
    result = response.read()
    try:
      global data
      data = json.loads(result)
      for key in list(enumerate(data)):
        currencies.append(key[1].upper())
      currencies.sort()
    except JSONDecodeError as e:
      raise e
    global inited
    inited = True


init()
last_init = time.time()

@listener(incoming=True, ignore_edited=True)
async def refresher(context):
  global last_init
  if time.time() - last_init > 24 * 60 * 60:
    # we'd better do this to prevent ruining the log file with massive fail logs
    # as this `refresher` would be called frequently
    last_init = time.time()
    try:
      init()
    except Exception as e:
      await log(f"Warning: plugin rate failed to refresh rates data. {e}")

@listener(is_plugin=True, outgoing=True, command="rate",
          description=lang_rate["des"],
          parameters=lang_rate["arg"])
async def rate(context):
  if not inited:
    init()
  if not inited:
    return
  if not context.parameter:
    await context.edit(f"{lang_rate['help']}`{', '.join(currencies)}`\n\n{lang_rate['notice']}")
    return
  NB = 1.0
  if len(context.parameter) != 3:
    if len(context.parameter) != 2:
      await context.edit(f"{lang_rate['help']}`{', '.join(currencies)}`\n\n{lang_rate['notice']}")
      return
  FROM = context.parameter[0].upper().strip()
  TO = context.parameter[1].upper().strip()
  try:
    NB = NB if len(context.parameter) == 2 else float(context.parameter[2].strip())
  except:
    NB = 1.0
  if currencies.count(FROM) == 0:
    await context.edit(f"{FROM}{lang_rate['nc']}`{', '.join(currencies)}`")
    return
  if currencies.count(TO) == 0:
    await context.edit(f"{TO}{lang_rate['nc']}{', '.join(currencies)}`")
    return
  endpoint = f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{FROM.lower()}/{TO.lower()}.json"
  with urllib.request.urlopen(endpoint) as response:
    result = response.read()
    try:
      rate_data = json.loads(result)
      await context.edit(f'`{FROM} : {TO} = {NB} : {round(NB * rate_data[TO.lower()], 4)}`\n\n{lang_rate["warning"]}')
    except Exception as e:
      await context.edit(str(e))
