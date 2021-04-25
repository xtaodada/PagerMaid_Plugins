""" Pagermaid Plugins AutoReplySticker """
#   ______          _
#   | ___ \        | |
#   | |_/ /__ _ __ | |_ __ _  ___ ___ _ __   ___
#   |  __/ _ \ '_ \| __/ _` |/ __/ _ \ '_ \ / _ \
#   | | |  __/ | | | || (_| | (_|  __/ | | |  __/
#   \_|  \___|_| |_|\__\__,_|\___\___|_| |_|\___|
#

from os import mkdir
from os.path import exists
from asyncio import sleep
from random import randint
import yaml
from telethon.tl.custom.message import Message
from telethon.tl.functions.messages import GetAllStickersRequest
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID
from pagermaid import log
from pagermaid.listener import listener

async def ars_check(message: Message) -> None:
    try:
        config = yaml.load(open(r"./plugins/autoreplysticker/config.yml"), Loader=yaml.FullLoader)
    except FileNotFoundError:
        await message.edit("自动回复贴纸的相关设置不存在。\n请使用 `-ars help` 查看设置方法")
        return
    _sticker_id = config['sticker_id']
    _sticker_hash = config['sticker_hash']
    _num = config['num']
    _time = config['time']
    _white = config['whitelist']
    _noti = await message.reply(
        '您当前的设置为:\n'
        f'sticker_id: {_sticker_id}\n'
        f'sticker_hash: {_sticker_hash}\n'
        f'time: {_time}\n'
        f'num: {_num}\n'
        f'白名单群组id: {_white}\n'
        '\n'
        '本消息15秒后自动删除')
    await message.delete()
    await sleep(15)
    await _noti.delete()

async def ars_getall(message: Message) -> None:
    sticker_sets = await message.client(GetAllStickersRequest(0))
    sticker_pack_list = []
    for sticker_set in sticker_sets.sets:
        if len(sticker_pack_list) < 10:
            text = "我发现了一个Sticker Pack，名为\n" + sticker_set.title + "\n" + "ID为： `" + \
                str(sticker_set.id) + "` \n" + "Hash为： `" + str(sticker_set.access_hash) + \
                "` \n" + "共有" + str(sticker_set.count) + "张"
            sticker_pack_list.extend([text])
        else:
            sticker_pack_list_old = sticker_pack_list
            send_text = '\n\n'.join(sticker_pack_list_old)
            await message.client.send_message(message.chat_id, send_text)
            sticker_pack_list = []
            await sleep(2)
    sendtext = '\n\n'.join(sticker_pack_list)
    await message.client.send_message(message.chat_id, sendtext)
    await message.delete()

async def ars_help(message: Message) -> None:
    await message.reply(
        '欢迎使用自动回复贴纸\n'
        '设置方法为\n'
        '先使用 `-ars getall` 获取贴纸包的id和hash\n'
        '之后使用 `-ars set` 贴纸包id 贴纸包hash 自动删除时间 第i张贴纸 第j张贴纸 ...\n'
        '比如 `-ars set 000 001 10 0 1 2 3` 的意义为\n'
        '设置贴纸包id为000, hash为001, 自动回复10秒后删除, 随机从第0, 1, 2, 3张贴纸中选择一张自动回复\n\n'
        '如果您想要在某个群内设置自动回复白名单,请在该群中回复`-ars w`'
        '如有使用问题,请前往 [这里](https://t.me/PagerMaid_Modify) 请求帮助')
    await message.delete()

async def ars_whitelist(message: Message) -> None:
    chat_id = str(message.chat_id)
    try:
        config = yaml.load(open(r"./plugins/autoreplysticker/config.yml"), Loader=yaml.FullLoader)
    except FileNotFoundError:
        await message.edit("自动回复贴纸的相关设置不存在。\n请使用 `-ars help` 查看设置方法")
        return
    try:
        _white = config['whitelist']
    except:
        white_list = ['0']
        set_state('whitelist', white_list)
        _white = config['whitelist']
    
    _white.append(chat_id)
    try:
        _white.remove('0')
    except:
        pass
    _white = list(set(_white))
    set_state('whitelist', _white)
    _noti = await message.edit('OK')
    await sleep(5)
    await _noti.delete()

