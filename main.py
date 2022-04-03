import math
import os
import random
import time

import requests
from dotenv import load_dotenv
from twitchio.ext import commands
from github import Github

load_dotenv('.env')
AUTH_TOKEN = os.environ['TMI_TOKEN']
BOT_CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_ID = "9ggr8vllhbakby13wq85giayqykkfx"
CLIENT_SECRET = "edq9plpecwlny3d0095i8lgliz5f8u"
JAWAH_AUTH_TOKEN = os.environ['JAWAH_AUTH_TOKEN']
nick = os.environ['BOT_NICK']
prefix = os.environ['BOT_PREFIX']
initial_channels = os.environ['CHANNEL'].split(",")
API_URL = "https://api.twitch.tv/kraken/channels/"
DISCORD_URL = "https://discord.com/invite/h3yWGf3"
TWITTER_URL = "https://twitter.com/JawahTV"
YOUTUBE_URL = "https://www.youtube.com/channel/UC0Uui0gxffT5p8HTqUp1e1g"
COMMAND_TIME_COOLDOWN = 5

github = Github(os.environ["GIT_TOKEN"])
repository = github.get_user().get_repo('minijawah')


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=AUTH_TOKEN, prefix=prefix, initial_channels=initial_channels)
        self.last_invocation_time = dict()

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        if message.echo:
            return

        # print(message.content)
        await self.handle_commands(message)

    def cooldown_checker(self, input_command):
        if input_command not in self.last_invocation_time:
            self.last_invocation_time[input_command] = time.time()
        else:
            time_diff = time.time() - self.last_invocation_time[input_command]
            if time_diff < COMMAND_TIME_COOLDOWN:
                return f"Please wait for {math.ceil(COMMAND_TIME_COOLDOWN - time_diff)} second(s) " \
                       f"before using the command again."
        self.last_invocation_time[input_command] = time.time()
        return False

    @commands.command(name="lookjake")
    async def lookjake(self, ctx: commands.Context):
        is_on_cooldown = self.cooldown_checker("lookjake")
        if is_on_cooldown:
            await ctx.send(is_on_cooldown)
        randomizer = random.randint(1, 5)
        if randomizer == 5:
            response_string = "Shut up @" + ctx.author.name
        elif randomizer % 2 == 0:
            response_string = 'It is Luna but with pirate hat!'
        elif randomizer % 2 == 1:
            response_string = 'IODabs'
        await ctx.send(response_string)

    @commands.command(name="bed")
    async def bed(self, ctx: commands.Context):
        is_on_cooldown = self.cooldown_checker("bed")
        if is_on_cooldown:
            await ctx.send(is_on_cooldown)
        randomizer = random.randint(1, 5)
        message = str(ctx.message.content)
        if len(message.split(" ")) == 1:
            response_string = "Go to bed Roger!"
        else:
            if randomizer == 5:
                response_string = "How about you go to bed @" + ctx.author.name
            else:
                response_string = "Go to bed " + message.split(' ', 1)[1]
        await ctx.send(response_string)

    @commands.command(name="discord")
    async def discord(self, ctx: commands.Context):
        is_on_cooldown = self.cooldown_checker("discord")
        if is_on_cooldown:
            await ctx.send(is_on_cooldown)
        response_string = f"Join Discord: {DISCORD_URL}"
        await ctx.send(response_string)

    @commands.command(name="twitter")
    async def twitter(self, ctx: commands.Context):
        is_on_cooldown = self.cooldown_checker("twitter")
        if is_on_cooldown:
            await ctx.send(is_on_cooldown)
        response_string = f"My Twitter: {TWITTER_URL}"
        await ctx.send(response_string)

    @commands.command(name="youtube")
    async def youtube(self, ctx: commands.Context):
        is_on_cooldown = self.cooldown_checker("youtube")
        if is_on_cooldown:
            await ctx.send(is_on_cooldown)
        response_string = f"My YouTube: {YOUTUBE_URL}"
        await ctx.send(response_string)

    @commands.command(name="trusted")
    async def trusted(self, ctx: commands.Context):
        if ctx.author.is_broadcaster or ctx.author.is_mod:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                await ctx.send("Please tag a person.")
            else:
                tagged_user = message.split(' ', 1)[1]
                git_file = repository.get_contents("/trusted.txt")
                with open('trusted.txt', 'a', encoding='utf-8') as local_file:
                    local_file.write("\n" + tagged_user)
                    repository.update_file("/trusted.txt", "Automated bot update", local_file.read(), git_file.sha)
                # with open("trusted.txt", "r") as local_file:
                #     repository.update_file("/trusted.txt", "Automated bot update", local_file.read(), git_file.sha)

    @commands.command(name="title")
    async def title(self, ctx: commands.Context):
        if ctx.author.is_broadcaster or ctx.author.is_mod:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                await ctx.send("Please enter a title")
            else:
                title = message.split(' ', 1)[1]
                channel_id = ctx.channel.name
                url = 'https://api.twitch.tv/helix/channels?broadcaster_id=' + channel_id
                headers = {
                    'Authorization': JAWAH_AUTH_TOKEN,
                    'Client-Id': CLIENT_ID,
                    'Content-Type': 'application/json'
                }
                data = f'{{"title":"{title}"}}'
                response = requests.put(url=url, headers=headers, data=data.encode('utf-8')).json()
                if response.status_code == 200:
                    await ctx.send(f'Title successfully changed to -> "{title}"')

# TODO: Add game change command ?game


if __name__ == "__main__":
    bot = Bot()
    bot.run()
