import io
import re

import aiohttp
import discord
from crayons import *
from youtube_dl import YoutubeDL


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

#
# Adapted from youtube_dl's source code
# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/extractor/twitter.py
#
TWITTER_LINK_REGEX = re.compile(
    r"https?://(?:(?:www|m(?:obile)?)\.)?twitter\.com/.+/status/\d+"
)

ydl_opts = {
    'logger': SilentLogger(),
}


class TwitVideo(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {blue(self.user)}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        matches = TWITTER_LINK_REGEX.findall(message.content)

        if not matches:
            return

        for match in matches:
            cprint(match, blue)

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(match, download=False)
            except Exception as e:
                cprint(f"Extraction error: {e}", red)
                continue

            if "url" not in info:
                continue

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(info["url"]) as resp:
                        size = int(resp.headers.get("Content-Length"))
                        if size > message.guild.filesize_limit:
                            await message.reply("Video is too large to upload")
                            continue
                        buffer = io.BytesIO(await resp.read())
            except Exception as e:
                cprint(f"Http error: {e}", red)
                continue

            status_id = match.split("/status/")[1]

            await message.reply(
                file=discord.File(fp=buffer, filename=f"{status_id}.mp4"),
                mention_author=False
            )


if __name__ == "__main__":
    bot = TwitVideo()
    bot.run(token())
