""" Pagermaid plugin base. """
import json, requests, re
from urllib.parse import urlparse
from pagermaid import bot, log
from pagermaid.listener import listener, config
from pagermaid.utils import clear_emojis, obtain_message, attach_log
from telethon.errors import ChatAdminRequiredError
from os import remove


@listener(is_plugin=True, outgoing=True, command="guess",
          description="能不能好好说话？ - 拼音首字母缩写释义工具（需要回复一句话）")
async def guess(context):
    reply = await context.get_reply_message()
    await context.edit("获取中 . . .")
    if not reply:
        context.edit("宁需要回复一句话")
        return True
    text = {'text': str(reply.message.replace("/guess ", "").replace(" ", ""))}
    guess_json = json.loads(
        requests.post("https://lab.magiconch.com/api/nbnhhsh/guess", data=text, verify=False).content.decode("utf-8"))
    guess_res = []
    if not len(guess_json) == 0:
        for num in range(0, len(guess_json)):
            guess_res1 = json.loads(json.dumps(guess_json[num]))
            guess_res1_name = guess_res1['name']
            try:
                guess_res1_ans = ", ".join(guess_res1['trans'])
            except:
                try:
                    guess_res1_ans = ", ".join(guess_res1['inputting'])
                except:
                    guess_res1_ans = "尚未录入"
            guess_res.extend(["词组：" + guess_res1_name + "\n释义：" + guess_res1_ans])
        await context.edit("\n\n".join(guess_res))
    else:
        await context.edit("没有匹配到拼音首字母缩写")


@listener(is_plugin=True, outgoing=True, command="wiki",
          description="查询维基百科词条",
          parameters="<词组>")
async def wiki(context):
    lang = config['application_language'].replace('zh-cn', 'zh')
    await context.edit("获取中 . . .")
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    try:
        wiki_json = json.loads(requests.get("https://zh.wikipedia.org/w/api.php?action=query&list=search&format=json"
                                            "&formatversion=2&srsearch=" + message).content.decode(
            "utf-8"))
    except:
        await context.edit("出错了呜呜呜 ~ 无法访问到维基百科。")
        return
    if not len(wiki_json['query']['search']) == 0:
        wiki_title = wiki_json['query']['search'][0]['title']
        wiki_content = wiki_json['query']['search'][0]['snippet'].replace('<span class=\"searchmatch\">', '**').replace(
            '</span>', '**')
        wiki_time = wiki_json['query']['search'][0]['timestamp'].replace('T', ' ').replace('Z', ' ')
        try:
            await context.edit("正在生成翻译中 . . .")
            USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
            headers = {"user-agent": USER_AGENT}
            wiki_content = json.loads(requests.get("https://xtaolink.cn/git/m/t.php?lang=" + lang + '&text=' +
                                                   clear_emojis(wiki_content), headers=headers)
                                      .content.decode("utf-8"))['data']['target_text']
            message = '词条： [' + wiki_title + '](https://zh.wikipedia.org/zh-cn/' + wiki_title + ')\n\n' + \
                      wiki_content + '...\n\n此词条最后修订于 ' + wiki_time
        except ValueError:
            await context.edit("出错了呜呜呜 ~ 找不到目标语言，请更正配置文件中的错误。")
            return
        await context.edit(message)
    else:
        await context.edit("没有匹配到相关词条")


@listener(is_plugin=True, outgoing=True, command="ip",
          description="IPINFO （或者回复一句话）",
          parameters="<ip/域名>")
