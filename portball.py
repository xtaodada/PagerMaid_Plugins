from pagermaid import bot, log
from pagermaid.listener import listener
from telethon.errors import rpcerrorlist
from asyncio import sleep            
from datetime import timedelta
from telethon.tl.types import ChannelParticipantsAdmins


@listener(is_plugin=True, outgoing=True, incoming=True, command="portball",
          description="回复你要临时禁言的人的消息来实现XX秒的禁言",
          parameters="<理由>(空格)<时间/秒>")
async def portball(context):
    if context.is_group:
        admins = await context.client.get_participants(context.chat, filter=ChannelParticipantsAdmins)
        reply = await context.get_reply_message()
        # if message sender is one of admins or group anonymous bot
        if (context.sender in admins) or (context.sender_id == 1087968824):
            # if this msg reply to a message
            if reply:
                action = context.arguments.split()
                # get sender's last_name
                if reply.sender.last_name == None:
                    last_name = ''
                else:
                    last_name = reply.sender.last_name
                # if something wrong with the command
                if len(action) < 2:
                    notification = await bot.send_message(context.chat_id, '格式是\n-portball 理由 秒数\n真蠢', reply_to = context.id)
                    await sleep(10)
                    await notification.delete()
                    try:
                        await context.delete()
                    except:
                        pass
                    return False
                # if time of portball less than 60 seconds
                if int(action[1])<60:
                    notification = await bot.send_message(context.chat_id, '诶呀不要小于60秒啦', reply_to = context.id)
                    await sleep(10)
                    await notification.delete()
                    try:
                        await context.delete()
                    except:
                        pass
                    return False
                # portball
                try:
                    await bot.edit_permissions(context.chat_id, reply.sender.id, timedelta(seconds=int(action[1].replace(' ',''))), send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, send_polls=False, invite_users=False, change_info=False, pin_messages=False)
                    portball_message = await bot.send_message(
                        context.chat_id,
                        f'[{reply.sender.first_name}{last_name}](tg://user?id={reply.sender.id}) 由于 {action[0]} 被塞了{action[1]}秒口球.\n'
                        f'到期自动拔出,无后遗症.',
                        reply_to = reply.id
                    )
                    await context.delete()
                    await sleep(int(action[1].replace(' ','')))
                    await portball_message.delete()
                except rpcerrorlist.UserAdminInvalidError:
                    notification = await bot.send_message(context.chat_id, '错误：我没有管理员权限或我的权限比被封禁的人要小', reply_to = context.id)
                    await sleep(10)
                    await notification.delete()
                except rpcerrorlist.ChatAdminRequiredError:
                    notification = await bot.send_message(context.chat_id, '错误：我没有管理员权限或我的权限比被封禁的人要小', reply_to = context.id)
                    await sleep(10)
                    await notification.delete()

            # if not reply to any message
            else:
                notification = await bot.send_message(context.chat_id, '你好蠢诶，都没有回复人，我哪知道你要搞谁的事情……', reply_to = context.id)
                await sleep(10)
                await notification.delete()
        # if sender is not admin
        else:
            return
    else:
        notification = await bot.send_message(context.chat_id, '你好蠢诶，又不是群组，怎么禁言啦！', reply_to = context.id)
        await sleep(10)
        await notification.delete()
    try:
        await context.delete()
    except:
        pass
