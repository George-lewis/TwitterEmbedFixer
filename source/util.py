"""Utilities"""

import re

#
# Adapted from youtube_dl's source code
# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/extractor/twitter.py
#
TWITTER_LINK_REGEX = re.compile(
    r"https?://(?:(?:www|m(?:obile)?)\.)?twitter\.com/.+/status/\d+"
)

# pylint: disable=missing-function-docstring
class SilentLogger:
    """Ignores logging"""

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

YDL_OPTS = {
    "logger": SilentLogger(),
}

def cprint(string: str, color):
    """Print with a color"""
    print(color(string))


def token() -> str:
    """Get the Discord token"""
    with open("discord_token.txt") as file:
        return file.read()

