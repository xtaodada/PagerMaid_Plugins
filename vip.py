from pagermaid import bot
from pagermaid.listener import listener
from pagermaid.utils import obtain_message

@listener(is_plugin=True, outgoing=True, command="weather",
          description="使用彩云天气 api 查询国内实时天气。",
          parameters="<城市>")
async def weather(context):
    await context.edit("获取中 . . .")
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    async with bot.conversation('PagerMaid_Modify_bot') as conversation:
        await conversation.send_message('/weather ' + message)
        chat_response = await conversation.get_response()
        await bot.send_read_acknowledge(conversation.chat_id)
        weather_text = chat_response.text
    await context.edit(weather_text)
