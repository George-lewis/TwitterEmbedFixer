"""A discord bot that fixes Twitter video embeds"""

import io
import re

import aiohttp
import discord
from crayons import blue, red
from youtube_dl import YoutubeDL


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


#
# Adapted from youtube_dl's source code
# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/extractor/twitter.py
#
TWITTER_LINK_REGEX = re.compile(
    r"https?://(?:(?:www|m(?:obile)?)\.)?twitter\.com/.+/status/\d+"
)

YDL_OPTS = {
    'logger': SilentLogger(),
}


class TwitVideo(discord.Client):
    """Our bot"""

    def __init__(self):
        super().__init__()
        self.ydl = YoutubeDL(YDL_OPTS)

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
                info = self.ydl.extract_info(match, download=False)
            except Exception as e:  # pylint: disable=broad-except
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
            except Exception as e:  # pylint: disable=broad-except
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
