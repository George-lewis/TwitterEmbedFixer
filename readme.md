# Twitter Embed Fixer

[![Python](https://github.com/George-lewis/TwitterEmbedFixer/actions/workflows/ci.yml/badge.svg?branch=master&event=push)](https://github.com/George-lewis/TwitterEmbedFixer/actions/workflows/ci.yml)

A simple Discord bot that fixes broken Twitter video embeds

## Screenshot

![](https://github.com/George-lewis/TwitterEmbedFixer/blob/master/resources/screenshot.png)

## Mechanism

The bot:

- Listens for messages with Twitter links
- Downloads the video using YoutubeDL
- Uploads the file as a reply to the original message