async def ipinfo(context):
    reply = await context.get_reply_message()
    await context.edit('正在查询中...')
    try:
        if reply:
            for num in range(0, len(reply.entities)):
                url = reply.message[reply.entities[num].offset:reply.entities[num].offset + reply.entities[num].length]
                url = urlparse(url)
                if url.hostname:
                    url = url.hostname
                else:
                    url = url.path
                ipinfo_json = json.loads(requests.get(
                    "http://ip-api.com/json/" + url + "?fields=status,message,country,regionName,city,lat,lon,isp,"
                                                      "org,as,mobile,proxy,hosting,query").content.decode(
                    "utf-8"))
                if ipinfo_json['status'] == 'fail':
                    pass
                elif ipinfo_json['status'] == 'success':
                    ipinfo_list = []
                    ipinfo_list.extend(["查询目标： `" + url + "`"])
                    if ipinfo_json['query'] == url:
                        pass
                    else:
                        ipinfo_list.extend(["解析地址： `" + ipinfo_json['query'] + "`"])
                    ipinfo_list.extend(["地区： `" + ipinfo_json['country'] + ' - ' + ipinfo_json['regionName'] + ' - ' +
                                        ipinfo_json['city'] + "`"])
                    ipinfo_list.extend(["经纬度： `" + str(ipinfo_json['lat']) + ',' + str(ipinfo_json['lon']) + "`"])
                    ipinfo_list.extend(["ISP： `" + ipinfo_json['isp'] + "`"])
                    if not ipinfo_json['org'] == '':
                        ipinfo_list.extend(["组织： `" + ipinfo_json['org'] + "`"])
                    try:
                        ipinfo_list.extend(
                            ['[' + ipinfo_json['as'] + '](https://bgp.he.net/' + ipinfo_json['as'].split()[0] + ')'])
                    except:
                        pass
                    if ipinfo_json['mobile']:
                        ipinfo_list.extend(['此 IP 可能为**蜂窝移动数据 IP**'])
                    if ipinfo_json['proxy']:
                        ipinfo_list.extend(['此 IP 可能为**代理 IP**'])
                    if ipinfo_json['hosting']:
                        ipinfo_list.extend(['此 IP 可能为**数据中心 IP**'])
                    await context.edit('\n'.join(ipinfo_list))
                    return True
        else:
            url = urlparse(context.arguments)
            if url.hostname:
                url = url.hostname
            else:
                url = url.path
            ipinfo_json = json.loads(requests.get(
                "http://ip-api.com/json/" + url + "?fields=status,message,country,regionName,city,lat,lon,isp,org,as,"
                                                  "mobile,proxy,hosting,query").content.decode(
                "utf-8"))
            if ipinfo_json['status'] == 'fail':
                pass
            elif ipinfo_json['status'] == 'success':
                ipinfo_list = []
                if url == '':
                    ipinfo_list.extend(["查询目标： `本机地址`"])
                else:
                    ipinfo_list.extend(["查询目标： `" + url + "`"])
                if ipinfo_json['query'] == url:
                    pass
                else:
                    ipinfo_list.extend(["解析地址： `" + ipinfo_json['query'] + "`"])
                ipinfo_list.extend(["地区： `" + ipinfo_json['country'] + ' - ' + ipinfo_json['regionName'] + ' - ' +
                                    ipinfo_json['city'] + "`"])
                ipinfo_list.extend(["经纬度： `" + str(ipinfo_json['lat']) + ',' + str(ipinfo_json['lon']) + "`"])
                ipinfo_list.extend(["ISP： `" + ipinfo_json['isp'] + "`"])
                if not ipinfo_json['org'] == '':
                    ipinfo_list.extend(["组织： `" + ipinfo_json['org'] + "`"])
                try:
                    ipinfo_list.extend(
                        ['[' + ipinfo_json['as'] + '](https://bgp.he.net/' + ipinfo_json['as'].split()[0] + ')'])
                except:
                    pass
                if ipinfo_json['mobile']:
                    ipinfo_list.extend(['此 IP 可能为**蜂窝移动数据 IP**'])
                if ipinfo_json['proxy']:
                    ipinfo_list.extend(['此 IP 可能为**代理 IP**'])
                if ipinfo_json['hosting']:
                    ipinfo_list.extend(['此 IP 可能为**数据中心 IP**'])
                await context.edit('\n'.join(ipinfo_list))
                return True
        await context.edit('没有找到要查询的 ip/域名 ...')
    except:
        await context.edit('没有找到要查询的 ip/域名 ...')


@listener(is_plugin=True, outgoing=True, command="ipping",
          description="Ping （或者回复一句话）",
          parameters="<ip/域名>")
