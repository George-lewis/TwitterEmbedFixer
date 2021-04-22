import os
import re

import discord
from crayons import *
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError, ExtractorError


def cprint(string: str, color):
    print(color(string))


def token():
    with open("discord_token.txt") as file:
        return file.read()


class SilentLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


ydl = YoutubeDL({"outtmpl": "videos/%(id)s.mp4", "logger": SilentLogger()})

TWITTER_LINK_REGEX = re.compile(r"https://twitter.com/\w{3,}/status/(\d{19})")

cache = [filename.split(".")[0] for filename in os.listdir("videos") or []]


class TwitVideo(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {blue(self.user)}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        match = TWITTER_LINK_REGEX.search(message.content)

        if not match:
            return

        link = match.group(0)
        status = match.group(1)

        cprint(link, blue)

        if status in cache:
            cprint("CACHED", green)
        else:
            try:
                ydl.download([link])
                cprint("DOWNLOAD", yellow)
                cache.append(status)
            except (DownloadError, ExtractorError):
                cprint("SKIP", red)
                return
            except Exception as e:
                cprint(f"ERROR: {e}")
                return

        with open(f"videos/{status}.mp4", "rb") as file:
            message = await message.reply(file=discord.File(file), mention_author=False)


bot = TwitVideo()
bot.run(token())
