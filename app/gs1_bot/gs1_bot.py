import os
import json
import datetime

import requests
import discord
import dotenv

from logger import Logger

logger = Logger()
dotenv.load_dotenv()

TOKEN = os.environ.get("GS_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = discord.Client(intents=intents)

VC_channel = int(os.environ.get("GS_Voice_Channel"))
Text_channel = int(os.environ.get("GS_Text_Channel"))

LINE_TOKENS = os.environ.get("GS_LINE_TOKENS").split(",")

data_json_path = "app/gs1_bot/data.json"

async def save_data(data):
    with open(data_json_path, "w", encoding="UTF-8") as f:
        json.dump(data, f, indent=4)

async def load_data():
    with open(data_json_path, "r", encoding="UTF-8") as f:
        return json.load(f)

def timedelta_to_string(td: datetime.timedelta) -> str:
    seconds = int(td.total_seconds())
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if td.days > 0:
        hours += td.days * 24
    return f"{hours:02d}時間{minutes:02d}分{seconds:02d}秒"

async def post_line(text):
    for l_token in LINE_TOKENS:
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {l_token}'}
        data = {'message': f'{text}'}
        requests.post(line_notify_api, headers = headers, data = data)

def gs1_main():
    @client.event
    async def on_ready():
        logger.info(f'We have logged in as {client.user}')
    
    @client.event
    async def on_voice_state_update(member, before, after):
        if before.channel != after.channel and not member.bot:
            if before.channel is None and after.channel.id == VC_channel:
                members = [member for member in after.channel.members if not member.bot]
                if len(members) == 1:
                    channel = client.get_channel(Text_channel)
                    logger.info(f"{member.name} が通話を開始しました")
                    data = await load_data()
                    started_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    data["Started_time"] = started_time
                    await save_data(data)
                    if member.nick is not None:
                        name = member.nick
                    else:
                        name = member.name
                    embed = discord.Embed(
                        title=f"{name} が通話を開始しました",
                        color=0x4169e1
                    )
                    await channel.send(embed=embed)
    
                logger.info(f"{member.name} が参加しました。")
    
            elif after.channel is None and before.channel.id == VC_channel:
                members = [member for member in before.channel.members if not member.bot]
                logger.info(f"{member.name} が退出しました。")
                if len(members) == 0:
                    channel = client.get_channel(Text_channel)
                    data = await load_data()
                    if "Started_time" in data and not data["Started_time"] == "None":
                        started_time = datetime.datetime.strptime(data["Started_time"], "%Y/%m/%d %H:%M:%S")
                        now_time = datetime.datetime.now()
                        talking_time: str = timedelta_to_string(now_time - started_time)
                        data["Started_time"] = "None"
                        await save_data(data)
                        logger.info(f"{member.name} が通話を終了しました。")
                        if member.nick is not None:
                            name = member.nick
                        else:
                            name = member.name
                        logger.info(f"通話時間：{talking_time}")
                        embed = discord.Embed(
                            title=f"{name} が通話を終了しました",
                            description=f"通話時間：{talking_time}\n通話開始時刻：{started_time.strftime('%Y/%m/%d %H:%M:%S')}\n通話終了時刻：{now_time.strftime('%Y/%m/%d %H:%M:%S')}",
                            color=0xff1493
                        )
                        await channel.send(embed=embed)
    
                    else:
                        logger.info(f"{member.name} が通話を終了しました。")
                        if member.nick is not None:
                            name = member.nick
                        else:
                            name = member.name
                        embed = discord.Embed(
                            title=f"{name} が通話を終了しました",
                            description="--  通話開始データが存在しません  --",
                            color=0xff1493
                        )
                        await channel.send(embed=embed)
    
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
    
        else:
            await post_line(f"Channel: {message.channel.name}\nUser: {message.author}\n{message.content}")
    
    client.run(TOKEN)