async def ipping(context):
    reply = await context.get_reply_message()
    await context.edit('正在查询中...')
    try:
        if reply:
            for num in range(0, len(reply.entities)):
                url = reply.message[reply.entities[num].offset:reply.entities[num].offset + reply.entities[num].length]
                url = urlparse(url)
                if url.hostname:
                    url = url.hostname
                else:
                    url = url.path
                pinginfo = requests.get(
                    "https://steakovercooked.com/api/ping/?host=" + url).content.decode("utf-8")
                if pinginfo == 'null':
                    pass
                elif not pinginfo == 'null':
                    pinginfo = pinginfo.replace('"', '').replace("\/", '/').replace('\\n', '\n', 7).replace('\\n', '')
                    await context.edit(pinginfo)
                    return True
        else:
            url = urlparse(context.arguments)
            if url.hostname:
                url = url.hostname
            else:
                url = url.path
            if url == '':
                await context.edit('没有找到要查询的 ip/域名 ...')
                return True
            pinginfo = requests.get(
                "https://steakovercooked.com/api/ping/?host=" + url).content.decode("utf-8")
            if pinginfo == 'null':
                pass
            elif not pinginfo == 'null':
                pinginfo = pinginfo.replace('"', '').replace("\/", '/').replace('\\n', '\n', 7).replace('\\n', '')
                await context.edit(pinginfo)
                return True
        await context.edit('没有找到要查询的 ip/域名 ...')
    except:
        await context.edit('没有找到要查询的 ip/域名 ...')


@listener(is_plugin=True, outgoing=True, command="t",
          description="通过腾讯AI开放平台将目标消息翻译成指定的语言。"
                      "目前支持的语言有 zh, en, jp, kr, fr, es, it, de, tr, ru, pt, vi, id, ms, th。",
          parameters="<回复消息/文本> <指定语言>")
async def tx_t(context):
    """ PagerMaid universal translator. """
    reply = await context.get_reply_message()
    message = context.arguments
    lang = 'zh'
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent": USER_AGENT}
    api_lang = ['zh', 'en', 'jp', 'kr', 'fr', 'es', 'it', 'de', 'tr', 'ru', 'pt', 'vi', 'id', 'ms', 'th']
    if reply:
        message = reply.text
        if context.parameter:
            if re.search(r'[a-z]{2}', context.parameter[0]):
                if context.parameter[0] in api_lang:
                    lang = context.parameter[0]
                else:
                    await context.edit("指定语言未支持，使用默认语言")
        else:
            await context.edit("未指定语言，使用默认语言")
    elif context.parameter:
        message = context.parameter[0]
        try:
            if re.search(r'[a-z]{2}', context.parameter[1]):
                if context.parameter[1] in api_lang:
                    lang = context.parameter[1]
                else:
                    await context.edit("指定语言未支持，使用默认语言")
        except IndexError:
            await context.edit("未指定语言，使用默认语言")
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    try:
        await context.edit("正在生成翻译中 . . .")
        tx_json = json.loads(requests.get(
            "https://xtaolink.cn/git/m/t.php?lang=" + lang + '&text=' + clear_emojis(message),
            headers=headers).content.decode(
            "utf-8"))
        if not tx_json['msg'] == 'ok':
            context.edit("出错了呜呜呜 ~ 翻译出错")
            return True
        else:
            result = '文本翻译：\n' + tx_json['data']['target_text']
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 找不到目标语言，请更正配置文件中的错误。")
        return

    if len(result) > 4096:
        await context.edit("输出超出 TG 限制，正在尝试上传文件。")
        await attach_log(result, context.chat_id, "translation.txt", context.id)
        return
    await context.edit(result)


@listener(is_plugin=True, outgoing=True, command="getdel",
          description="获取当前群组/频道的死号数。")
async def getdel(context):
    """ PagerMaid getdel. """
    cid = str(context.chat_id)
    pri = cid.startswith('-100')
    if pri:
        member_count = 0
        try:
            await context.edit('遍历成员中。。。')
            chat = await context.get_chat()
            async for member in bot.iter_participants(chat):
                if member.deleted:
                    member_count += 1
            await context.edit(f'此频道/群组的死号数：`{member_count}`')
        except ChatAdminRequiredError:
            await context.edit('未加入此频道。')
    else:
        await context.edit("请在在群组/频道发送。")
