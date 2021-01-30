from discord import Client, File as DiscordFile  # type: ignore
from dotenv import load_dotenv  # type: ignore
from os import getenv, path

from analyze import analyze, draw
from get_data import get_data
from symbols import Symbol, SYMBOLS

# Environment variables that should be defined for these functions:
# - DISCORD_BOT_TOKEN
# - DISCORD_CHANNEL_ID
load_dotenv()


class BotClient(Client):
    """
    Discord bot for printing out stock analysis
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        """
        When the bot is ready, start analyzing stocks via main
        """
        print("Logged in as {0} ({1})".format(self.user.name, self.user.id))
        await main(self)

    async def post(self, message, filename):
        """
        Post a message with attached file to channel

        :param message: message
        :param filename: file to be attached with the message
        """
        channel = self.get_channel(int(getenv("DISCORD_CHANNEL_ID")))
        with open(filename, mode="rb") as file:
            await channel.send(content=message, file=DiscordFile(file))


async def main(bot):
    """
    Loop through symbols, analyze them and post to discord the
    ones that have been highlighted

    :param bot: discord bot client
    """
    print("Analyzing stock data and posting to discord")
    for (index, symbol) in enumerate(SYMBOLS):
        print("{0} ({1}/{2})".format(symbol.name, index + 1, len(SYMBOLS)))
        (df, highlight, summary) = analyze(symbol)
        if highlight:
            filename = draw(symbol, df)
            await bot.post(summary, filename)


get_data()
client = BotClient()
client.run(getenv("DISCORD_BOT_TOKEN"))
