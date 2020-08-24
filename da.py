from asyncio import sleep
from pagermaid import log
from pagermaid.listener import listener

@listener(is_plugin=True, outgoing=True, command="da",
          description="以此命令删除所有消息。（非群组管理员只删除自己的消息）",
          parameters="<text>")
async def prune(context):
    if len(context.parameter) > 2 or len(context.parameter) == 0:
        await context.edit("\n呜呜呜，请执行 `-da true` 来删除所有消息。")
        return
    if context.parameter[0] != "true":
        await context.edit("\n呜呜呜，请执行 `-da true` 来删除所有消息。")
        return
    await context.edit('正在删除所有消息 . . .')
    input_chat = await context.get_input_chat()
    messages = []
    count = 0
    async for message in context.client.iter_messages(input_chat, min_id=1):
        messages.append(message)
        count += 1
        messages.append(1)
        if len(messages) == 100:
            await context.client.delete_messages(input_chat, messages)
            messages = []

    if messages:
        await context.client.delete_messages(input_chat, messages)
    await log(f"批量删除了 {str(count)} 条消息。")
    notification = await send_prune_notify(context, count)
    await sleep(.5)
    await notification.delete()

async def send_prune_notify(context, count):
    return await context.client.send_message(
        context.chat_id,
        "批量删除了 "
        + str(count)
        + " 条消息。"
    )
