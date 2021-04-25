"""The bot"""

import io
from functools import partial
from typing import Dict

import aiohttp
from crayons import blue, green, red, yellow
from discord import Client, Message, File as DiscordFile
from youtube_dl import YoutubeDL

from errors import FileSizeException, NoVideoException
from util import TWITTER_LINK_REGEX, YDL_OPTS, cprint


# pylint: disable=missing-class-docstring
class TwitterVideoBot(Client):
    def __init__(self):
        super().__init__()
        self.ydl = YoutubeDL(YDL_OPTS)

    async def download(self, url: str, message: Message) -> io.BytesIO:
        """
        Download `url` into a buffer and return it
        :param url: The downloadable url of a video
        :param message: The message the video link is from
        :return: A BytesIO object containing the video data
        :raises: FileSizeException when the video is larger than Discord allows
        """
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(url) as resp:
                size = int(resp.headers.get("Content-Length", "0"))
                limit = message.guild.filesize_limit
                if size > limit:
                    raise FileSizeException(size, limit)

                #
                # Process chunks as they come in
                #
                resp_bytes = bytearray()
                async for data, _ in resp.content.iter_chunks():
                    resp_bytes.extend(data)
                    if len(resp_bytes) > limit:
                        raise FileSizeException(size, limit)

                return io.BytesIO(resp_bytes)

    def extract_info(self, url: str) -> Dict:
        """
        Extracts the info of a Twitter url
        :param url: The URL of the Twitter status
        :return: The info dict
        :raises: NoVideoException if this Tweet doesn't have a video
        """
        try:
            return self.ydl.extract_info(url, download=False)
        except Exception as ex:  # pylint: disable=broad-except
            if str(ex).startswith("ERROR: There's no video in this tweet"):
                raise NoVideoException  # pylint: disable=raise-missing-from
            raise

    # pylint: disable=missing-function-docstring
    async def on_ready(self):
        print(f"Logged in as {blue(self.user)}")

    # pylint: disable=missing-function-docstring
    async def on_message(self, message: Message):
        if message.author == self.user:
            return

        matches = TWITTER_LINK_REGEX.findall(message.content)

        if not matches:
            return

        reply = partial(message.reply, mention_author=False)

        for match in matches:
            cprint(match, blue)

            try:
                info = self.extract_info(match)
            except NoVideoException:
                cprint("Tweet has no video", yellow)
                continue
            except Exception as ex:  # pylint: disable=broad-except
                cprint(f"Extraction error: {ex}", red)
                await reply("Failed to download video")
                continue

            if "url" not in info:
                continue

            try:
                buffer = await self.download(info["url"], message)
            except FileSizeException as ex:
                cprint(f"Not uploading, file is too large: {ex.filesize} > {ex.limit}", red)
                await reply("Video is too large to upload")
                continue
            except Exception as ex:  # pylint: disable=broad-except
                cprint(f"Http error: {ex}", red)
                await reply("Failed to download video")
                continue

            status_id = match.split("/status/")[1]

            await reply(file=DiscordFile(fp=buffer, filename=f"{status_id}.mp4"))

            cprint("Upload success", green)
