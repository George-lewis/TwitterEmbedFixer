"""Utilities"""

from typing import Dict

import re
from functools import cache
from io import BytesIO

import aiohttp
from youtube_dl import YoutubeDL

from errors import FileSizeException, NoVideoException

#
# Adapted from youtube_dl's source code
# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/extractor/twitter.py
#
TWITTER_LINK_REGEX = re.compile(r"https?://(?:(?:www|m(?:obile)?)\.)?twitter\.com/.+/status/\d+")


def cprint(string: str, color):
    """Print with a color"""
    print(color(string))


def token() -> str:
    """Get the Discord token"""
    with open("discord_token.txt") as file:
        return file.read()


@cache
def youtube_dl() -> YoutubeDL:
    # pylint: disable=missing-function-docstring
    class SilentLogger:
        """Ignores logging"""

        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            pass

    return YoutubeDL(
        {
            "logger": SilentLogger(),
        }
    )


async def download(url: str, limit: int) -> BytesIO:
    """
    Download `url` into a buffer and return it
    :param url: The downloadable url of a video
    :param limit: The maximum size the file can be
    :return: A BytesIO object containing the video data
    :raises: FileSizeException when the video is larger than `limit`
    """
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as resp:
            size = int(resp.headers.get("Content-Length", 0))
            if size > limit:
                raise FileSizeException(limit, size)

            # Process chunks as they come in.
            resp_bytes = bytearray()
            async for data, _ in resp.content.iter_chunks():
                resp_bytes.extend(data)
                if len(resp_bytes) > limit:
                    raise FileSizeException(limit)

            return BytesIO(resp_bytes)


def extract_info(url: str) -> Dict:
    """
    Extracts the info of a Twitter url
    :param url: The URL of the Twitter status
    :return: The info dict
    :raises: NoVideoException if this Tweet doesn't have a video
    """
    try:
        return youtube_dl().extract_info(url, download=False)
    except Exception as ex:  # pylint: disable=broad-except
        if str(ex).startswith("ERROR: There's no video in this tweet"):
            raise NoVideoException  # pylint: disable=raise-missing-from
        raise
