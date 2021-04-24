# Twitter Embed Fixer

A simple Discord bot that fixes broken Twitter video embeds

## Mechanism

The bot:

- Listens for messages with Twitter links
- Downloads the video using YoutubeDL, if it hasn't been cached
- Uploads the file as a reply to the original message

### Warning

The cache grows indefinitely and must be cleaned manually 