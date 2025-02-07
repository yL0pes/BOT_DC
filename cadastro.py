import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

TOKEN2 = os.getenv('DISCORD_TOKEN2')

intents2 = nextcord.Intents.default()
intents2.message_content = True
intents2.guilds = True
intents2.members = True  # Ativar intents para membros

bot2 = commands.Bot(command_prefix="!", intents=intents2)

@bot2.event
async def on_ready():
    print(f'Bot 2 logado como {bot2.user}')

if __name__ == "__main__":
    bot2.run(TOKEN2)
