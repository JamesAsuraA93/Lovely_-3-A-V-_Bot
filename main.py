import os
import discord
import json
from replit import db
import keep_alive


keys = db.keys()
if "vote" not in keys or "textCh" not in keys or "userID" not in keys:
    print("__init__ db[]")
    db["vote"] = {"vote1": 0, "vote2": 0}
    db["textCh"] = 0
    db["userID"] = []

file = open('config.json')
config = json.load(file)
command_list = config['command']
bam_message = config['bam_message']


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):

        # don't respond to ourselves
        if message.author == self.user:
            return

        ln = len(config["prefix"])
        prefix = message.content[0:ln]
        command = message.content[ln:].strip().split(
            " ") if message.content[ln:] != "" else [""]
        print(prefix)
        print(command)
        #print(type(command))

        if prefix != config["prefix"]:
            print("wrong prefix")
            return
        
        if command[0] == command_list["create"]:
            channel = await message.guild.create_text_channel(
                config["channel_name"], )
            db["textCh"] = channel.id
            await message.channel.send(bam_message["create_room"].format(
                config["channel_name"]))
            return
        if command[0] == command_list["setup"]:
            print("setup")
            if db["textCh"] != 0:
                await message.channel.send(bam_message["create_room_already"])
                return
            channel = await message.guild.create_text_channel(
                config["channel_name"], )
            db["textCh"] = channel.id
            await message.channel.send(bam_message["create_room"].format(
                config["channel_name"]))
            return

        if db["textCh"] == 0 and command[0] != command_list["setup"]:
            print("unsetup")
            await message.channel.send(bam_message["setup_me_first"])
            await message.channel.send(
                bam_message["setup_me_with_key_words"].format(
                    config["prefix"], command_list["setup"]))
            return

        if message.channel.id != db["textCh"]:
            await message.channel.send(bam_message["let_talk_in_my_room"])
            return

        def switch(command):
            switcher = {
                command_list["vote1"]: vote1,
                command_list["vote2"]: vote2,
                command_list["callback"]: missyou,
                command_list["result"]: result,
                command_list["reset"]: reset,
                command_list["clear"]: clearroom,
                command_list["list_of_command"]: list_command
            }
            return switcher.get(command, whatthefuq)

        async def whatthefuq():
            await message.channel.send(
                bam_message["pls_type_correctly"].format(
                    config["prefix"] + command_list['list_of_command']))

        async def reset():
            db["vote"] = {"vote1": 0, "vote2": 0}
            # db["textCh"] = 0
            await message.channel.send(bam_message["reset_already"])
        
        async def clearroom():
            db["vote"] = {"vote1": 0, "vote2": 0}
            db["textCh"] = 0
            await message.channel.send(bam_message["clear_room"])

        async def vote1():
            if authorId in db["userID"]:
                await message.channel.send(bam_message["you_said"])
                return
            await message.channel.send(bam_message["vote1"])
            print("Vote1")
            db["vote"]["vote1"] += 1
            done_voting()

        async def vote2():
            if authorId in db["userID"]:
                await message.channel.send(bam_message["you_said"])
                return
            await message.channel.send(bam_message["vote2"])
            print("Vote2")
            db["vote"]["vote2"] += 1
            done_voting()

        async def list_command():
            text = 'เรียก {} ตามด้วยคำสั่งด้านล่าง\n'.format(config["prefix"])
            count = 1
            for s in command_list:
                if s != "callback":
                    s = command_list[s]
                    text += '{}). {}\n'.format(count, s)
                    count += 1
            await message.channel.send(text)

        async def result():
            print("Result")
            result = [db["vote"]["vote1"], db["vote"]["vote2"]]
            print(db["userID"])
            await message.channel.send(result)

        def done_voting():
            db["userID"].append(authorId)

        async def missyou():
            author_user = message.author
            dm_channel = await author_user.create_dm()
            await dm_channel.send(bam_message["i_miss_you_too"].format(
                message.author.name))

        # Driver
        authorId = message.author.id
        switch_fn = switch(command[0])
        await switch_fn()


keep_alive.keep_alive()
secret_token = os.getenv("TOKEN")
if secret_token:
  print("The secret TOKEN is:", secret_token)
  client = MyClient().run(secret_token)
else:
  print("Looks like you're not the owner")


