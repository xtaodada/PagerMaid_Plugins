import re, time, asyncio, requests
from os import path, mkdir, remove
from uuid import uuid4
from base64 import b64encode, b64decode
from pagermaid import bot, redis, log, redis_status
from pagermaid.listener import listener

msg_rate = 1
last_time = time.time()

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
        if len(p) == 2: data = p
        else: data[1] = p[0]
        n_rule.append(data)
    return n_rule

def get_capture(search_data, group_name):
    try:
        capture_data = search_data.group(group_name)
        return capture_data
    except:
        return None

def get_rule(chat_id, rule_type, rule_index):
    rule_index = int(rule_index)
    rule_data = get_redis(f"keyword.{chat_id}.{rule_type}")
    index = 0
    for k, v in rule_data.items():
        if index == rule_index:
            return encode(k)
        index += 1
    return None

async def del_msg(context, t_lim):
    await asyncio.sleep(t_lim)
    await context.delete()

async def send_reply(chat_id, reply_msg, context):
    chat = context.chat
    sender = context.sender
    replace_data = {
        "user_id": sender.id,
        "first_name": sender.first_name,
        "last_name": sender.last_name if sender.last_name else "",
        "chat_id": chat.id,
        "chat_name": chat.title
    }
    for re_type, re_msg in reply_msg:
        for k, v in replace_data.items():
            re_msg = re_msg.replace(f"${k}", str(v))
        if re_type == "plain":
            await bot.send_message(chat_id, re_msg)
        elif re_type == "reply":
            await bot.send_message(chat_id, re_msg, reply_to = context.id)
        elif re_type == "file" and len(re_msg.split()) >= 2:
            if not path.exists("/tmp"): mkdir("/tmp")
            re_data = re_msg.split()
            file_name = "/tmp/" + re_data[0]
            file_get = requests.get(" ".join(re_data[1: ]))
            with open(file_name, "wb") as f:
                f.write(file_get.content)
            await bot.send_file(chat_id, file_name)
            remove(file_name)
        elif re_type == "op":
            if re_msg == "delete":
                await context.delete()
            elif re_msg.split()[0] == "sleep" and len(re_msg.split()) == 2:
                sleep_time = re_msg.split()[1]
                if is_num(sleep_time):
                    await asyncio.sleep(int(sleep_time))

@listener(is_plugin=True, outgoing=True, command="keyword",
          description="关键词自动回复",
          parameters="``new <plain|regex> '<规则>' '<回复信息>'` 或者 `del <plain|regex> '<规则>'` 或者 `list` 或者 `clear <plain|regex>")
