import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

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

async def update_embed(bot, channel_id, title, description, color):
    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"Channel with ID {channel_id} not found.")
        return

    embed = nextcord.Embed(
        title=title,
        description=description,
        color=color
    )

    async for message in channel.history(limit=10):
        if message.author == bot.user and message.embeds:
            await message.delete()

    await channel.send(embed=embed)

async def schedule_embed_updates(bot):
    while True:
        await update_embed(bot, 1337181665545420826, "Verificação", "Clique no botão abaixo para verificar seu ID.", nextcord.Color.green())
        await update_embed(bot, 1337181666040483880, "Registro de Usuário", "Clique no botão abaixo para iniciar o registro.", nextcord.Color.blue())
        await update_embed(bot, 1337181666463977530, "Solicitação de Transferência", "Selecione a divisão para a qual deseja ser transferido no dropdown abaixo.", nextcord.Color.blue())
        await asyncio.sleep(3600)  # 1 hour

if __name__ == "__main__":
    bot2.run(TOKEN2)
