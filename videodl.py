# -*- coding: utf-8 -*-
import requests
import json
from os import remove, mkdir
from os.path import exists
from re import compile as regex_compile
from pagermaid import bot, log
from pagermaid.listener import listener
from telethon.tl.types import DocumentAttributeVideo
from time import sleep


@listener(outgoing=True, command="vdl",
          description="下载 YouTube/bilibili 视频并上传",
          parameters="<url>")
async def vdl(context):
    url = context.arguments
    reply = await context.get_reply_message()
    reply_id = None
    await context.edit("视频获取中 . . .")
    if reply:
        reply_id = reply.id
    if url is None:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    bilibili_pattern = regex_compile(
        r"^(http(s)?://)?((w){3}.)?bilibili(\.com)?/.+")
    youtube_pattern = regex_compile(
        r"^(http(s)?://)?((w){3}.)?youtu(be|.be)?(\.com)?/.+")
    if youtube_pattern.match(url):
        try:
            from pytube import YouTube
        except ImportError:
            await context.edit('`pytube`支持库未安装，YouTube视频无法下载\n请使用 `-sh pip3 install --user '
                               'git+https://github.com/nficano/pytube 或 -sh pip3 install pytube --upgrade ` 安装，或自行ssh安装\n\n已安装过 `pytube3` 的用户请使用 `-sh pip3 '
                               'uninstall pytube3 -y` 进行卸载')
            return
        url = url.replace('www.youtube.com/watch?v=', 'youtu.be/')
        if not await youtube_dl(url, context, reply_id):
            await context.edit("出错了呜呜呜 ~ 视频下载失败。")
            sleep(3)
        await log(f"已拉取 YouTube 视频，地址： {url}.")
        await context.delete()
    elif bilibili_pattern.match(url):
        if not await bilibili_dl(url, context, reply_id):
            await context.edit("出错了呜呜呜 ~ 视频下载失败。")
            sleep(3)
        await log(f"已拉取 bilibili 视频，地址： {url}.")
        await context.delete()
    else:
        await context.edit("出错了呜呜呜 ~ 无效的网址。")


async def youtube_dl(url, context, reply_id):
    from pytube import YouTube
    video = YouTube(url)
    title = video.title
    filename = title + ".mp4"
    duration = video.length
    await context.edit("视频下载中 . . .")
    YouTube(url).streams.filter(
        file_extension='mp4').get_highest_resolution().download()
    if not exists(filename):
        return False
    await upload(False, filename, context, reply_id, title, duration)
    return True


async def bilibili_dl(url, context, reply_id):
    url = 'https://tenapi.cn/bilivideo/?url=' + url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063', "X-Real-IP": "223.252.199.66"}
    for _ in range(20):  # 最多尝试20次
        status = False
        try:
            req = requests.request('GET', url, headers=headers)
            if req.status_code == 200:
                req = json.loads(req.content)
                if req['title']:
                    title = req['title']
                    url = req['url']
                    status=True
                    break
                else:
                    return False
        except:
            continue
    if status is False:
        await context.client.send_message(context.chat_id, "出错了呜呜呜 ~ 试了好多好多次都无法访问到 API 服务器 。")
        return False
    filename = title + ".flv"
    video = requests.get(url, headers=headers)
    await context.edit("视频下载中 . . .")
    with open(filename, 'wb') as f:
        f.write(video.content)
    await upload(True, filename, context, reply_id, title)
    return True


async def upload(as_file, filename, context, reply_id, caption, duration=0):
    if not exists("plugins/VideoDL/FastTelethon.py"):
        if not exists("plugins/VideoDLExtra"):
            mkdir("plugins/VideoDLExtra")
        faster = requests.request(
            "GET", "https://gist.githubusercontent.com/TNTcraftHIM/ca2e6066ed5892f67947eb2289dd6439/raw"
                   "/86244b02c7824a3ca32ce01b2649f5d9badd2e49/FastTelethon.py")
        for _ in range(6):  # 最多尝试6次
            if faster.status_code == 200:
                with open("plugins/VideoDLExtra/FastTelethon.py", "wb") as f:
                    f.write(faster.content)
                    break
    try:
        from VideoDLExtra.FastTelethon import upload_file
        file = await upload_file(context.client, open(filename, 'rb'), filename)
    except:
        file = filename
        await context.client.send_message(context.chat_id, '(`FastTelethon`支持文件导入失败，上传速度可能受到影响)')
    await context.edit("视频上传中 . . .")
    if as_file is True:
        await context.client.send_file(
            context.chat_id,
            file,
            caption=caption,
            link_preview=False,
            force_document=True,
            reply_to=reply_id
        )
    else:
        await context.client.send_file(
            context.chat_id,
            file,
            caption=caption,
            link_preview=False,
            force_document=False,
            attributes=(DocumentAttributeVideo(duration, 0, 0),),
            reply_to=reply_id
        )
    remove(filename)
