from time import sleep
from os.path import exists
from os import mkdir, remove
from pagermaid import redis, log, redis_status
from pagermaid.listener import listener

@listener(is_plugin=True, outgoing=True, command="aff",
          description="在别人要打算买机场的时候光速发出自己的aff信息(请尽量配合短链接)",
          parameters="<save|remove> (可选，用于保存|删除aff信息)")
async def aff(context):
    if not context.parameter: #发送aff信息
        try:
            with open("plugins/AffExtra/aff.txt", "r", encoding="UTF-8") as f:
                msg = f.read()
        except:
            msg = ""
        if msg == "":
            await context.edit("出错了呜呜呜 ~ Aff消息不存在。\n(你有提前保存好嘛？)")
            return
        try:
            await context.edit(msg, link_preview=True)
        except:
            await context.edit("出错了呜呜呜 ~ 信息无变化。")
            sleep(3)
            await context.delete()
    elif context.parameter[0] == "save": #保存aff信息
        reply = await context.get_reply_message()
        if not reply:
            await context.edit("出错了呜呜呜 ~ 请回复一条消息以保存新的Aff信息。")
            return
        msg = reply.message
        if not exists("plugins/AffExtra"):
            mkdir("plugins/AffExtra")
        with open("plugins/AffExtra/aff.txt", "w", encoding="UTF-8") as f:
            f.write(msg)
        await context.edit("好耶 ！ Aff信息保存成功。")
        sleep(3)
        await context.delete()
    elif context.parameter[0] == "remove": #删除aff信息
        try:
            remove("plugins/AffExtra/aff.txt")
            await context.edit("好耶 ！ Aff信息删除成功。")
        except:
            await context.edit("出错了呜呜呜 ~ Aff信息删除失败。")
        sleep(3)
        await context.delete()
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        sleep(3)
        await context.delete()