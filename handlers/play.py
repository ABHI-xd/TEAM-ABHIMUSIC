import os
from asyncio.queues import QueueEmpty
from os import path
from typing import Callable

import aiofiles
import aiohttp
import converter
import ffmpeg
import requests
from cache.admins import admins as a
from callsmusic import callsmusic
from callsmusic.callsmusic import client as USER
from callsmusic.queues import queues
from config import (
    ASSISTANT_NAME,
    BOT_NAME,
    BOT_USERNAME,
    DURATION_LIMIT,
    GROUP_SUPPORT,
    THUMB_IMG,
    UPDATES_CHANNEL,
    que,
)
from downloaders import youtube
from helpers.admins import get_administrators
from helpers.channelmusic import get_chat_id
from helpers.chattitle import CHAT_TITLE
from helpers.decorators import authorized_users_only
from helpers.filters import command, other_filters
from helpers.gets import get_file_name
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtube_search import YoutubeSearch

aiohttpsession = aiohttp.ClientSession()
chat_id = None
useer = "NaN"
DISABLED_GROUPS = []


def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admemes = a.get(cb.message.chat.id)
        if cb.from_user.id in admemes:
            return await func(client, cb)
        else:
            await cb.answer("💡 only admin can tap this button !", show_alert=True)
            return

    return decorator


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def generate_cover(title, thumbnail, ctitle):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()
    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/Roboto-Medium.ttf", 55)
    font2 = ImageFont.truetype("etc/finalfont.ttf", 80)
    draw.text((20, 528), f"Playing on {ctitle[:10]}", (0, 0, 0), font=font)
    draw.text((20, 610), f"{title[:20]}...", (0, 0, 0), font=font2)
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")
    
@Client.on_message(
    command(["playlist", f"playlist@{BOT_USERNAME}"]) & filters.group & ~filters.edited
)
async def playlist(client, message):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💫𝚂𝚄𝙿𝙿𝙾𝚁T✨", url=f"https://t.me/SNEHABHI_SERVER"),
                InlineKeyboardButton(
                    "💫 𝙲𝙷𝙰𝙽𝙽𝙴𝙻✨", url=f"https://t.me/SNEHABHI_UPDATES"
                ),
            ]
        ]
    )

    global que
    if message.chat.id in DISABLED_GROUPS:
        return
    queue = que.get(message.chat.id)
    if not queue:
        await message.reply_text("❌ **KOI SONG PLAY HI NI HAI**")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "💡 **now playing** on {}".format(message.chat.title)
    msg += "\n\n• " + now_playing
    msg += "\n• Req By " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "🔖 **Queued Song:**\n"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n• {name}"
            msg += f"\n• Req by {usr}\n"
    await message.reply_text(msg, reply_markup=keyboard)


# ============================= Settings =========================================
def updated_stats(chat, queue, vol=100):
    if chat.id in callsmusic.pytgcalls.active_calls:
        stats = "⚙ settings for **{}**".format(chat.title)
        if len(que) > 0:
            stats += "\n\n"
            stats += "• volume: `{}%`\n".format(vol)
            stats += "• song played: `{}`\n".format(len(que))
            stats += "• now playing: **{}**\n".format(queue[0][0])
            stats += "• request by: {}".format(queue[0][1].mention(style="md"))
    else:
        stats = None
    return stats


def r_ply(type_):
    if type_ == "play":
        pass
    else:
        pass
    mar = InlineKeyboardMarkup(
        [
          [

                    InlineKeyboardButton(text="💫 𝙲𝙷𝙰𝙽𝙽𝙴𝙻✨", url=f"https://t.me/SNEHABHI_UPDATES"),

                    InlineKeyboardButton(text="💫𝚂𝚄𝙿𝙿𝙾𝚁T✨", url=f"https://t.me/SNEHABHI_SERVER")

            ],[

                    InlineKeyboardButton(

                           text="💫 JOIN 𝙼𝙰𝚂𝚃𝙸 𝙶𝚁𝙾𝚄𝙿 👈", url=f"https://t.me/LIVE_LIFE_LIKE")

            ],[       

                    InlineKeyboardButton(

                           text="💫𝙾𝚆𝙽𝙴𝚁 𝙺𝙸𝙽𝙶✨", url=f"https://t.me/SNEHABHI_KING")

            ],[           

                    InlineKeyboardButton(

                           text="💫𝙾𝚆𝙽𝙴𝚁 𝚀𝚄𝙴𝙴𝙽✨", url=f"HTTP://T.ME/SNEHABHI_QUEEN")
              ]
         ]
    )
    return mar

