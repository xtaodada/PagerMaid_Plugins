from telethon.tl.types import ChannelParticipantsAdmins
from pagermaid import bot
from pagermaid.listener import listener
from telethon.errors.rpcbaseerrors import BadRequestError
from os import remove
import re
import time

@listener(is_plugin=True, incoming=True, outgoing=True, command="atadmins",
          description="一键 AT 本群管理员（仅在群组中有效）",
          parameters="<要说的话>")
async def atadmins(context):
    await context.edit('正在获取管理员列表中...')
    chat = await context.get_chat()
    try:
        admins = await context.client.get_participants(chat, filter=ChannelParticipantsAdmins)
    except:
        await context.edit('请在群组中运行。')
        return True
    admin_list = []
    if context.arguments == '':
        say = '召唤本群所有管理员'
    else:
        say = context.arguments
    for admin in admins:
        if not admin.bot:
            if admin.username is not None:
                admin_list.extend(['@'+ admin.username])
            elif admin.first_name is not None:
                admin_list.extend(['[' + admin.first_name + '](tg://user?id=' + str(admin.id) + ')'])
    send_list = ' , '.join(admin_list)
    # print(send_list)
    await context.reply("%s：\n\n%s" % (say, send_list))
    # await context.reply(' , '.join(admin_list))
    await context.delete()

@listener(is_plugin=True, incoming=True, outgoing=True, command="atall",
          description="一键 AT 本群成员（仅在群组中有效）")
async def atall(context):
    await context.edit('正在获取成员列表中...')
    chat = await context.get_chat()
    try:
        users = await context.client.get_participants(chat)
    except:
        await context.edit('请在群组中运行。')
        return True
    user_list = []
    if context.arguments == '':
        say = '召唤本群所有成员'
    else:
        say = context.arguments
    for user in users:
        if not user.bot:
            if len(user_list) < 128:
                if user.username is not None:
                    user_list.extend(['@'+ user.username])
                elif user.first_name is not None:
                    user_list.extend(['[' + user.first_name + '](tg://user?id=' + str(user.id) + ')'])
            else:
                user_list_old = user_list
                text = ' , '.join(user_list_old)
                await context.reply("%s：\n\n%s" % (say, text))
                user_list = []
                time.sleep(1)
    text = ' , '.join(user_list)
    await context.reply("%s：\n\n%s" % (say, text))
    await context.delete()
