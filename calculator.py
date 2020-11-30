from pagermaid import log, bot
from pagermaid.listener import listener
from pagermaid.utils import attach_log, execute
@listener(is_plugin=False, outgoing=True, command="cal",
          description="计算",
          parameters="<加减乘除>")
async def cal(context):
    command = context.arguments
    if context.is_channel and not context.is_group:
        await context.edit("`出错了呜呜呜 ~ 当前 PagerMaid-Modify 的配置禁止在频道中执行此命令。`")
        return
        
    if not command:
        await context.edit("`出错了呜呜呜 ~ 无效的参数。`")
        return

    await context.edit(f"{command}" )
    cmd = f'echo "scale=4;{command}" | bc'
    result = await execute(cmd)

    if result:
        if len(result) > 4096:
            await attach_log(result, context.chat_id, "output.log", context.id)
            return

        await context.edit(f"{command}=\n`{result}`")
    else:
        return
