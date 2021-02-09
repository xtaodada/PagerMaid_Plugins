""" PagerMaid module for different ways to avoid users. """

from pyrogram import Client, filters
from main import cmd, par, des, prefix_str, redis
from modules.status import redis_status
from modules.plugin import check_require


incoming_load, incoming_load_text = check_require('incoming', '0.1')
cmd.extend(['ghost'])
par.extend(['<true|false|status>'])
des.extend(['开启对话的自动已读，需要 Redis。'])


@Client.on_message(filters.me & filters.command('ghost', list(prefix_str)))
async def ghost(client, message):
    """ Toggles ghosting of a user. """
    if not redis_status():
        await message.edit("出错了呜呜呜 ~ Redis 好像离线了，无法执行命令。")
        return
    if not incoming_load:
        await message.edit(incoming_load_text)
        return
    if len(message.text.split()) != 2:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    myself = await client.get_me()
    self_user_id = myself.id
    if message.text.split()[1] == "true":
        if message.chat.id == self_user_id:
            await message.edit("在？为什么要在收藏夹里面用？")
            return
        redis.set("ghosted.chat_id." + str(message.chat.id), "true")
        await message.delete()
    elif message.text.split()[1] == "false":
        if message.chat.id == self_user_id:
            await message.edit("在？为什么要在收藏夹里面用？")
            return
        try:
            redis.delete("ghosted.chat_id." + str(message.chat.id))
        except:
            await message.edit("emm...当前对话不存在于自动已读对话列表中。")
            return
        await message.delete()
    elif message.text.split()[1] == "status":
        if redis.get("ghosted.chat_id." + str(message.chat.id)):
            await message.edit("emm...当前对话存在于自动已读对话列表中。")
        else:
            await message.edit("emm...当前对话不存在于自动已读对话列表中。")
    else:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")


cmd.extend(['deny'])
par.extend(['<true|false|status>'])
des.extend(['拒绝聊天功能，需要 Redis。'])


@Client.on_message(filters.me & filters.command('deny', list(prefix_str)))
async def deny(client, message):
    """ Toggles denying of a user. """
    if not redis_status():
        await message.edit("出错了呜呜呜 ~ Redis 离线，无法运行。")
        return
    if not incoming_load:
        await message.edit(incoming_load_text)
        return
    if len(message.text.split()) != 2:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    myself = await client.get_me()
    self_user_id = myself.id
    if message.text.split()[1] == "true":
        if message.chat.id == self_user_id:
            await message.edit("在？为什么要在收藏夹里面用？")
            return
        redis.set("denied.chat_id." + str(message.chat.id), "true")
        await message.delete()
    elif message.text.split()[1] == "false":
        if message.chat.id == self_user_id:
            await message.edit("在？为什么要在收藏夹里面用？")
            return
        redis.delete("denied.chat_id." + str(message.chat.id))
        await message.delete()
    elif message.text.split()[1] == "status":
        if redis.get("denied.chat_id." + str(message.chat.id)):
            await message.edit("emm...当前对话已被加入自动拒绝对话列表中。")
        else:
            await message.edit("emm...当前对话已从自动拒绝对话列表移除。")
    else:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
