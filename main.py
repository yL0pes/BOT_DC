from dotenv import load_dotenv
import os
import nextcord
from nextcord.ext import commands

from curso import CursoDropdownView

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

TOKEN = os.getenv('DISCORD_TOKEN')

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True  # Add this line to ensure guild-related events are enabled

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Estamos logados como {bot.user}')
    
    # Reenviar comandos nos canais específicos
    await resend_commands()

async def resend_commands():
    # IDs dos canais específicos
    curso_channel_id = 1306026729755906098  # Substitua pelo ID do canal de cursos
    acao_channel_id = 1331362298182500382  # Substitua pelo ID do canal de ações

    curso_channel = bot.get_channel(curso_channel_id)
    acao_channel = bot.get_channel(acao_channel_id)

    # Apagar mensagens anteriores nos canais específicos
    if curso_channel:
        await curso_channel.purge(limit=100)
        embed = nextcord.Embed(title="Escolha um curso", description=" - Novo BOT de solicitar aulas! Escolha um curso na lista abaixo e aguarde um Instrutor aceitar o seu Curso.", color=0xffff00)
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼 ")
        view = CursoDropdownView()
        await curso_channel.send(embed=embed, view=view)

    if acao_channel:
        await acao_channel.purge(limit=100)
        embed = nextcord.Embed(
            title="REGISTRO DE AÇÕES DO EXÉRCITO BRASILEIRO",
            description=" - Lembre-se de utilizar apenas números para informar a quantidade de membros e o horário da ação. Unidos pela missão, prontos para a vitória!",
            color=nextcord.Color.blue()
        )
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")
        button = nextcord.ui.Button(label="REGISTRAR AÇÃO", style=nextcord.ButtonStyle.primary)
        view = nextcord.ui.View(timeout=None)
        view.add_item(button)
        await acao_channel.send(embed=embed, view=view)

# Carregar os cogs
bot.load_extension('acao') # Adicione esta linha para carregar o acao.py
bot.load_extension('curso')
bot.load_extension('teste')  # Adicione esta linha para carregar o upamento.py

bot.run(TOKEN)