@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
async def ytplay(_, message: Message):
    global que
    if message.chat.id in DISABLED_GROUPS:
        return
    lel = await message.reply("**𝙹𝚄𝚂𝚃 𝚆𝙰𝙸𝚃 𝙰 𝚂𝙴𝙲𝙾𝙽𝙳 💫🥺 𝙵𝙾𝚁 𝙿𝙻𝙰𝚈 𝚂𝙾𝙽𝙶 😋❤️...uploaded by @SNEHABHI_SERVER ✨  ♩✌**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "music assistant"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"💡 **please add the userbot to your channel first**",
                    )
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "💡 **To use me, I need to be an Administrator with the permissions:\n\n» ❌ __Delete messages__\n» ❌ __Ban users__\n» ❌ __Add users__\n» ❌ __Manage voice chat__\n\n**Then type /reload**",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        f"✅ **userbot succesfully entered chat**",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"🔴 **Flood Wait Error** 🔴 \n\n**userbot can't join this group due to many join requests for userbot.**"
                        f"\n\n**or add @{ASSISTANT_NAME} to this group manually then try again.**",
                    )
    try:
        await USER.get_chat(chid)
    except:
        await lel.edit(
            f"💡 **userbot was banned in this group !** \n\n**unban @{ASSISTANT_NAME} and add to this group again manually.**"
        )
        return

    message.from_user.id
    message.from_user.first_name

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    await lel.edit("🔄 **𝙹𝚄𝚂𝚃 𝚆𝙰𝙸𝚃 𝙰 𝚂𝙴𝙲𝙾𝙽𝙳 💫🥺 𝙵𝙾𝚁 𝙿𝙻𝙰𝚈 𝚂𝙾𝙽𝙶 😋.JOIN @SNEHABHI_SERVER..**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"][:60]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        ctitle = message.chat.title
        ctitle = await CHAT_TITLE(ctitle)
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        results[0]["url_suffix"]
        results[0]["views"]

    except Exception as e:
        await lel.edit(
            "✌**/𝐏𝐋𝐀𝐘 𝐊𝐄 𝐁𝐀𝐃 𝐒𝐎𝐍𝐆🌺 𝐊𝐀 𝐍𝐀𝐌 𝐁𝐇𝐈 𝐋𝐈𝐊𝐇𝐍𝐀 🙄𝐇𝐎𝐓𝐀 𝐇𝐀𝐈🥺🧿🤟**"
        )
        print(str(e))
        return
    try:
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ **music with duration more than** `{DURATION_LIMIT}` **minutes, can't play !**"
            )
            return
    except:
        pass
    keyboard = InlineKeyboardMarkup(
        [
            [

                    InlineKeyboardButton(text="💫 𝙲𝙷𝙰𝙽𝙽𝙴𝙻✨", url=f"https://t.me/ABHI_NETWORK1"),

                    InlineKeyboardButton(text="💫𝚂𝚄𝙿𝙿𝙾𝚁T✨", url=f"https://t.me/SNEHABHI_SERVER")

            ],[

                    InlineKeyboardButton(

                           text="💫JOIN 𝙼𝙰𝚂𝚃𝙸 𝙶𝚁𝙾𝚄𝙿 👈", url=f"https://t.me/LIVE_LIFE_LIKE")

            ],[       

                    InlineKeyboardButton(

                           text="💫𝙾𝚆𝙽𝙴𝚁 𝙺𝙸𝙽𝙶✨", url=f"https://t.me/SNEHU_IS_MINE")

            ],[           

                    InlineKeyboardButton(

                           text="💫𝙾𝚆𝙽𝙴𝚁 𝚀𝚄𝙴𝙴𝙽✨", url=f"HTTP://T.ME/ABHI_IS_MINE")

               ]
        ]
    )
    message.from_user.first_name
    await generate_cover(title, thumbnail, ctitle)
    file_path = await converter.convert(youtube.download(url))
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption=f"💡 **JOIN SNEHABHI_SERVER**/n **RUKO ZARA SABAR AAPKA SONG IS SONG KE BAD CHALEGA ITNE NO. PE »** `{position}`\n\n🏷 **JO SONG AAPNE PLAY KIYA HAI USKA NAM😉👉** [{title[:35]}...]({url})\n⏱ **JO ITNE MINUTES KA HAI 👉** `{duration}`\n🎧 **JISNE IS SONG KO PLAY KIYA HAI USKA NAM 👉 ** {message.from_user.mention}",
            reply_markup=keyboard,
        )
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            await lel.edit(
                "😕 VC TO ON KAR LO PAHLE SIR/MADAM 😐 GANE KAHA BAJAU MAI BINA VC ON KE 🙂"
            )
            return
        await message.reply_photo(
            photo="final.png",
            caption=f"🏷 **JO SONG AAPNE PLAY KIYA HAI USKA NAM😉👉** [{title[:60]}]({url})\n⏱ **JO ITNE MINUTES KA HAI👉** `{duration}`\n💡 **status:** `Playing`\n"
            + f"🎧 **JISNE IS SONG KO PLAY KIYA HAI USKA USERNAME 😌👉** {message.from_user.mention}",
            reply_markup=keyboard,
        )
        os.remove("final.png")
        return await lel.delete()
