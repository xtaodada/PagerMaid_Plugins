from pyrogram import Client, filters
from main import redis
from modules.status import redis_status
from modules.plugin import check_plugin


if check_plugin('avoid'):
    avoid_incoming = True
if check_plugin('keyword'):
    from modules.plugins.keyword import auto_reply
    keyword_incoming = True


@Client.on_message(filters.incoming)
async def incoming(client, message):
    if not redis_status():
        return
    if avoid_incoming:
        if redis.get("ghosted.chat_id." + str(message.chat.id)):
            await client.read_history(message.chat.id)
        if redis.get("denied.chat_id." + str(message.chat.id)):
            await message.delete()
    if keyword_incoming:
        auto_reply(client, message)
