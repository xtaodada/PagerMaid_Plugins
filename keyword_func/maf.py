from asyncio import sleep


async def del_msg(context, t):
    await sleep(t)
    try:
        await context.delete()
    except:
        pass


async def main(context, text, tgurl, mode=0, re=1, t=-1):
    ids = tgurl.split("/")[-2:]
    message = await context.client.get_messages(int(ids[0]), ids=int(ids[1]))
    re_id = context.id
    try:
        data = message.photo
    except:
        data = message.media.document
    if context.is_reply:
        me = await context.client.get_me()
        if context.sender.id == me.id:
            msg = await context.get_reply_message()
            re_id = msg.id
    sent = await context.client.send_message(context.chat_id, text, file=data, force_document=mode, reply_to=(re_id if re else None))
    if t >= 0:
        await del_msg(sent, t)
    return ""
