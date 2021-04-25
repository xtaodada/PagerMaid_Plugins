""" PagerMaid module to handle sticker collection. """

from PIL import Image
from os.path import exists
from os import remove
from requests import get
from random import randint
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from struct import error as StructError
from pagermaid.listener import listener

positions = {
    "1": [297, 288],
    "2": [85, 368],
    "3": [127, 105],
    "4": [76, 325],
    "5": [256, 160],
}
max_number = 5


def eat_it(base, mask, photo, number):
    mask_size = mask.size
    photo_size = photo.size
    if mask_size[0] < photo_size[0] and mask_size[1] < photo_size[1]:
        scale = photo_size[1] / mask_size[1]
        photo = photo.resize((int(photo_size[0] / scale), int(photo_size[1] / scale)), Image.LANCZOS)
    photo = photo.crop((0, 0, mask_size[0], mask_size[1]))
    mask1 = Image.new('RGBA', mask_size)
    mask1.paste(photo, mask=mask)
    base.paste(mask1, (positions[str(number)][0], positions[str(number)][1]), mask1)
    temp = base.size[0] if base.size[0] > base.size[1] else base.size[1]
    if temp != 512:
        scale = 512 / temp
        base = base.resize((int(base.size[0] * scale), int(base.size[1] * scale)), Image.LANCZOS)
    return base


@listener(is_plugin=True, outgoing=True, command="eat",
          description="生成一张 吃头像 图片，（可选：当第二个参数存在时，旋转用户头像 180°）",
          parameters="<username/uid> [随意内容]")
async def eat(context):
    if len(context.parameter) > 2:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    diu_round = False
    await context.edit("正在生成 吃头像 图片中 . . .")
    if context.reply_to_msg_id:
        reply_message = await context.get_reply_message()
        user_id = reply_message.sender_id
        target_user = await context.client(GetFullUserRequest(user_id))
        if len(context.parameter) == 1:
            diu_round = True
    else:
        if len(context.parameter) == 1 or len(context.parameter) == 2:
            user = context.parameter[0]
            if user.isnumeric():
                user = int(user)
        else:
            user_object = await context.client.get_me()
            user = user_object.id
        if context.message.entities is not None:
            if isinstance(context.message.entities[0], MessageEntityMentionName):
                return await context.client(GetFullUserRequest(context.message.entities[0].user_id))
        try:
            user_object = await context.client.get_entity(user)
            target_user = await context.client(GetFullUserRequest(user_object.id))
        except (TypeError, ValueError, OverflowError, StructError) as exception:
            if str(exception).startswith("Cannot find any entity corresponding to"):
                await context.edit("出错了呜呜呜 ~ 指定的用户不存在。")
                return
            if str(exception).startswith("No user has"):
                await context.edit("出错了呜呜呜 ~ 指定的道纹不存在。")
                return
            if str(exception).startswith("Could not find the input entity for") or isinstance(exception, StructError):
                await context.edit("出错了呜呜呜 ~ 无法通过此 UserID 找到对应的用户。")
                return
            if isinstance(exception, OverflowError):
                await context.edit("出错了呜呜呜 ~ 指定的 UserID 已超出长度限制，您确定输对了？")
                return
            raise exception
    photo = await context.client.download_profile_photo(
        target_user.user.id,
        "plugins/eat/" + str(target_user.user.id) + ".jpg",
        download_big=True
    )
    reply_to = context.message.reply_to_msg_id
    if exists("plugins/eat/" + str(target_user.user.id) + ".jpg"):
        for num in range(1, max_number + 1):
            print(num)
            if not exists('plugins/eat/eat' + str(num) + '.png'):
                re = get('https://raw.githubusercontent.com/FlowerSilent/Photo/master/photo/eat' + str(num) + '.png')
                with open('plugins/eat/eat' + str(num) + '.png', 'wb') as bg:
                    bg.write(re.content)
            if not exists('plugins/eat/mask' + str(num) + '.png'):
                re = get('https://raw.githubusercontent.com/FlowerSilent/Photo/master/photo/mask' + str(num) + '.png')
                with open('plugins/eat/mask' + str(num) + '.png', 'wb') as ms:
                    ms.write(re.content)
        number = randint(1, max_number)
        markImg = Image.open("plugins/eat/" + str(target_user.user.id) + ".jpg")
        eatImg = Image.open("plugins/eat/eat" + str(number) + ".png")
        maskImg = Image.open("plugins/eat/mask" + str(number) + ".png")
        if len(context.parameter) == 2:
            diu_round = True
        if diu_round:
            markImg = markImg.rotate(180)  # 对图片进行旋转
        result = eat_it(eatImg, maskImg, markImg, number)
        result.save('plugins/eat/eat.webp')
        target_file = await context.client.upload_file("plugins/eat/eat.webp")
        try:
            remove("plugins/eat/" + str(target_user.user.id) + ".jpg")
            remove("plugins/eat/" + str(target_user.user.id) + ".png")
            remove("plugins/eat/eat.webp")
            remove(photo)
        except:
            pass
    else:
        await context.edit("此用户未设置头像或头像对您不可见。")
        return
    if reply_to:
        try:
            await context.client.send_file(
                context.chat_id,
                target_file,
                link_preview=False,
                force_document=False,
                reply_to=reply_to
            )
            await context.delete()
            remove("plugins/eat/eat.webp")
            try:
                remove(photo)
            except:
                pass
            return
        except TypeError:
            await context.edit("此用户未设置头像或头像对您不可见。")
    else:
        try:
            await context.client.send_file(
                context.chat_id,
                target_file,
                link_preview=False,
                force_document=False
            )
            await context.delete()
            remove("plugins/eat/eat.webp")
            try:
                remove(photo)
            except:
                pass
            return
        except TypeError:
            await context.edit("此用户未设置头像或头像对您不可见。")
