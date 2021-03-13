from requests import get
from os import remove
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


@listener(is_plugin=True, outgoing=True, command="pixiv",
          description="查询插画信息 （或者回复一条消息）",
          parameters="[<图片链接>] <图片序号>")
async def pixiv(context):
    await context.edit("获取中 . . .")
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    async with bot.conversation('PagerMaid_Modify_bot') as conversation:
        await conversation.send_message('/pixiv_api ' + message)
        chat_response = await conversation.get_response()
        await bot.send_read_acknowledge(conversation.chat_id)
        pixiv_text = chat_response.text
    pixiv_list = pixiv_text.split('|||||')
    if len(pixiv_list) == 2:
        pixiv_albums = pixiv_list[1].split('|||')
        pixiv_album = []
        await context.edit("下载图片中 . . .")
        for i in range(0, len(pixiv_albums)):
            r = get(pixiv_albums[i])
            with open("pixiv." + str(i) + ".jpg", "wb") as code:
                  code.write(r.content)
            pixiv_album.extend(["pixiv." + str(i) + ".jpg"])
        await context.client.send_file(context.chat_id, pixiv_album,
                                 caption=pixiv_list[0])
        await context.delete()
        for i in pixiv_album:
            try:
                remove(i)
            except:
                pass
    else:
        await context.edit(pixiv_text)
