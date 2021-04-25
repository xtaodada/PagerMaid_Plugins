""" Module to automate message deletion. """
from asyncio import sleep
import time
import random
from time import strftime
from telethon.tl.functions.account import UpdateProfileRequest
from emoji import emojize
from pagermaid import bot, log
from pagermaid.listener import listener

dizzy = emojize(":dizzy:", use_aliases=True)
cake = emojize(":cake:", use_aliases=True)
all_time_emoji_name = ["clock12", "clock1230", "clock1", "clock130", "clock2", "clock230", "clock3", "clock330", "clock4", "clock430", "clock5", "clock530", "clock6", "clock630", "clock7", "clock730", "clock8", "clock830", "clock9", "clock930", "clock10", "clock1030", "clock11", "clock1130"]
time_emoji_symb = [emojize(":%s:" %s, use_aliases=True) for s in all_time_emoji_name]


@listener(is_plugin=True, outgoing=True, command="autochangename",
          description="每 30 秒更新一次 last_name")
async def change_name_auto(context):
    await context.delete()
    await log("开始每 30 秒更新一次 last_name")
    while True:
        try:
            time_cur = strftime("%H:%M:%S:%p:%a", time.localtime())
            hour, minu, seco, p, abbwn = time_cur.split(':')
            if seco == '00' or seco == '30':
                shift = 0
                mult = 1
                if int(minu) > 30: shift = 1
                # print((int(hour)%12)*2+shift)
                # hour symbols
                hsym = time_emoji_symb[(int(hour) % 12) * 2 + shift]
                # await client1.send_message('me', hsym)
                for_fun = random.random()
                if for_fun < 0.10:
                    last_name = '%s时%s分 %s' % (hour, minu, hsym)
                elif for_fun < 0.30:
                    last_name = '%s:%s %s %s %s' % (hour, minu, p, abbwn, hsym)
                elif for_fun < 0.60:
                    last_name = '%s:%s %s UTC+8 %s' % (hour, minu, p, hsym)
                elif for_fun < 0.90:
                    last_name = '%s' % dizzy
                else:
                    last_name = '%s' % cake

                await bot(UpdateProfileRequest(last_name=last_name))
        except:
            pass
        await sleep(1)
