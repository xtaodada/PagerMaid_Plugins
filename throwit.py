""" PagerMaid module to handle sticker collection. """

from PIL import Image, ImageDraw, ImageFilter
from os.path import exists
from os import remove
from requests import get
from random import randint
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from struct import error as StructError
from pagermaid.listener import listener

def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def mask_circle_transparent(pil_img, blur_radius, offset=0):
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    result = pil_img.copy()
    result.putalpha(mask)
    return result

@listener(is_plugin=True, outgoing=True, command="diu",
          description="生成一张 扔头像 图片，（可选：当第二个参数存在时，旋转用户头像 180°）",
          parameters="<username/uid> [随意内容]")
async def throwit(context):
    if len(context.parameter) > 2:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    diu_round = False
    await context.edit("正在生成 扔头像 图片中 . . .")
    if context.reply_to_msg_id:
        reply_message = await context.get_reply_message()
        user_id = reply_message.from_id
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
              "plugins/throwit/" + str(target_user.user.id) + ".jpg",
              download_big=True
               )
    reply_to = context.message.reply_to_msg_id
    if exists("plugins/throwit/" + str(target_user.user.id) + ".jpg"):
        if not exists('plugins/throwit/1.png'):
            r = get('https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/throwit/1.png')
            with open("plugins/throwit/1.png", "wb") as code:
                code.write(r.content)
        if not exists('plugins/throwit/2.png'):
            r = get('https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/throwit/2.png')
            with open("plugins/throwit/2.png", "wb") as code:
                code.write(r.content)
        if not exists('plugins/throwit/3.png'):
            r = get('https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/throwit/3.png')
            with open("plugins/throwit/3.png", "wb") as code:
                code.write(r.content)
        # 随机数生成
        randint_r = randint(1,3)
        # 将头像转为圆形
        markImg = Image.open("plugins/throwit/" + str(target_user.user.id) + ".jpg")
        if randint_r == 1:
            thumb_width = 136
        elif randint_r == 2:
            thumb_width = 122
        elif randint_r == 3:
            thumb_width = 180
        im_square = crop_max_square(markImg).resize((thumb_width, thumb_width), Image.LANCZOS)
        im_thumb = mask_circle_transparent(im_square, 0)
        im_thumb.save("plugins/throwit/" + str(target_user.user.id) + ".png")
        # 将头像复制到模板上
        if randint_r == 1:
            background = Image.open("plugins/throwit/2.png")
        elif randint_r == 2:
            background = Image.open("plugins/throwit/1.png")
        elif randint_r == 3:
            background = Image.open("plugins/throwit/3.png")
        foreground = Image.open("plugins/throwit/" + str(target_user.user.id) + ".png")
        if len(context.parameter) == 2:
            diu_round = True
        if diu_round:
            foreground = foreground.rotate(180)  # 对图片进行旋转
        if randint_r == 1:
            background.paste(foreground, (19, 181), foreground)
        elif randint_r == 2:
            background.paste(foreground, (368, 16), foreground)
        elif randint_r == 3:
            background.paste(foreground, (331, 281), foreground)
        background.save('plugins/throwit/throwout.webp')
        target_file = await context.client.upload_file('plugins/throwit/throwout.webp')
        try:
            remove("plugins/throwit/" + str(target_user.user.id) + ".jpg")
            remove("plugins/throwit/" + str(target_user.user.id) + ".png")
            remove("plugins/throwit/throwout.webp")
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
            try:
                remove(photo)
            except:
                pass
            return
        except TypeError:
            await context.edit("此用户未设置头像或头像对您不可见。")