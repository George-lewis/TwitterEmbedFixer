"""Utilities"""

from typing import Callable, Dict, Generator, Tuple

import re
from functools import cache
from io import BytesIO
from os import getenv, path

import aiohttp
from crayons import yellow
from tenacity import retry, retry_base, stop_after_attempt, wait_exponential
from youtube_dl import YoutubeDL
from youtube_dl.version import __version__ as ydl_version

from errors import FileSizeException, NoVideoException

# Adapted from youtube_dl's source code
# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/extractor/twitter.py
TWITTER = re.compile(r"https?://(?:(?:www|m(?:obile)?)\.)?twitter\.com/.+/status/(\d+)")
FXTWITTER = re.compile(r"https?://(?:www\.)?fxtwitter.com/.+/status/(\d+)")
REDGIF = re.compile(r"https?://(?:www\.)?redgifs\.com/watch/(\w+)")

LINK_REGEXES = [TWITTER, FXTWITTER]


def extract_links(content: str) -> Generator[Tuple[str, str], None, None]:
    """
    Extract links for all supported sites from the input string
    :param content: The text
    :return: A generator that yields (str: link, str: filename)
    """
    for regex in LINK_REGEXES:
        for match in regex.finditer(content):
            yield (match.group(0), match.group(1))


def cprint(string: str, color: Callable):
    """Print with a color"""
    print(color(string))


DISCORD_TOKEN_FILE = "discord_token.txt"
DISCORD_TOKEN_ENV = "DISCORD_TOKEN"


def token() -> str:
    """Get the Discord token"""
    if path.exists(DISCORD_TOKEN_FILE):
        with open(DISCORD_TOKEN_FILE, encoding="utf-8") as file:
            return file.read()
    return getenv(DISCORD_TOKEN_ENV)


@cache
def youtube_dl() -> YoutubeDL:
    """Get a YoutubeDL instance"""
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
            # Force IPv4
            "source_address": "0.0.0.0",
        }
    )


# pylint: disable=invalid-name,too-few-public-methods
class my_retry_predicate(retry_base):
    """Retries if the function raises an error that is not one of ours."""

    def __call__(self, retry_state):
        if retry_state.outcome.failed:
            ex = retry_state.outcome.exception()
            return not isinstance(ex, (NoVideoException, FileSizeException))
        return False


@retry(retry=my_retry_predicate(), stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=3, max=8))
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


@retry(retry=my_retry_predicate(), stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=3, max=8))
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
        strex = str(ex)
        if strex.startswith("ERROR: There's no video in this tweet"):
            raise NoVideoException  # pylint: disable=raise-missing-from
        if strex.startswith("ERROR: Unsupported URL"):
            raise NoVideoException  # pylint: disable=raise-missing-from
        if strex == "ERROR: Bad guest token.":
            cprint("Bad guest token, trying again with new YDL", yellow)

            # This will force a fresh YDL instance
            # Solving the guest token issue
            youtube_dl.cache_clear()
            return extract_info(url)
        print(f"Unknown Error: {strex}")
        raise