async def reply(context):
    if not redis_status():
        await context.edit("出错了呜呜呜 ~ Redis 离线，无法运行")
        await del_msg(context, 5)
        return
    chat_id = context.chat_id
    if chat_id > 0:
        await context.edit("请在群组中使用")
        await del_msg(context, 5)
        return
    plain_dict = get_redis(f"keyword.{chat_id}.plain")
    regex_dict = get_redis(f"keyword.{chat_id}.regex")
    params = context.parameter
    params = " ".join(params)
    placeholder = random_str()
    params = params.replace(r"\'", placeholder)
    tmp_parse = params.split("'")
    parse = []
    for i in range(len(tmp_parse)):
        if len(tmp_parse[i].split()) != 0:
            parse.append(tmp_parse[i])
    if len(parse) == 0 or (len(parse[0].split()) == 1 and parse[0].split()[0] in ("new", "del", "clear")) or len(parse[0].split()) > 2:
        await context.edit("[Code: -1] 格式错误，格式为 `-keyword` 加上 `new <plain|regex> '<规则>' '<回复信息>'` 或者 `del <plain|regex> '<规则>'` 或者 `list` 或者 `clear <plain|regex>`")
        await del_msg(context, 10)
        return
    else: parse[0] = parse[0].split()
    if parse[0][0] == "new" and len(parse) == 3:
        if parse[0][1] == "plain":
            plain_dict[parse[1]] = parse[2]
            redis.set(f"keyword.{chat_id}.plain", save_rules(plain_dict, placeholder))
        elif parse[0][1] == "regex":
            regex_dict[parse[1]] = parse[2]
            redis.set(f"keyword.{chat_id}.regex", save_rules(regex_dict, placeholder))
        else:
            await context.edit("格式错误，格式为 `-keyword` 加上 `new <plain|regex> '<规则>' '<回复信息>'` 或者 `del <plain|regex> '<规则>'` 或者 `list` 或者 `clear <plain|regex>`")
            await del_msg(context, 10)
            return
        await context.edit("设置成功")
        await del_msg(context, 5)
    elif parse[0][0] == "del" and len(parse) == 2:
        if parse[0][1] == "plain":
            if parse[1] in plain_dict:
                redis.delete(f"keyword.{chat_id}.single.plain.{encode(parse[1])}")
                plain_dict.pop(parse[1])
                redis.set(f"keyword.{chat_id}.plain", save_rules(plain_dict, placeholder))
            else:
                await context.edit("规则不存在")
                await del_msg(context, 5)
                return
        elif parse[0][1] == "regex":
            if parse[1] in regex_dict:
                redis.delete(f"keyword.{chat_id}.single.regex.{encode(parse[1])}")
                regex_dict.pop(parse[1])
                redis.set(f"keyword.{chat_id}.regex", save_rules(regex_dict, placeholder))
            else:
                await context.edit("规则不存在")
                await del_msg(context, 5)
                return
        else:
            await context.edit("格式错误，格式为 -keyword 加上 new <plain|regex> '<规则>' '<回复信息>' 或者 del <plain|regex> '<规则>' 或者 list 或者 clear <plain|regex>")
            await del_msg(context, 10)
            return
        await context.edit("删除成功")
        await del_msg(context, 5)
    elif parse[0][0] == "list" and len(parse) == 1:
        plain_msg = "Plain: \n"
        index = 0
        for k, v in plain_dict.items():
            plain_msg += f"`{index}`: `{k}` -> `{v}`\n"
            index += 1
        regex_msg = "Regex: \n"
        index = 0
        for k, v in regex_dict.items():
            regex_msg += f"`{index}`: `{k}` -> `{v}`\n"
            index += 1
        await context.edit(plain_msg + "\n" + regex_msg)
    elif parse[0][0] == "clear" and len(parse) == 1:
        if parse[0][1] == "plain":
            for k in plain_dict.keys():
                redis.delete(f"keyword.{chat_id}.single.plain.{encode(k)}")
            redis.set(f"keyword.{chat_id}.plain", "")
        elif parse[0][1] == "regex":
            for k in regex_dict.keys():
                redis.delete(f"keyword.{chat_id}.single.regex.{encode(k)}")
            redis.set(f"keyword.{chat_id}.regex", "")
        else:
            await context.edit("参数错误")
            await del_msg(context, 5)
            return
        await context.edit("清除成功")
        await del_msg(context, 5)
    else:
        await context.edit("[Code -2] 格式错误，格式为 `-keyword` 加上 `new <plain|regex> '<规则>' '<回复信息>'` 或者 `del <plain|regex> '<规则>'` 或者 `list` 或者 `clear <plain|regex>`")
        await del_msg(context, 10)
        return

@listener(outgoing=True, command="replyset",
          description="自动回复设置",
          parameters="help")
