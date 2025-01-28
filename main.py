from dotenv import load_dotenv
import os
import nextcord
from nextcord.ext import commands
from multiprocessing import Process

from curso import CursoDropdownView

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

TOKEN1 = os.getenv('DISCORD_TOKEN')
TOKEN2 = os.getenv('DISCORD_TOKEN2')

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True  # Add this line to ensure guild-related events are enabled

def run_bot1():
    bot1 = commands.Bot(command_prefix="!", intents=intents)

    @bot1.event
    async def on_ready():
        print(f'Bot 1 logado como {bot1.user}')
        await resend_commands(bot1)

    async def resend_commands(bot):
        # IDs dos canais específicos
        curso_channel_id = 1333608749121929218  # Substitua pelo ID do canal de cursos
        acao_channel_id = 1260329390743621683  # Substitua pelo ID do canal de ações

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
    bot1.load_extension('acao')  # Adicione esta linha para carregar o acao.py
    bot1.load_extension('curso')
    bot1.load_extension('carteira')  # Adicione esta linha para carregar o upamento.py
    bot1.load_extension('anunciar')  # Adicione esta linha para carregar o anunciar.py

    bot1.run(TOKEN1)

def run_bot2():
    bot2 = commands.Bot(command_prefix="!", intents=intents)

    @bot2.event
    async def on_ready():
        print(f'Bot 2 logado como {bot2.user}')
        # IDs dos canais
        verificacao_channel_id = 1315844202856321134
        registro_channel_id = 1333549238671380570
        transfer_channel_id = 1333549260704321617
        form_channel_id = 1332103347657904139  # Substitua pelo ID do canal de formulários
        cursos_channel_id = 1333608749121929218  # Substitua pelo ID do canal de cursos

        # Apagar mensagens antigas e enviar as embeds respectivas para cada canal
        for channel_id in [verificacao_channel_id, registro_channel_id, transfer_channel_id, form_channel_id, cursos_channel_id]:
            channel = bot2.get_channel(channel_id)
            if channel:
                await channel.purge()

        verificacao_channel = bot2.get_channel(verificacao_channel_id)
        registro_channel = bot2.get_channel(registro_channel_id)
        transfer_channel = bot2.get_channel(transfer_channel_id)
        form_channel = bot2.get_channel(form_channel_id)
        cursos_channel = bot2.get_channel(cursos_channel_id)

        if verificacao_channel:
            embed = nextcord.Embed(
                title="Verificação",
                description="Clique no botão abaixo para verificar seu ID.",
                color=nextcord.Color.green()
            )
            embed.set_footer(text="Criado por - 𝓛𝓸𝓮𝓼")
            button = nextcord.ui.Button(label="VERIFICAÇÃO", style=nextcord.ButtonStyle.green)
            button.callback = bot2.get_cog('Verificacao').button_callback
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
            button.callback = bot2.get_cog('Registro').button_callback
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
            select.callback = bot2.get_cog('Registro').transfer_callback
            view = nextcord.ui.View(timeout=None)
            view.add_item(select)
            await transfer_channel.send(embed=embed, view=view)

        if form_channel:
            embed = nextcord.Embed(
                title="Formulários",
                description="Clique no botão abaixo para abrir o formulário.",
                color=nextcord.Color.blue()
            )
            button = nextcord.ui.Button(label="Abrir Formulário", style=nextcord.ButtonStyle.green)
            button.callback = bot2.get_cog('Teste').form_callback
            view = nextcord.ui.View(timeout=None)
            view.add_item(button)
            await form_channel.send(embed=embed, view=view)

        if cursos_channel:
            embed = nextcord.Embed(
                title="Cursos",
                description="Clique no botão abaixo para escolher um curso.",
                color=nextcord.Color.blue()
            )
            button = nextcord.ui.Button(label="Escolher Curso", style=nextcord.ButtonStyle.green)
            button.callback = bot2.get_cog('Curso').cursos_callback
            view = nextcord.ui.View(timeout=None)
            view.add_item(button)
            await cursos_channel.send(embed=embed, view=view)

    # Carregar os cogs
    bot2.load_extension('setagem')
    bot2.load_extension('verificacao')
    bot2.load_extension('registro')
    bot2.load_extension('curso')
    bot2.load_extension('carteira')
    bot2.load_extension('anunciar')  # Adicione esta linha para carregar o anunciar.py

    bot2.run(TOKEN2)

if __name__ == "__main__":
    p1 = Process(target=run_bot1)
    p2 = Process(target=run_bot2)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()