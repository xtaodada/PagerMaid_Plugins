import re, time, asyncio, requests, os, json
from io import BytesIO
from os import path, mkdir, remove, makedirs, chdir
from shutil import copyfile, move, rmtree
from uuid import uuid4
from base64 import b64encode, b64decode
from importlib import import_module
from pagermaid import bot, redis, log, redis_status, working_dir
from pagermaid.listener import listener

msg_freq = 1
group_last_time = {}
read_context = {}


def is_num(x: str):
    try:
        x = int(x)
        return isinstance(x, int)
    except ValueError:
        return False


def encode(s: str):
    return str(b64encode(s.encode('utf-8')), 'utf-8')


def decode(s: str):
    return str(b64decode(s.encode('utf-8')), 'utf-8')


def random_str():
    return str(uuid4()).replace('-', '')


def parse_rules(rules: str):
    n_rules = {}
    rules_parse = rules.split(";")
    for p in rules_parse:
        d = p.split(":")
        if len(d) == 2:
            key = decode(d[0])
            value = decode(d[1])
            n_rules[key] = value
    return n_rules


def save_rules(rules: dict, placeholder: str):
    n_rules = ""
    for k, v in rules.items():
        if placeholder:
            k = k.replace(placeholder, "'")
            v = v.replace(placeholder, "'")
        n_rules += encode(k) + ":" + encode(v) + ";"
    return n_rules


def validate(user_id: str, mode: int, user_list: list):
    if mode == 0:
        return user_id not in user_list
    elif mode == 1:
        return user_id in user_list
    else:
        return False


def get_redis(db_key: str):
    byte_data = redis.get(db_key)
    byte_data = byte_data if byte_data else b""
    byte_data = str(byte_data, "ascii")
    return parse_rules(byte_data)


def parse_multi(rule: str):
    sep_ph = random_str()
    col_ph = random_str()
    rule = rule.replace(r"\||", sep_ph)
    rule = rule.replace(r"\::", col_ph)
    rule = rule.split("||")
    n_rule = []
    for r in rule:
        p = r.split("::")
        p = [i.replace(sep_ph, "||") for i in p]
        p = [i.replace(col_ph, "::") for i in p]
        data = ['plain', '']
        if len(p) == 2:
            data = p
        else:
            data[1] = p[0]
        n_rule.append(data)
    return n_rule


def get_capture(search_data, group_name: str):
    try:
        capture_data = search_data.group(group_name)
        return capture_data
    except:
        return None


def get_rule(chat_id, rule_type, rule_index):
    rule_index = int(rule_index)
    rule_data = get_redis(f"keyword.{chat_id}.{rule_type}")
    index = 0
    for k in rule_data.keys():
        if index == rule_index:
            return encode(k)
        index += 1
    return None


def valid_time(chat_id):
    global msg_freq, group_last_time
    cus_freq = get_redis(f"keyword.{chat_id}.settings").get("freq", msg_freq)
    try:
        cus_freq = float(cus_freq)
    except:
        cus_freq = msg_freq
    n_time = time.time()
    chat_id = int(chat_id)
    if chat_id in group_last_time:
        if n_time - group_last_time[chat_id] >= cus_freq:
            return True
        else:
            return False
    else:
        return True


def has_cache(chat_id, mode, trigger, filename):
    basepath = f"data/keyword_cache/{chat_id}/{mode}:{encode(trigger)}"
    filepath = f"{basepath}/{filename}"
    if not path.exists(basepath):
        makedirs(basepath)
        return (False, filepath)
    if not path.exists(filepath):
        return (False, filepath)
    return (True, filepath)


def cache_opened(chat_id, mode, trigger):
    rule_data = get_redis(f"keyword.{chat_id}.single"
                          f".{mode}.{encode(trigger)}").get("cache", None)
    chat_data = get_redis(f"keyword.{chat_id}.settings").get("cache", None)
    global_data = get_redis("keyword.settings").get("cache", None)
    if rule_data:
        return True if rule_data == "1" else False
    elif chat_data:
        return True if chat_data == "1" else False
    elif global_data:
        return True if global_data == "1" else False
    return False


