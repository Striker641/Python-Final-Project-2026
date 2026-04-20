import discord
from discord.ext import commands
import google.generativeai as genai
import keys

genai.configure(api_key=keys.GEN_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
@bot.command()
async def  ask(ctx,*args):
    await ctx.send(" ".join(args))

@bot.command()
async def chat(ctx,*args):
    question = " ".join(args)
    response = model.generate_content(question)
    await ctx.send(response.text)

@bot.command()
async def ask(ctx, *, question):
    response = model.generate_content(question)
    await ctx.send("Thinking...")
    await ctx.send(response.text)
    
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

bot.run(keys.TOKEN)