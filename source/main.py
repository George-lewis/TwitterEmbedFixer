
"""A discord bot that fixes Twitter video embeds"""

import os
import re

import discord
from crayons import blue, green, yellow, red
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError, ExtractorError


def cprint(string: str, color):
    """Print with a color"""
    print(color(string))


def token() -> str:
    """Get the Discord token"""
    with open("discord_token.txt") as file:
        return file.read()


# pylint: disable=missing-function-docstring
class SilentLogger:
    """Ignores logging"""
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


ydl = YoutubeDL({"outtmpl": "videos/%(id)s.mp4", "logger": SilentLogger()})

TWITTER_LINK_REGEX = re.compile(r"https://twitter.com/\w{3,}/status/(\d{19})")

cache = {filename.split(".")[0] for filename in os.listdir("videos") or []}


class TwitVideo(discord.Client):
    """Our bot"""
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
                cache.add(status)
            except (DownloadError, ExtractorError) as error:
                cprint(f"SKIP: {error}", red)
                return
            except Exception as error: # pylint: disable=broad-except
                cprint(f"ERROR: {error}", red)
                return

        with open(f"videos/{status}.mp4", "rb") as file:
            message = await message.reply(file=discord.File(file), mention_author=False)


bot = TwitVideo()
bot.run(token())