async def del_msg(context, t_lim):
    await asyncio.sleep(t_lim)
    try:
        await context.delete()
    except:
        pass


async def send_reply(chat_id, trigger, mode, reply_msg, context):
    try:
        real_chat_id = chat_id
        chat = context.chat
        sender = context.sender
        replace_data = {}
        if chat_id < 0:
            replace_data = {
                "chat_id": chat.id,
                "chat_name": chat.title
            }
            if sender:
                replace_data["user_id"] = sender.id
                replace_data["first_name"] = sender.first_name
                replace_data["last_name"] = sender.last_name if sender.last_name else ""
        else:
            replace_data["user_id"] = chat_id
            if sender:
                replace_data["first_name"] = sender.first_name
                replace_data["last_name"] = sender.last_name if sender.last_name else ""
            if chat:
                replace_data["chat_id"] = chat.id
                last_name = chat.last_name
                if not last_name:
                    last_name = ""
                replace_data["chat_name"] = f"{chat.first_name} {last_name}"
        update_last_time = False
        could_send_msg = valid_time(chat_id)
        for re_type, re_msg in reply_msg:
            try:
                for k, v in replace_data.items():
                    re_type = re_type.replace(f"${k}", str(v))
                    re_msg = re_msg.replace(f"${k}", str(v))
                type_parse = re_type.split(",")
                type_parse = [(p[4:] if p[0:3] == "adv" else "") for p in type_parse]
                for s in type_parse:
                    if len(s) >= 5 and "ext_" == s[0:4] and is_num(s[4:]):
                        chat_id = int(s[4:])
                        type_parse.remove(s)
                        break
                if ("file" in type_parse or "photo" in type_parse) and len(re_msg.split()) >= 2:
                    if could_send_msg:
                        update_last_time = True
                        re_data = re_msg.split(" ")
                        cache_exists, cache_path = has_cache(chat_id, mode, trigger, re_data[0])
                        is_opened = cache_opened(chat_id, mode, trigger)
                        filename = "/tmp/" + re_data[0]
                        if is_opened:
                            filename = cache_path
                            if not cache_exists:
                                if re_data[1][0:7] == "file://":
                                    re_data[1] = re_data[1][7:]
                                    copyfile(" ".join(re_data[1:]), filename)
                                else:
                                    fileget = requests.get(" ".join(re_data[1:]))
                                    with open(filename, "wb") as f:
                                        f.write(fileget.content)
                        else:
                            if re_data[1][0:7] == "file://":
                                re_data[1] = re_data[1][7:]
                                copyfile(" ".join(re_data[1:]), filename)
                            else:
                                fileget = requests.get(" ".join(re_data[1:]))
                                with open(filename, "wb") as f:
                                    f.write(fileget.content)
                        reply_to = None
                        if "reply" in type_parse:
                            reply_to = context.id
                        await bot.send_file(chat_id, filename,
                                            reply_to=reply_to, force_document=("file" in type_parse))
                        if not is_opened:
                            remove(filename)
                elif ("tgfile" in type_parse or "tgphoto" in type_parse) and len(re_msg.split()) >= 2:
                    if could_send_msg:
                        update_last_time = True
                        if not path.exists("/tmp"):
                            mkdir("/tmp")
                        re_data = re_msg.split()
                        file_name = "/tmp/" + re_data[0]
                        _data = BytesIO()
                        re_data[1] = re_data[1].split("/")[-2:]
                        try:
                            msg_chat_id = int(re_data[1][0])
                        except:
                            async with bot.conversation(re_data[1][0]) as conversation:
                                msg_chat_id = conversation.chat_id
                        msg_id_inchat = int(re_data[1][1])
                        await bot.send_message(chat_id, f"{msg_chat_id, msg_id_inchat}")
                        media_msg = (await bot.get_messages(msg_chat_id, msg_id_inchat))[0]
                        _data = BytesIO()
                        if media_msg and media_msg.media:
                            if "tgfile" in type_parse:
                                await bot.download_file(media_msg.media.document, _data)
                            else:
                                await bot.download_file(media_msg.photo, _data)
                            with open(file_name, "wb") as f:
                                f.write(_data.getvalue())
                            reply_to = None
                            if "reply" in type_parse:
                                reply_to = context.id
                            await bot.send_file(chat_id, file_name, reply_to=reply_to,
                                                force_document=("tgfile" in type_parse))
                            remove(file_name)
                elif "plain" in type_parse:
                    if could_send_msg:
                        update_last_time = True
                        await bot.send_message(chat_id, re_msg,
                                               link_preview=("nopreview" not in type_parse))
                elif "reply" in type_parse and chat_id == real_chat_id:
                    if could_send_msg:
                        update_last_time = True
                        await bot.send_message(chat_id, re_msg, reply_to=context.id,
                                               link_preview=("nopreview" not in type_parse))
                elif "op" in type_parse:
                    if re_msg == "delete":
                        await context.delete()
                    elif re_msg.split()[0] == "sleep" and len(re_msg.split()) == 2:
                        sleep_time = re_msg.split()[1]
                        await asyncio.sleep(float(sleep_time))
            except:
                pass
            chat_id = real_chat_id
        if update_last_time:
            global group_last_time
            group_last_time[int(chat_id)] = time.time()
    except:
        pass


