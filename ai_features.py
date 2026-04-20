import discord
from discord.ext import commands
from os import getenv
from dotenv import load_dotenv
from google.genai import Client, types
import random


load_dotenv()

all_keys = [getenv('GEN_KEY'), getenv('GEN_KEY2'), getenv('GEN_KEY3')]  
keys = [k for k in all_keys if k is not None]
if not keys:
    print("Error: No API keys found in .env file.")
else:
    client = Client(api_key=random.choice(keys))

Intents = discord.Intents.default()
Intents.message_content = True
model_name = 'gemini-2.5-flash'
AIFeature = commands.Bot(command_prefix="!", intents=Intents)

stream_update_interval = 50
@AIFeature.command()
async def send_streamed(ctx, stream, msg):
    accumulated = ""
    l_update_len = 0 
    
    async for chunk in stream:
        accumulated += chunk.text
        if len(accumulated) - l_update_len >= stream_update_interval:
            display = accumulated[:1900] + "..." if len(accumulated) >  1900 else accumulated
            await msg.edit(content=display)
            l_update_len = len(accumulated)
    if not accumulated:
        await msg.edit(content="I was unable to generate a response.")
        return
    
    if len(accumulated) <= 1900:
        await msg.edit(content=accumulated)
    else:
        await msg.edit(content=accumulated[:1900])
        for i in range(1900, len(accumulated), 1900):
            await ctx.send(accumulated[i:i+1900])




@AIFeature.command()
async def  test(ctx,*args):
    await ctx.send(" ".join(args))

@AIFeature.command(aliases=["tell"])
async def chat(ctx,*args):
    question = " ".join(args)
    if not question:
        return
    msg = await ctx.send("Thinking... 🧠")
    try:
        stream = await client.aio.models.generate_content_stream(model=model_name, contents=question, config=types.GenrateContentConfig(max_output_tokens=2000))
        await send_streamed(ctx, stream, msg)
#Stream included in chat command as well for ask command. 
#This integrations allow a faster response time and less waiting time.

    except Exception as exc:
        await msg.edit(content=f"Error: {exc}")

user_chats={}
@AIFeature.command()
async def ask(ctx, *, question):
    userID = ctx.author.id
    msg = await ctx.send("Thinking... 🧠")
    try:
        if userID not in user_chats:
            current_key = random.choice(keys)
            session_client = Client(api_key=current_key)
            user_chats[userID] = session_client.aio.chats.create(model=model_name)
# Stream response included in ask command.
        chatSession = user_chats[userID]
        stream = await chatSession.send_message_stream(question, config=types.GenerateContentConfig(max_output_tokens=2000))
        await send_streamed(ctx, stream, msg)

    except Exception as exc:
        await msg.edit(content=f"Error contacting server: {exc}")
  
#This line is extra is just to avoid using command prefix when messaging privately or DM.
@AIFeature.event
async def on_message(message):
    if message.author == AIFeature.user:
        return
    if not message.content.startswith("!"):
        if AIFeature.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            cleanContent = message.content.replace(f"<@{AIFeature.user.id}>", "").replace(f"<@!{AIFeature.user.id}>", "").strip()
            if cleanContent:
                ctx = await AIFeature.get_context(message)
                await ask(ctx, question=cleanContent)
    await AIFeature.process_commands(message)

    
    

AIFeature.run(getenv('TOKEN'))