from dotenv import load_dotenv
import os
import nextcord
from nextcord.ext import commands

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

TOKEN = os.getenv('DISCORD_TOKEN')

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Estamos logados como {bot.user}')

# Carregar os cogs
bot.load_extension('acao')
bot.load_extension('curso')

bot.run(TOKEN)