def set_state(name: str, state: list) -> None:
    file_name = "./plugins/autoreplysticker/config.yml"
    if exists(file_name):
        with open(file_name) as f:
            doc = yaml.safe_load(f)
        doc[name] = state
        with open(file_name, 'w') as f:
            yaml.safe_dump(doc, f, default_flow_style=False)
    else:
        dc = {name: state}
        with open(file_name, 'w', encoding='utf-8') as f:
            yaml.dump(dc, f)

def get_name(sender: Message.sender) -> str:
    """
    get_name(Message.sender)
    """
    username = sender.username 
    first_name = sender.first_name
    last_name = sender.last_name
    _id = sender.id
    if username == None:
        if last_name == None:
            name = f'[{first_name}](tg://user?id={_id})'
        else:
            name = f'[{first_name}{last_name}](tg://user?id={_id})'
    else:
        name = f'@{username}'
    return name

def process_link(chatid: int, msgid: int) -> str:
    """
    process_link(chat_id, message_id)
    return https://t.me/c/chat_id/message_id
    """
    if chatid < 0:
        if chatid < -1000000000000:
            chatid *= -1
            chatid -= 1000000000000
        else:
            chatid *= -1
    link = f'https://t.me/c/{chatid}/{msgid}'
    return link

@listener(is_plugin=True, outgoing=True, command="ars")
async def ars(context):
    if not exists('./plugins/autoreplysticker'):
        mkdir('./plugins/autoreplysticker')
    
    if len(context.parameter) == 0:
        await ars_help(context)
        return

    if context.parameter[0] == 'set':
        if len(context.parameter) < 5:
            await context.reply('请正确输入 `-ars set` <sticker_id> <sticker_hash> <time> <num>')
            await context.delete()
            return
        try:
            set_state('sticker_id', context.parameter[1])
            set_state('sticker_hash', context.parameter[2])
            set_state('time', context.parameter[3])
            num_list = []
            for i in range(4, len(context.parameter)):
                num_list.append(context.parameter[i])
            set_state('num', num_list)
            white_list = ['0']
            set_state('whitelist', white_list)
        except:
            await context.reply('设置失败,请手动设置`./plugins/autoreplysticker/config.yml`')
            return
        _noti = await context.reply('设置成功')
        await sleep(10)
        await _noti.delete()
        await ars_check(context)
    
    elif context.parameter[0] == 'check':
        await ars_check(context)
    elif context.parameter[0] == 'getall':
        await ars_getall(context)
    elif context.parameter[0] == 'help':
        await ars_help(context)
    elif context.parameter[0] == 'w':
        await ars_whitelist(context)

@listener(incoming=True, ignore_edited=True)
async def process_message(context):
    reply_user_id = 0
    link = process_link(context.chat_id, context.id)
    me = await context.client.get_me()
    try:
        reply = await context.get_reply_message()
        reply_user_id = reply.sender.id
        if context.sticker:
            return
        if context.chat_id > 0:
            return
    except:
        pass
    
    try:
        config = yaml.load(open(r"./plugins/autoreplysticker/config.yml"), Loader=yaml.FullLoader)
        _sticker_id = int(config['sticker_id'])
        _sticker_hash = int(config['sticker_hash'])
        _num = config['num']
        _time = int(config['time'])
        _whitelist = config['whitelist']
    except:
        return

    if str(context.chat_id) in _whitelist:
        return

    if (reply and reply_user_id == me.id):
        stickers = await context.client(
            GetStickerSetRequest(
                stickerset=InputStickerSetID(
                    id=_sticker_id, access_hash=_sticker_hash)))
        try:
            i = randint(0, len(_num)-1)
            sticker = await context.client.send_file(
                context.chat_id,
                stickers.documents[int(_num[i])],
                reply_to=context.id)
            await sleep(_time)
            await sticker.delete()
            await log(f'#被回复\n在 [{context.chat.title}]({process_link(context.chat_id, context.id)})\n获得了 {get_name(context.sender)} 的回复')
        except:
            pass
