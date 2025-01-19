import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

TOKEN = os.getenv('DISCORD_TOKEN')

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Estamos logados como {bot.user}')

# Carregar o cog de ações
bot.load_extension('acao')

# Carregar o cog de aulas
bot.load_extension('aulas')

bot.run(TOKEN)