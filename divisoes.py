import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

TOKEN = os.getenv('DISCORD_TOKEN2')

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Ativar intents para membros

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Estamos logados como {bot.user}')
    
    # IDs dos canais
    verificacao_channel_id = 1315844202856321134
    registro_channel_id = 1333549238671380570
    transfer_channel_id = 1333549260704321617

    # Apagar mensagens antigas e enviar as embeds respectivas para cada canal
    for channel_id in [verificacao_channel_id, registro_channel_id, transfer_channel_id]:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.purge()

    verificacao_channel = bot.get_channel(verificacao_channel_id)
    registro_channel = bot.get_channel(registro_channel_id)
    transfer_channel = bot.get_channel(transfer_channel_id)

    if verificacao_channel:
        embed = nextcord.Embed(
            title="Verificação",
            description="Clique no botão abaixo para verificar seu ID.",
            color=nextcord.Color.green()
        )
        embed.set_footer(text="Criado por - 𝓛𝓸𝓮𝓼")
        button = nextcord.ui.Button(label="VERIFICAÇÃO", style=nextcord.ButtonStyle.green)
        button.callback = bot.get_cog('Verificacao').button_callback
        view = nextcord.ui.View(timeout=None)
        view.add_item(button)
        await verificacao_channel.send(embed=embed, view=view)

    if registro_channel:
        embed = nextcord.Embed(
            title="Registro de Usuário",
            description="Clique no botão abaixo para iniciar o registro.",
            color=nextcord.Color.blue()
        )
        button = nextcord.ui.Button(label="Registrar", style=nextcord.ButtonStyle.green)
        button.callback = bot.get_cog('Registro').button_callback
        view = nextcord.ui.View(timeout=None)
        view.add_item(button)
        await registro_channel.send(embed=embed, view=view)

    if transfer_channel:
        embed = nextcord.Embed(
            title="Solicitação de Transferência",
            description="Selecione a divisão para a qual deseja ser transferido no dropdown abaixo.",
            color=nextcord.Color.blue()
        )
        select = nextcord.ui.Select(
            placeholder="Escolha sua nova Divisão",
            custom_id="transfer_select",
            options=[
                nextcord.SelectOption(label="CIGS", description="Centro de Instrução de Guerra na Selva", value=os.getenv('ROLE_CIGS')),
                nextcord.SelectOption(label="FAB", description="Força Áerea Brasileira", value=os.getenv('ROLE_FAB')),
                nextcord.SelectOption(label="CMDS", description="Batalhão dos Comandos", value=os.getenv('ROLE_CMDS')),
                nextcord.SelectOption(label="CIEX", description="Centro de Inteligência do Exército", value=os.getenv('ROLE_CIEX')),
                nextcord.SelectOption(label="BFE", description="Batalhão de Forças Especiais", value=os.getenv('ROLE_BFE')),
                nextcord.SelectOption(label="PE", description="Polícia do Exército", value=os.getenv('ROLE_PE')),
                nextcord.SelectOption(label="SPEED", description="Força Speed Tática", value=os.getenv('ROLE_SPEED')),
            ]
        )
        select.callback = bot.get_cog('Registro').transfer_callback
        view = nextcord.ui.View(timeout=None)
        view.add_item(select)
        await transfer_channel.send(embed=embed, view=view)

@bot.event
async def on_message(message):
    # Apagar o comando que foi feito com o prefixo e deixar somente a embed
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        await message.delete()
    else:
        await bot.process_commands(message)

# Carregar os cogs
bot.load_extension('setagem')
bot.load_extension('verificacao')
bot.load_extension('registro')

bot.run(TOKEN)