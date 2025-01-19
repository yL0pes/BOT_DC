import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Estamos logados como {bot.user}')

# Carregar o cog de ações
bot.load_extension('acao')

bot.run(TOKEN)