async def main(context):
    if not redis_status():
        return
    try:
        chat_id = context.chat_id
        sender_id = context.sender_id
        if f"{chat_id}:{context.id}" not in read_context:
            plain_dict = get_redis(f"keyword.{chat_id}.plain")
            regex_dict = get_redis(f"keyword.{chat_id}.regex")
            g_settings = get_redis("keyword.settings")
            n_settings = get_redis(f"keyword.{chat_id}.settings")
            g_mode = g_settings.get("mode", None)
            n_mode = n_settings.get("mode", None)
            mode = "0"
            g_list = g_settings.get("list", None)
            n_list = n_settings.get("list", None)
            user_list = []
            if g_mode and n_mode:
                mode = n_mode
            elif g_mode or n_mode:
                mode = g_mode if g_mode else n_mode
            if g_list and n_list:
                user_list = n_list
            elif g_list or n_list:
                user_list = g_list if g_list else n_list
            send_text = context.text
            if not send_text:
                send_text = ""
            for k, v in plain_dict.items():
                if k in send_text:
                    tmp = get_redis(f"keyword.{chat_id}.single.plain.{encode(k)}")
                    could_reply = validate(str(sender_id), int(mode), user_list)
                    if tmp:
                        could_reply = validate(str(sender_id), int(tmp.get("mode", "0")), tmp.get("list", []))
                    if could_reply:
                        read_context[f"{chat_id}:{context.id}"] = None
                        await send_reply(chat_id, k, "plain", parse_multi(v), context)
            for k, v in regex_dict.items():
                pattern = re.compile(k)
                if pattern.search(send_text):
                    tmp = get_redis(f"keyword.{chat_id}.single.regex.{encode(k)}")
                    could_reply = validate(str(sender_id), int(mode), user_list)
                    if tmp:
                        could_reply = validate(str(sender_id), int(tmp.get("mode", "0")), tmp.get("list", []))
                    if could_reply:
                        read_context[f"{chat_id}:{context.id}"] = None
                        catch_pattern = r"\$\{regex_(?P<str>((?!\}).)+)\}"
                        count = 0
                        while re.search(catch_pattern, v) and count < 20:
                            search_data = re.search(k, send_text)
                            group_name = re.search(catch_pattern, v).group("str")
                            capture_data = get_capture(search_data, group_name)
                            if not capture_data:
                                capture_data = ""
                            if re.search(catch_pattern, capture_data):
                                capture_data = ""
                            v = v.replace("${regex_%s}" % group_name, capture_data)
                            count += 1
                        await send_reply(chat_id, k, "regex", parse_multi(v), context)
        else:
            del read_context[f"{chat_id}:{context.id}"]
    except:
        pass
    return ""
