""" PagerMaid Plugins Paolu """
#   ______          _
#   | ___ \        | |
#   | |_/ /__ _ __ | |_ __ _  ___ ___ _ __   ___
#   |  __/ _ \ '_ \| __/ _` |/ __/ _ \ '_ \ / _ \
#   | | |  __/ | | | || (_| | (_|  __/ | | |  __/
#   \_|  \___|_| |_|\__\__,_|\___\___|_| |_|\___|
#

from asyncio import sleep
from pagermaid.listener import listener

@listener(is_plugin=True, outgoing=True, command="paolu",
          description="⚠一键跑路 删除群内消息并禁言⚠")
async def paolu(context):
    """一键跑路 删除群内消息并禁言"""
    try:
        await context.client.edit_permissions(
                            entity=context.chat_id,
                            send_messages=False,
                            send_media=False,
                            send_stickers=False,
                            send_gifs=False,
                            send_games=False,
                            send_inline=False,
                            send_polls=False,
                            invite_users=False,
                            change_info=False,
                            pin_messages=False)
    except:
        pass
    await context.client.delete_messages(context.chat_id, list(range(1,context.message.id)))
    try:
        await context.client.edit_permissions(
                            entity=context.chat_id,
                            send_messages=False)
    except:
        pass
    await context.edit("Finished")
    await sleep(10)
    await context.delete()
