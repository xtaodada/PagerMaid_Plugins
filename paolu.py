""" PagerMaid Plugins Paolu """
from asyncio import sleep
from pagermaid import bot
from pagermaid.listener import listener

@listener(is_plugin=True, outgoing=True, command="paolu",
          description="⚠一键跑路 删除群内消息并禁言⚠")
async def paolu(context):
    """一键跑路 删除群内消息并禁言"""
    await bot.edit_permissions(
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
    await bot.delete_messages(context.chat_id, list(range(1,context.message.id)))
    await context.edit("Finished")
    await sleep(10)
    await context.delete()