async def reply_set(context):
    if not redis_status():
        await context.edit("出错了呜呜呜 ~ Redis 离线，无法运行")
        await del_msg(context, 5)
        return
    chat_id = context.chat_id
    if chat_id > 0:
        await context.edit("请在群组中使用")
        await del_msg(context, 5)
        return
    params = context.parameter
    redis_data = f"keyword.{chat_id}.settings"
    if len(params) >= 1 and params[0] == "global":
        redis_data = "keyword.settings"
        del params[0]
    elif len(params) >= 2 and params[0] in ("plain", "regex") and is_num(params[1]):
        rule_data = get_rule(chat_id, params[0], params[1])
        if rule_data:
            redis_data = f"keyword.{chat_id}.single.{params[0]}.{rule_data}"
            del params[0:2]
    settings_dict = get_redis(redis_data)
    cmd_list = ["help", "mode", "list", "show", "clear"]
    cmd_dict = {"help": (1, ), "mode": (2, ), "list": (2, 3), "show": (1, ), "clear": (1, )}
    if len(params) < 1:
        await context.edit("参数错误")
        await del_msg(context, 5)
        return
    if params[0] in cmd_list and len(params) in cmd_dict[params[0]]:
        if params[0] == "help":
            await context.edit('''
`-replyset show` 或
`-replyset clear` 或
`-replyset mode <0/1/clear>` ( 0 表示黑名单，1 表示白名单 ) 或
`-replyset list <add/del/show/clear> [user_id]`。
在 `-replyset` 后面加上 `global` 即为全局设置''')
            await del_msg(context, 15)
            return
        elif params[0] == "show":
            defaults = {"mode": "未设置", "list": "未设置"}
            msg = "Settings: \n"
            for k, v in defaults.items():
                msg += f"`{k}` -> `{settings_dict[k] if k in settings_dict else v}`\n"
            await context.edit(msg)
            return
        elif params[0] == "mode":
            if params[1] in ("0", "1"):
                settings_dict["mode"] = params[1]
                redis.set(redis_data, save_rules(settings_dict, None))
                if params[1] == "0": await context.edit("模式已更改为黑名单")
                elif params[1] == "1": await context.edit("模式已更改为白名单")
                await del_msg(context, 5)
                return
            elif params[1] == "clear":
                if "mode" in settings_dict: del settings_dict["mode"]
                redis.set(redis_data, save_rules(settings_dict, None))
                await context.edit("清除成功")
                await del_msg(context, 5)
                return
            else:
                await context.edit("参数错误")
                await del_msg(context, 5)
                return
        elif params[0] == "list":
            if params[1] == "show" and len(params) == 2:
                user_list = settings_dict.get("list", None)
                if user_list:
                    msg = "List: \n"
                    for p in user_list.split(","):
                        msg += f"`{p}`\n"
                    await context.edit(msg)
                    return
                else:
                    await context.edit("列表为空")
                    await del_msg(context, 5)
                    return
            elif params[1] == "add" and len(params) == 3:
                if is_num(params[2]):
                    tmp = settings_dict.get("list", None)
                    if not tmp: settings_dict["list"] = params[2]
                    else: settings_dict["list"] += f",{params[2]}"
                    redis.set(redis_data, save_rules(settings_dict, None))
                    await context.edit("添加成功")
                    await del_msg(context, 5)
                    return
                else:
                    await context.edit("user_id 需为整数")
                    await del_msg(context, 5)
                    return
            elif params[1] == "del" and len(params) == 3:
                if is_num(params[2]):
                    tmp = settings_dict.get("list", None)
                    if tmp:
                        user_list = settings_dict["list"].split(",")
                        if params[2] in user_list:
                            user_list.remove(params[2])
                            settings_dict["list"] = ",".join(user_list)
                            redis.set(redis_data, save_rules(settings_dict, None))
                            await context.edit("删除成功")
                            await del_msg(context, 5)
                            return
                        else:
                            await context.edit("user_id 不在列表")
                            await del_msg(context, 5)
                            return
                    else:
                        await context.edit("列表为空")
                        await del_msg(context, 5)
                        return
                else:
                    await context.edit("user_id 需为整数")
                    await del_msg(context, 5)
                    return
            elif params[1] == "clear" and len(params) == 2:
                if "list" in settings_dict: del settings_dict["list"]
                redis.set(redis_data, save_rules(settings_dict, None))
                await context.edit("清除成功")
                await del_msg(context, 5)
                return
            else:
                await context.edit("参数错误")
                await del_msg(context, 5)
                return
        elif params[0] == "clear":
            redis.delete(redis_data)
            await context.edit("清除成功")
            await del_msg(context, 5)
            return
    else:
        await context.edit("参数错误")
        await del_msg(context, 5)
        return
    

@listener(incoming=True, ignore_edited=True)
async def auto_reply(context):
    if not redis_status():
        return
    global msg_rate, last_time
    chat_id = context.chat_id
    sender_id = context.sender_id
    if chat_id < 0:
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
        if g_mode and n_mode: mode = n_mode
        elif g_mode or n_mode: mode = g_mode if g_mode else n_mode
        if g_list and n_list: user_list = n_list
        elif g_list or n_list: user_list = g_list if g_list else n_list
        send_text = context.text
        for k, v in plain_dict.items():
            if k in send_text and time.time() - last_time > msg_rate:
                tmp = get_redis(f"keyword.{chat_id}.single.plain.{encode(k)}")
                could_reply = validate(str(sender_id), int(mode), user_list)
                if tmp:
                    could_reply = validate(str(sender_id), int(tmp.get("mode", "0")), tmp.get("list", []))
                if could_reply:
                    last_time = time.time()
                    await send_reply(chat_id, parse_multi(v), context)
        for k, v in regex_dict.items():
            pattern = re.compile(k)
            if pattern.search(send_text) and time.time() - last_time > msg_rate:
                tmp = get_redis(f"keyword.{chat_id}.single.regex.{encode(k)}")
                could_reply = validate(str(sender_id), int(mode), user_list)
                if tmp:
                    could_reply = validate(str(sender_id), int(tmp.get("mode", "0")), tmp.get("list", []))
                if could_reply:
                    last_time = time.time()
                    catch_pattern = r"\$\{regex_(?P<str>((?!\}).)+)\}"
                    count = 0
                    while re.search(catch_pattern, v) and count < 20:
                        search_data = re.search(k, send_text)
                        group_name = re.search(catch_pattern, v).group("str")
                        capture_data = get_capture(search_data, group_name)
                        if not capture_data: capture_data = ""
                        if re.search(catch_pattern, capture_data): capture_data = ""
                        v = v.replace("${regex_%s}" % group_name, capture_data)
                        count += 1
                    await send_reply(chat_id, parse_multi(v), context)
