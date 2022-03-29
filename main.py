from twitchio.ext import commands
import random
import os
from dotenv import load_dotenv
import requests


load_dotenv('.env')
AUTH_TOKEN = os.environ['TMI_TOKEN']
BOT_CLIENT_ID = os.environ['CLIENT_ID']
nick = os.environ['BOT_NICK']
prefix = os.environ['BOT_PREFIX']
initial_channels = os.environ['CHANNEL'].split(",")
API_URL = "https://api.twitch.tv/kraken/channels/"
DISCORD_URL = "https://discord.com/invite/h3yWGf3"
TWITTER_URL = "https://twitter.com/JawahTV"
YOUTUBE_URL = "https://www.youtube.com/channel/UC0Uui0gxffT5p8HTqUp1e1g"

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=AUTH_TOKEN, prefix=prefix, initial_channels=initial_channels)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        if message.echo:
            return

        # print(message.content)
        await self.handle_commands(message)

    @commands.command(name="lookjake")
    async def lookjake(self, ctx: commands.Context):
        randomizer = random.randint(1, 5)
        if randomizer == 5:
            response_string = "Shut up Fide"
        elif randomizer % 2 == 0:
            response_string = 'Its Luna with pirate hat'
        elif randomizer % 2 == 1:
            response_string = 'IODabs'
        await ctx.send(response_string)

    @commands.command(name="discord")
    async def discord(self, ctx: commands.Context):
        response_string = f"Join Discord: {DISCORD_URL}"
        await ctx.send(response_string)

    @commands.command(name="twitter")
    async def twitter(self, ctx: commands.Context):
        response_string = f"My Twitter: {TWITTER_URL}"
        await ctx.send(response_string)

    @commands.command(name="youtube")
    async def youtube(self, ctx: commands.Context):
        response_string = f"My YouTube: {YOUTUBE_URL}"
        await ctx.send(response_string)

    @commands.command(name="title")
    async def title(self, ctx: commands.Context):
        if ctx.author.is_broadcaster or ctx.author.is_mod:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                await ctx.send("Please enter a title")
            else:
                title = message.split(' ', 1)[1]
                channel_id = ctx.channel.name
                url = API_URL + channel_id
                headers = \
                    {
                        'Accept': 'application/vnd.twitchtv.v5+json',
                        "Client-ID": BOT_CLIENT_ID,
                        "Authorization": "OAuth " + AUTH_TOKEN,
                        "Content-Type": "application/json"
                    }
                data = f'{{"channel": {{"status":"{title}"}}}}'
                response = requests.put(url=url, headers=headers, data=data.encode('utf-8')).json()
                if response.status_code == 200:
                    await ctx.send(f'Title successfully changed to -> "{title}"')
                # await ctx.send(f'Title successfully changed to -> "{title}" for channel {channel_id}')


if __name__ == "__main__":
    bot = Bot()
    bot.run()
