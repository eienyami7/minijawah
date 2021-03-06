import math
import os
import random
import time
import re

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

dbx = dropbox.Dropbox(oauth2_access_token=os.environ["DROPBOX_TOKEN"],
                      oauth2_refresh_token=os.environ["DROPBOX_REFRESH_TOKEN"],
                      app_key=os.environ["DROPBOX_KEY"],
                      app_secret=os.environ["DROPBOX_SECRET"])
dbx.refresh_access_token()
overwrite = dropbox.files.WriteMode.overwrite


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=AUTH_TOKEN, prefix=prefix, initial_channels=initial_channels)
        self.last_invocation_time = dict()
        md, res = dbx.files_download("/minijawah/trusted.txt")
        self.trusted_members = res.content.decode("utf-8").split("\n")
        self.stream_queue = list()

    async def event_ready(self):
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        if message.echo:
            return

        if re.match(r"^hello there[.!]*$", message.content.lower()):
            await message.channel.send("General Kenobi!")

        if re.match(r"^first[ !.]*$", message.content.lower()):
            randomizer = random.randint(1, 2)
            if randomizer == 1:
                response_string = f"Are you though {message.author.name}?"
            else:
                response_string = f"No you are not {message.author.name}"
            await message.channel.send(response_string)

        if re.match(r"[??38O@Cc???QG]*[=\-]+[DoO08B]", message.content):
            message_id = message.tags['id']
            await message.channel.send(f"/delete {message_id}")
            await message.channel.send(f"Don't be a dick {message.author.name}")

        if re.match(r"[??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????]"
                    r"{3, }", message.content):
            message_id = message.tags['id']
            await message.channel.send(f"/delete {message_id}")
            await message.channel.send(f"Try joining art school {message.author.name}")

        if re.match(r"[\\\-_/?,=|();:]{10,}", message.content):
            message_id = message.tags['id']
            await message.channel.send(f"/delete {message_id}")
            await message.channel.send(f"These are not the signs I was looking for {message.author.name}")
        await self.handle_commands(message)

    def cooldown_checker(self, input_command, input_cooldown=COMMAND_TIME_COOLDOWN):
        if input_command not in self.last_invocation_time:
            self.last_invocation_time[input_command] = time.time()
        else:
            time_diff = time.time() - self.last_invocation_time[input_command]
            if time_diff < input_cooldown:
                return f"Please wait for {math.ceil(input_cooldown - time_diff)} second(s) " \
                       f"before using the command again."
        self.last_invocation_time[input_command] = time.time()
        return False

    def refresh_token(self):
        print("refreshing token")
        global JAWAH_AUTH_TOKEN
        response = requests.post("https://id.twitch.tv/oauth2/token?grant_type=refresh_token"
                                 f"&refresh_token={JAWAH_REFRESH_TOKEN}"
                                 f"&client_id={CLIENT_ID}"
                                 f"&client_secret={CLIENT_SECRET}")
        if response.status_code == 200:
            JAWAH_AUTH_TOKEN = response.json()["access_token"]
            dotenv.set_key(".env", "JAWAH_AUTH_TOKEN", JAWAH_AUTH_TOKEN)
            return True

    @commands.command(name="lookjake")
    async def lookjake(self, ctx: commands.Context):
        if ctx.author.name in self.trusted_members:
            is_on_cooldown = self.cooldown_checker("lookjake")
            if is_on_cooldown:
                response_string = is_on_cooldown
            else:
                randomizer = random.randint(1, 5)
                if randomizer % 2 == 0:
                    response_string = 'It is Luna but with pirate hat!'
                elif randomizer % 2 == 1:
                    response_string = 'IODabs'
                else:
                    response_string = "Shut up @" + ctx.author.name
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
                    tagged_person = message.split(' ', 1)[1]
                    if "minijawah" in tagged_person.lower():
                        response_string = "How about I put you to bed and tuck you in @" + ctx.author.name
                    elif randomizer == 5:
                        response_string = "How about you go to bed @" + ctx.author.name
                    else:
                        response_string = "Go to bed " + tagged_person
                await ctx.send(response_string)

    @commands.command(name="randomize")
    async def randomize(self, ctx: commands.Context):
        if ctx.author.name in self.trusted_members:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                response_string = "No names provided"
            else:
                name_list = message.split(' ')[1:]
                if len(name_list) == 5:
                    random.shuffle(name_list)
                    response_string = f"Killer:{name_list[0]}, survivors:{', '.join(name_list[1:])}"
                else:
                    response_string = "Please enter only 5 names"
            await ctx.send(response_string)

    @commands.command(name="queue")
    async def queue(self, ctx: commands.Context):
        if ctx.author.name in self.trusted_members:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                response_string = f"Current Queue: {', '.join(self.stream_queue)}"
            else:
                objects = message.split(' ')[1:]
                self.stream_queue.extend(objects)
                response_string = f"Current Queue: {', '.join(self.stream_queue)}"
            await ctx.send(response_string)

    @commands.command(name="qpop")
    async def qpop(self, ctx: commands.Context):
        if ctx.author.name in self.trusted_members:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                response_string = f"{self.stream_queue.pop(0)} removed from queue"
            else:
                qobject = message.split(' ', 1)[1]
                if qobject in self.stream_queue:
                    self.stream_queue.remove(qobject)
                    response_string = f"{qobject} removed from queue"
                else:
                    response_string = f"{qobject} not in queue"
            await ctx.send(response_string)

    @commands.command(name="qwipe")
    async def qwipe(self, ctx: commands.Context):
        if ctx.author.name in self.trusted_members:
            self.stream_queue = list()
            response_string = "Queue cleaned"
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
                    try:
                        dbx.files_upload(bytes(updated_content, "utf-8"), "/minijawah/trusted.txt", mode=overwrite)
                    except dropbox.exceptions.AuthError:
                        dbx.check_and_refresh_access_token()
                        dbx.files_upload(bytes(updated_content, "utf-8"), "/minijawah/trusted.txt", mode=overwrite)
                    response_string = f"{tagged_user} is not trusted anymore."
            await ctx.send(response_string)

    @commands.command(name="title")
    async def title(self, ctx: commands.Context):
        if ctx.author.name in self.trusted_members:
            is_on_cooldown = self.cooldown_checker("title", 150)
            if is_on_cooldown:
                await ctx.send(is_on_cooldown)
            else:
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
                    if response.status_code == 401:
                        self.refresh_token()
                        headers = {
                            'Authorization': "Bearer " + JAWAH_AUTH_TOKEN,
                            'Client-Id': CLIENT_ID,
                            'Content-Type': 'application/json'
                        }
                        response = requests.patch(url=url, headers=headers, data=data.encode('utf-8'))
                    if response.status_code == 204:
                        await ctx.send(f'Title successfully changed to -> "{title}"')

    @commands.command(name="game")
    async def game(self, ctx: commands.Context):
        if ctx.author.is_broadcaster or ctx.author.is_mod:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                await ctx.send("Please enter a game")
            else:
                game = message.split(' ', 1)[1]
                url = 'https://api.twitch.tv/helix/games?name=' + game
                headers = {
                    'Authorization': "Bearer " + JAWAH_AUTH_TOKEN,
                    'Client-Id': CLIENT_ID
                }
                response = requests.get(url=url, headers=headers)
                if response.status_code == 401:
                    self.refresh_token()
                    headers = {
                        'Authorization': "Bearer " + JAWAH_AUTH_TOKEN,
                        'Client-Id': CLIENT_ID
                    }
                    response = requests.get(url=url, headers=headers)

                response = response.json()
                game_id = response["data"][0]["id"]
                game_name = response["data"][0]["name"]

                url = 'https://api.twitch.tv/helix/channels?broadcaster_id=' + JAWAH_BROADCASTER_ID
                headers = {
                    'Authorization': "Bearer " + JAWAH_AUTH_TOKEN,
                    'Client-Id': CLIENT_ID,
                    'Content-Type': 'application/json'
                }
                data = f'{{"game_id":"{game_id}"}}'
                response = requests.patch(url=url, headers=headers, data=data.encode('utf-8'))
                if response.status_code == 204:
                    await ctx.send(f'Category changed to -> "{game_name}"')

    @commands.command(name="marker")
    async def marker(self, ctx: commands.Context):
        if ctx.author.is_broadcaster or ctx.author.is_mod:
            message = str(ctx.message.content)
            if len(message.split(" ")) == 1:
                await ctx.send("Please enter a game")
            marker_description = message.split(' ', 1)[1]
            url = 'https://api.twitch.tv/helix/streams/markers'
            headers = {
                'Authorization': 'Bearer ' + JAWAH_AUTH_TOKEN,
                'Client-Id': CLIENT_ID,
                'Content-Type': 'application/json',
            }
            data = f"{{'user_id': '{JAWAH_BROADCASTER_ID}', 'description': '{marker_description}'}}"
            print(data)
            response = requests.get(url=url, headers=headers, data=data.encode('utf-8'))
            if response.status_code == 401:
                self.refresh_token()
                headers = {
                    'Authorization': 'Bearer ' + JAWAH_AUTH_TOKEN,
                    'Client-Id': CLIENT_ID,
                    'Content-Type': 'application/json',
                }
                response = requests.get(url=url, headers=headers, data=data.encode('utf-8'))
            print(response.json())
            if response.status_code == 204:
                await ctx.send("Marker Created!")


if __name__ == "__main__":
    bot = Bot()
    bot.run()
