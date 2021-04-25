"""A discord bot that fixes Twitter video embeds"""

from util import token
from bot import TwitterVideoBot

if __name__ == "__main__":
    bot = TwitterVideoBot()
    bot.run(token())
