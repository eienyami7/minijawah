import math
import os
import random
import time

import dotenv
import dropbox
import requests
from twitchio.ext import commands

dotenv.load_dotenv('.env')
AUTH_TOKEN = os.environ['TMI_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
JAWAH_AUTH_TOKEN = os.environ['JAWAH_AUTH_TOKEN']
JAWAH_BROADCASTER_ID = os.environ['JAWAH_BROADCASTER_ID']
JAWAH_REFRESH_TOKEN = os.environ["JAWAH_REFRESH_TOKEN"]
prefix = os.environ['BOT_PREFIX']
initial_channels = os.environ['CHANNEL'].split(",")
API_URL = "https://api.twitch.tv/kraken/channels/"
DISCORD_URL = "https://discord.com/invite/h3yWGf3"
TWITTER_URL = "https://twitter.com/JawahTV"
YOUTUBE_URL = "https://www.youtube.com/channel/UC0Uui0gxffT5p8HTqUp1e1g"
COMMAND_TIME_COOLDOWN = 5

dbx = dropbox.Dropbox(os.environ["DROPBOX_TOKEN"])
overwrite = dropbox.files.WriteMode.overwrite


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=AUTH_TOKEN, prefix=prefix, initial_channels=initial_channels)
        self.last_invocation_time = dict()
        md, res = dbx.files_download("/minijawah/trusted.txt")
        self.trusted_members = res.content.decode("utf-8").split("\n")

    async def event_ready(self):
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
        if ctx.author.name in self.trusted_members:
            is_on_cooldown = self.cooldown_checker("lookjake")
            if is_on_cooldown:
                response_string = is_on_cooldown
            else:
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
        if ctx.author.name in self.trusted_members:
            is_on_cooldown = self.cooldown_checker("bed")
            if is_on_cooldown:
                await ctx.send(is_on_cooldown)
            else:
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
            response_string = is_on_cooldown
        else:
            response_string = f"Join Discord: {DISCORD_URL}"
        await ctx.send(response_string)

    @commands.command(name="twitter")
    async def twitter(self, ctx: commands.Context):
        is_on_cooldown = self.cooldown_checker("twitter")
        if is_on_cooldown:
            response_string = is_on_cooldown
        else:
            response_string = f"My Twitter: {TWITTER_URL}"
        await ctx.send(response_string)

    @commands.command(name="youtube")
    async def youtube(self, ctx: commands.Context):
        is_on_cooldown = self.cooldown_checker("youtube")
        if is_on_cooldown:
            response_string = is_on_cooldown
        else:
            response_string = f"My YouTube: {YOUTUBE_URL}"
        await ctx.send(response_string)

    @commands.command(name="trusted")
    async def trusted(self, ctx: commands.Context):
        if ctx.author.is_broadcaster or ctx.author.is_mod:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                response_string = "Please tag a person."
            else:
                tagged_user = message.split(' ', 1)[1].strip("@").lower()
                if tagged_user in self.trusted_members:
                    response_string = f"{tagged_user} is already trusted! Or are they? * Vsauce music *"
                else:
                    md, res = dbx.files_download("/minijawah/trusted.txt")
                    new_content = res.content + bytes("\n" + tagged_user, "utf-8")
                    dbx.files_upload(new_content, "/minijawah/trusted.txt", mode=overwrite)
                    self.trusted_members.append(tagged_user)
                    response_string = f"{tagged_user} is now trusted. You are now invited to next JawahCon!"
            await ctx.send(response_string)

    @commands.command(name="untrusted")
    async def untrusted(self, ctx: commands.Context):
        if ctx.author.is_broadcaster or ctx.author.is_mod:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                response_string = "Please tag a person."
            else:
                tagged_user = message.split(' ', 1)[1].strip("@").lower()
                if tagged_user not in self.trusted_members:
                    response_string = f"{tagged_user} were never trusted! They are quite sus."
                else:
                    self.trusted_members.remove(tagged_user)
                    updated_content = "\n".join(self.trusted_members)
                    dbx.files_upload(bytes(updated_content, "utf-8"), "/minijawah/trusted.txt", mode=overwrite)
                    response_string = f"{tagged_user} is not trusted anymore."
            await ctx.send(response_string)

    @commands.command(name="title")
    async def title(self, ctx: commands.Context):
        if ctx.author.is_broadcaster or ctx.author.is_mod:
            global JAWAH_AUTH_TOKEN
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                await ctx.send("Please enter a title")
            else:
                title = message.split(' ', 1)[1]
                url = 'https://api.twitch.tv/helix/channels?broadcaster_id=' + JAWAH_BROADCASTER_ID
                headers = {
                    'Authorization': "Bearer " + JAWAH_AUTH_TOKEN,
                    'Client-Id': CLIENT_ID,
                    'Content-Type': 'application/json'
                }
                data = f'{{"title":"{title}"}}'
                response = requests.patch(url=url, headers=headers, data=data.encode('utf-8'))
                if response.status_code == 204:
                    await ctx.send(f'Title successfully changed to -> "{title}"')
                elif response.status_code == 401:
                    response = requests.post("https://id.twitch.tv/oauth2/token?grant_type=refresh_token"
                                             f"&refresh_token={JAWAH_REFRESH_TOKEN}"
                                             f"&client_id={CLIENT_ID}"
                                             f"&client_secret={CLIENT_SECRET}")
                    if response.status_code == 200:
                        JAWAH_AUTH_TOKEN = response.json()["access_token"]
                        dotenv.set_key(".env", "JAWAH_AUTH_TOKEN", JAWAH_AUTH_TOKEN)
                        response = requests.patch(url=url, headers=headers, data=data.encode('utf-8'))
                        if response.status_code == 204:
                            await ctx.send(f'Title successfully changed to -> "{title}"')


# TODO: Add game change command ?game


if __name__ == "__main__":
    bot = Bot()
    bot.run()
