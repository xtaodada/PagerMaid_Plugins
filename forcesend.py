""" 在不进群的情况下，向频道的附属群内强制发送消息。 """

# By tg @fruitymelon

from pagermaid import log 
from pagermaid.listener import listener

helpmsg = """在不进群的情况下，强制向频道的附属群内发送消息。需要事先关注频道。
用法：`-forcesend 消息内容`

本插件用途狭窄，主要用于让别人以为你在群里。该群必须是频道的附属群，且你必须已经关注了对应的频道。

在该频道的任意一条消息的评论区，发送 `-forcesend 消息内容`，即可强行将文字发送到附属群内，但不出现在原频道消息的评论区中。

在普通群内使用 -forcesend 时，效果与直接发送消息基本没有区别。因此不做特殊判断。
"""

async def sendmsg(context, chat, origin_text):
    text = origin_text.strip()
    msg = await context.client.send_message(chat, text)
    return msg

@listener(is_plugin=True, outgoing=True, command="forcesend", diagnostics=True, ignore_edited=True,
          description=helpmsg,
          parameters="<text>")
async def forcesend(context):
    if not context.parameter:
        await context.edit(helpmsg)
        return
    chat = await context.get_chat()
    text = " ".join(context.parameter)
    await context.delete()
    await sendmsg(context, chat, text)
    return
