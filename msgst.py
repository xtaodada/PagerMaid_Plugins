import asyncio
from pagermaid import bot, redis, redis_status
from pagermaid.listener import listener

def is_num(x: str):
    try:
        x = int(x)
        return isinstance(x, int)
    except ValueError:
        return False

def get_bot():
    data = [1527463252, "msg_schedule_bot"]
    if redis_status():
        n_id = redis.get("msgst.bot_id")
        n_un = redis.get("msgst.bot_un")
        if n_id and is_num(str(n_id, "ascii")): data[0] = int(str(n_id, "ascii"))
        if n_un: data[1] = str(n_un, "ascii")
    return data

async def del_msg(context, t_lim):
    await asyncio.sleep(t_lim)
    await context.delete()

@listener(is_plugin=True, outgoing=True, command="msgst",
          description="消息每天定时发送",
          parameters="new <time> <text>` 或 `del <msg_id>` 或 `list")
async def process(context):
    params = []
    for p in context.parameter:
        if len(p.split()) != 0:
            params.append(p)
    bot_data = get_bot()
    if len(params) == 1 and params[0] == "bot":
        await context.edit(str(bot_data))
        await del_msg(context, 10)
        return
    if len(params) >= 3 and params[0] == "new": params.insert(2, str(context.chat_id))
    async with bot.conversation(bot_data[1]) as conversation:
        await conversation.send_message("/" + " ".join(params))
        response = await conversation.get_response()
        await bot.send_read_acknowledge(conversation.chat_id)
        await context.edit(response.text)
    if len(params) > 0 and params[0] != "list": await del_msg(context, 10)

@listener(is_plugin=True, outgoing=True, command="msgset",
          description="定时发送 bot 服务端设置",
          parameters="bot <bot_id> <bot_username>` 或 `bot clear")
async def settings(context):
    if not redis_status():
        await context.edit("出错了呜呜呜 ~ Redis 离线，无法运行")
        await del_msg(context, 10)
        return
    params = []
    for p in context.parameter:
        if len(p.split()) != 0:
            params.append(p)
    if len(params) > 0 and params[0] == "bot":
        if len(params) == 3 and is_num(params[1]):
            redis.set("msgst.bot_id", params[1])
            redis.set("msgst.bot_un", params[2])
            await context.edit("设置成功")
            await del_msg(context, 10)
        elif len(params) == 2 and params[1] == "clear":
            redis.delete("msgst.bot_id")
            redis.delete("msgst.bot_un")
            await context.edit("清除成功")
            await del_msg(context, 10)
    else:
        await context.edit("参数错误")
        await del_msg(context, 10)

@listener(incoming=True, ignore_edited=True)
async def sendmsg(context):
    bot_data = get_bot()
    if context.sender_id == bot_data[0]:
        parse = context.text.split("|")
        if parse[0] == "send_msg":
            async with bot.conversation(bot_data[1]) as conversation:
                await bot.send_read_acknowledge(conversation.chat_id)
            await bot.send_message(int(parse[1]), "|".join(parse[2:]))
