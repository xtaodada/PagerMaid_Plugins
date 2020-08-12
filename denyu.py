""" PagerMaid module for different ways to avoid users. """

# Plugin by fruitymelon

from pagermaid import redis, log, redis_status
from pagermaid.listener import listener

@listener(is_plugin=True, outgoing=True, command="denyu",
          description="在某群中强制禁言某用户，需要删除他人消息权限，需要 redis。强制禁言全群请使用 `-deny`。",
          parameters="<userid> <true|false|status> 或直接回复用户并指定 <true|false|status>")
async def denyu(context):
    """ Toggles denying of a user. """
    if not redis_status():
        await context.edit("出错了呜呜呜 ~ Redis 离线，无法运行。")
        return
    myself = await context.client.get_me()
    self_user_id = myself.id
    uid = None
    offset = 0
    if len(context.parameter) != 2:
        reply_to_msg = await context.get_reply_message()
        if not reply_to_msg:
            await context.edit("在某群中强制禁言某用户，需要删除他人消息权限，需要 redis。用法：回复某条消息，格式为 `-denyu <true|false|status>`")
            return
        uid = reply_to_msg.sender.id
        offset = 1
    else:
        uid = context.parameter[0]
    try:
        context.parameter[1 - offset]
    except IndexError:
        await context.edit("请指定参数 <true|false|status>！")
        return
    if context.parameter[1 - offset] == "true":
        if context.chat_id == self_user_id:
            await context.edit("在？为什么要在收藏夹里面用？")
            return
        redis.set(f"denieduser.{context.chat_id}.{uid}", "true")
        await context.delete()
        await log(f"ChatID {context.chat_id} UserID {uid} 已被添加到自动拒绝对话列表中。")
    elif context.parameter[1 - offset] == "false":
        if context.chat_id == self_user_id:
            await context.edit("在？为什么要在收藏夹里面用？")
            return
        redis.delete(f"denieduser.{context.chat_id}.{uid}")
        await context.delete()
        await log(f"ChatID {context.chat_id} UserID {uid} 已从自动拒绝对话列表中移除。")
    elif context.parameter[1 - offset] == "status":
        if redis.get(f"denieduser.{context.chat_id}.{uid}"):
            await context.edit("emm...当前对话的该用户已存在于自动拒绝对话列表中。")
        else:
            await context.edit("emm...当前对话不存在于自动拒绝对话列表中。")
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。只能为 `<true|false|status>`。")

@listener(incoming=True, ignore_edited=True)
async def message_removal_user(context):
    """ Event handler to infinitely delete denied messages. """
    if not redis_status():
        return
    uid = context.sender_id
    if redis.get(f"denieduser.{context.chat_id}.{uid}"):
        # 避免和 -deny 冲突
        if not redis.get(f"denied.chat_id.{context.chat_id}"):
            await context.delete()
