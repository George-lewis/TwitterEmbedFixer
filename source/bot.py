"""The bot"""

from functools import partial

from crayons import blue, green, red, yellow
from discord import AutoShardedClient
from discord import File as DiscordFile
from discord import Game, Message, Status

from errors import FileSizeException, NoVideoException
from util import TWITTER_LINK_REGEX, cprint, download, extract_info, token


# pylint: disable=missing-class-docstring,missing-function-docstring
class TwitterVideoBot(AutoShardedClient):
    def run(self):  # pylint: disable=arguments-differ
        super().run(token())

    async def on_ready(self):
        print(f"Logged in as {blue(self.user)}")
        await self.change_presence(activity=Game("Created by bolt#8452"), status=Status.online)

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
                info = extract_info(match)
            except NoVideoException:
                cprint("Tweet has no video", yellow)
                continue
            except Exception as ex:  # pylint: disable=broad-except
                cprint(f"Extraction error: {ex}", red)
                await reply("Failed to download video")
                continue

            if "url" not in info:
                continue

            url = info["url"]

            try:
                buffer = await download(url, message.guild.filesize_limit)
            except FileSizeException as ex:
                if ex.filesize:
                    cprint(f"Not uploading, file is too large: {ex.filesize} > {ex.limit}", red)
                else:
                    cprint(f"Not uploading, file is larger than [{ex.limit}] bytes", red)

                cprint("Falling back to direct URL", yellow)

                # If the file is too large, we fall back to posting a direct URL
                await reply(url)

                continue

            except Exception as ex:  # pylint: disable=broad-except
                cprint(f"Http error: {ex}", red)
                await reply("Failed to download video")
                continue

            status_id = match.split("/status/")[1]

            await reply(file=DiscordFile(fp=buffer, filename=f"{status_id}.mp4"))

            cprint("Upload success", green)
