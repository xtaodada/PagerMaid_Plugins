import json
from os import remove, mkdir
from os.path import isfile, exists
from telethon.tl.types import ChannelParticipantsAdmins

extra_path = "plugins/keyword_func/extra"


def get_data(filename):
    filepath = f"{extra_path}/{filename}"
    if exists(filepath):
        with open(filepath, "r") as f:
            data = f.read()
        return data
    else:
        return ""


def write_data(filename, data):
    filepath = f"{extra_path}/{filename}"
    with open(filepath, "w") as f:
        f.write(data)


def init_file(filename):
    if exists(extra_path):
        if isfile(extra_path):
            remove(extra_path)
            mkdir(extra_path)
    else:
        mkdir(extra_path)
    if not exists(f"{extra_path}/{filename}"):
        with open(f"{extra_path}/{filename}", "w") as f:
            f.write("{}")


async def main(context):
    try:
        chat_id = context.chat_id
        if chat_id < 0:
            admins = await context.client.get_participants(context.chat, filter=ChannelParticipantsAdmins)
            text = context.text
            if not text:
                text = ""
            if text.split()[0] == "/add":
                if context.sender in admins:
                    try:
                        parse = text.split("\n")
                        parse[0] = " ".join(parse[0].split()[1:])
                        init_file(f"newkeyword_{chat_id}.json")
                        data = json.loads(get_data(f"newkeyword_{chat_id}.json"))
                        data[parse[0]] = parse[1]
                        write_data(f"newkeyword_{chat_id}.json", json.dumps(data))
                        await context.client.send_message(chat_id, "设置成功", reply_to=context.id)
                    except:
                        await context.client.send_message(chat_id, "设置失败", reply_to=context.id)
                else:
                    await context.client.send_message(chat_id, "您无权进行此操作", reply_to=context.id)
            elif text.split()[0] == "/del":
                if context.sender in admins:
                    try:
                        init_file(f"newkeyword_{chat_id}.json")
                        data = json.loads(get_data(f"newkeyword_{chat_id}.json"))
                        del data[" ".join(text.split(" ")[1:])]
                        write_data(f"newkeyword_{chat_id}.json", json.dumps(data))
                        await context.client.send_message(chat_id, "删除成功", reply_to=context.id)
                    except:
                        await context.client.send_message(chat_id, "删除失败", reply_to=context.id)
                else:
                    await context.client.send_message(chat_id, "您无权进行此操作", reply_to=context.id)
            elif text.split()[0] == "/list":
                if context.sender in admins:
                    try:
                        init_file(f"newkeyword_{chat_id}.json")
                        data = json.loads(get_data(f"newkeyword_{chat_id}.json"))
                        message = ""
                        count = 1
                        for k, v in data.items():
                            message += f"`{count}` : `{k}` -> `{v}`\n"
                            count += 1
                        await context.client.send_message(context.sender_id, message)
                        await context.client.send_message(chat_id, "已发送私聊", reply_to=context.id)
                    except:
                        await context.client.send_message(chat_id, "获取失败", reply_to=context.id)
                else:
                    await context.client.send_message(chat_id, "您无权进行此操作", reply_to=context.id)
            else:
                data = json.loads(get_data(f"newkeyword_{chat_id}.json"))
                for k, v in data.items():
                    if k in text:
                        await context.client.send_message(chat_id, v, reply_to=context.id)
        return ""
    except:
        return ""
