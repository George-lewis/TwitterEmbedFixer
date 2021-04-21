from functools import cache

@cache
def token():
    with open("discord_token.txt") as file:
        return file.read()

