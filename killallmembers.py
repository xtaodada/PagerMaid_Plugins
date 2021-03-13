""" PagerMaid Plugin killallmembers """
from asyncio import sleep
from telethon.tl.types import ChannelParticipantsAdmins
from pagermaid.listener import listener

@listener(is_plugin=True, outgoing=True, command="killallmembers",
          description="⚠⚠慎用! 一件扬了群内所有成员⚠⚠")
async def killallmembers(context):
    """ PagerMaid Plugin killallmembers """
    await context.edit('正在准备扬了这个破群的所有人...')
    chat = await context.get_chat()
    if not context.is_group:
        await context.edit('发生错误,请在群组中运行本命令。')
        await sleep(10)
        await context.delete()
        return False
    else:
        try:
            chat = await context.get_chat()
            admins = await context.client.get_participants(chat, filter=ChannelParticipantsAdmins)
            users = await context.client.get_participants(chat)
            admins_ids = [a.id for a in admins]
            users_ids = [u.id for u in users]
            users_wo_admins = list(set(users_ids).difference(set(admins_ids)))
        except:
            await context.edit('发生错误,无法获取本群名单。')
            await sleep(10)
            await context.delete()
            return False

        if context.sender.id in admins_ids:
            i = 0
            for user_id in users_wo_admins:
                try:
                    await context.client.edit_permissions(context.chat_id, user_id, view_messages=False)
                    i += 1
                    if i == len(users_wo_admins):
                        await context.edit(f'完成！\n进度:{i}/{len(users_wo_admins)}')
                    elif (i < 10) or (i % 10 == 0):
                        await context.edit(f'进度:{i}/{len(users_wo_admins)}'
                        "{'percent: {:.0f}%'.format(i/len(users_wo_admins))")
                except:
                    await context.edit('发生错误')
                    await sleep(10)
                    await context.delete()
            await sleep(5)
            await context.delete()
        else:
            await context.edit('你又不是管理员,你在这儿干个屁?')
            await sleep(10)
            await context.delete()
