from pagermaid.listener import listener
#  from pagermaid import log
from telethon import functions, types


@listener(outgoing=True,
          command="nthmsg",
          description="获取你发送的第 n 条消息，默认为第一条",
          parameters="<n>")
async def nthmsg(context):
    await context.edit("获取中 . . .")

    try:
        n = int(context.parameter[0])
    except:
        n = 1

    m = object()
    async for m in context.client.iter_messages(context.chat_id,
                                                from_user="me",
                                                reverse=True,
                                                limit=n):
        pass
    r = await context.client(
        functions.channels.ExportMessageLinkRequest(channel=m.to_id,
                                                    id=m.id,
                                                    grouped=True))
    await context.edit(r.link)
