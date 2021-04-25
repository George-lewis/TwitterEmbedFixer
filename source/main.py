"""A discord bot that fixes Twitter video embeds"""

from bot import TwitterVideoBot
from util import token

if __name__ == "__main__":
    TwitterVideoBot().run(token())
