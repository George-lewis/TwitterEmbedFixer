import re
import os

import discord
from crayons import *
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError, ExtractorError

def cprint(string: str, color: 'crayons' = None):
    if color:
        old_print(color(string))
    else:
        old_print(string)

def token():
    with open("discord_token.txt") as file:
        return file.read()

class SilentLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(red(msg))

ydl = YoutubeDL({"outtmpl": "video/video.%(ext)s", "logger": SilentLogger()})

TWITTER_LINK_REGEX = re.compile(r"https://twitter.com/\w{3,}/status/(\d{19})")
class TwitVideo(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {blue(self.user)}")

    def download(link):
        try:
            ydl.download([link])
        except (DownloadError, ExtractorError):
            pass
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if match := TWITTER_LINK_REGEX.search(message.content):
            link = match.group(0)
            status = match.group(1)

            print(red(link))

            prefix = f"status."
            files = [filename for filename in os.listdir("videos") if filename.startswith(prefix)]

            if files:
                filename = files[0]
                path = f"videos/{filename}"
            else:
                TwitVideo.download(link)
                filename = os.listdir('video')[0]
                path = f"video/{filename}"

            try:
                with open(path, "rb") as file:
                    await message.reply(file=discord.File(file, filename=filename))
            finally:
                try:
                    new_name = f"{status}.{filename.split('.')[1]}"
                    os.rename(path, f"videos/{new_name}")
                except:
                    pass

try:
    os.mkdir("videos")
except:
    pass

bot = TwitVideo()
bot.run(token())
