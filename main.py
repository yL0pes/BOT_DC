from dotenv import load_dotenv
import os
import nextcord
from nextcord.ext import commands
from multiprocessing import Process
import schedule
import time
import cmd

from carteira import FormView
from curso import CursoDropdownView

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

TOKEN1 = os.getenv('DISCORD_TOKEN')
TOKEN2 = os.getenv('DISCORD_TOKEN2')

intents1 = nextcord.Intents.default()
intents1.message_content = True
intents1.guilds = True

intents2 = nextcord.Intents.default()
intents2.message_content = True
intents2.guilds = True
intents2.members = True  # Ativar intents para membros no bot 2

async def resend_commands(bot):
    # IDs dos canais específicos
    curso_channel_id = 1333608749121929218  # Substitua pelo ID do canal de cursos
    acao_channel_id = 1260329390743621683  # Substitua pelo ID do canal de ações
    form_channel_id = 1332103347657904139  # Substitua pelo ID do canal de formulários

    curso_channel = bot.get_channel(curso_channel_id)
    acao_channel = bot.get_channel(acao_channel_id)
    form_channel = bot.get_channel(form_channel_id)

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

    if form_channel:
        await form_channel.purge(limit=100)
        embed = nextcord.Embed(
            title="Escolha a carteira que quer enviar",
            description="Escolha uma das opções abaixo para abrir o formulário correspondente.",
            color=0x00ff00
        )
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")
        view = FormView()
        await form_channel.send(embed=embed, view=view)

async def resend_commands_divisoes(bot):
    # IDs dos canais específicos
    form_channel_id = 1332103347657904139  # Substitua pelo ID do canal de formulários

    form_channel = bot.get_channel(form_channel_id)

    if form_channel:
        await form_channel.purge(limit=100)
        embed = nextcord.Embed(
            title="Escolha a carteira que quer enviar",
            description="Escolha uma das opções abaixo para abrir o formulário correspondente.",
            color=0x00ff00
        )
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")
        view = FormView()
        await form_channel.send(embed=embed, view=view)

def run_bot1():
    bot1 = commands.Bot(command_prefix="!", intents=intents1)

    @bot1.event
    async def on_ready():
        print(f'Bot 1 logado como {bot1.user}')
        await resend_commands(bot1)

    # Carregar os cogs
    bot1.load_extension('acao')
    bot1.load_extension('curso')
    bot1.load_extension('carteira')
    bot1.load_extension('anunciar')

    bot1.run(TOKEN1)

def run_bot2():
    bot2 = commands.Bot(command_prefix="!", intents=intents2)

    @bot2.event
    async def on_ready():
        print(f'Bot 2 logado como {bot2.user}')
        await resend_commands_divisoes(bot2)

        # IDs dos canais
        verificacao_channel_id = 1315844202856321134
        registro_channel_id = 1333549238671380570
        transfer_channel_id = 1333549260704321617
        form_channel_id = 1332103347657904139
        cursos_channel_id = 1333608749121929218

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
    bot2.load_extension('anunciar')

    bot2.run(TOKEN2)

def schedule_restarts():
    schedule.every(5).hours.do(restart_bots)

def restart_bots():
    os._exit(1)

class BotConsole(cmd.Cmd):
    def __init__(self, bot1, bot2):
        super().__init__()
        self.bot1 = bot1
        self.bot2 = bot2
    prompt = '> '

    def do_restart(self, arg):
        """Reinicia os bots"""
        print("Reiniciando os bots...")
        restart_bots()

    def do_status(self, arg):
        """Mostra o status dos bots"""
        print("Bot 1 está rodando" if p1.is_alive() else "Bot 1 está parado")
        print("Bot 2 está rodando" if p2.is_alive() else "Bot 2 está parado")

    def do_load_cog(self, cog_name):
        """Carrega um cog específico"""
        self.bot1.load_extension(cog_name)
        self.bot2.load_extension(cog_name)
        print(f"Cog {cog_name} carregado")

    def do_unload_cog(self, cog_name):
        """Descarrega um cog específico"""
        self.bot1.unload_extension(cog_name)
        self.bot2.unload_extension(cog_name)
        print(f"Cog {cog_name} descarregado")

    def do_reload_cog(self, cog_name):
        """Recarrega um cog específico"""
        self.bot1.reload_extension(cog_name)
        self.bot2.reload_extension(cog_name)
        print(f"Cog {cog_name} recarregado")

    def do_send_message(self, args):
        """Envia uma mensagem para um canal específico"""
        channel_id, message = args.split(' ', 1)
        channel = self.bot1.get_channel(int(channel_id)) or self.bot2.get_channel(int(channel_id))
        if channel:
            channel.send(message)
            print(f"Mensagem enviada para o canal {channel_id}")
        else:
            print(f"Canal {channel_id} não encontrado")

    def do_purge_channel(self, channel_id):
        """Apaga todas as mensagens de um canal específico"""
        channel = self.bot1.get_channel(int(channel_id)) or self.bot2.get_channel(int(channel_id))
        if channel:
            channel.purge()
            print(f"Mensagens apagadas do canal {channel_id}")
        else:
            print(f"Canal {channel_id} não encontrado")

    def do_list_cogs(self, arg):
        """Lista todos os cogs carregados"""
        print("Cogs carregados no Bot 1:")
        for cog in self.bot1.cogs:
            print(cog)
        print("Cogs carregados no Bot 2:")
        for cog in self.bot2.cogs:
            print(cog)

    def do_shutdown(self, arg):
        """Desliga os bots"""
        print("Desligando os bots...")
        self.bot1.close()
        self.bot2.close()

    def do_schedule_restart(self, hours):
        """Agenda uma reinicialização dos bots em um intervalo de horas específico"""
        schedule.every(int(hours)).hours.do(restart_bots)
        print(f"Reinicialização agendada a cada {hours} horas")

    def do_cancel_scheduled_restarts(self, arg):
        """Cancela todas as reinicializações agendadas"""
        schedule.clear()
        print("Reinicializações agendadas canceladas")

    def do_list_channels(self, arg):
        """Lista todos os canais do servidor"""
        print("Canais do servidor:")
        for guild in self.bot1.guilds + self.bot2.guilds:
            for channel in guild.channels:
                print(f"{channel.id} - {channel.name}")

    def do_list_roles(self, arg):
        """Lista todos os cargos do servidor"""
        print("Cargos do servidor:")
        for guild in self.bot1.guilds + self.bot2.guilds:
            for role in guild.roles:
                print(f"{role.id} - {role.name}")

    def do_add_role(self, args):
        """Adiciona um cargo a um usuário específico"""
        user_id, role_id = args.split()
        user = self.bot1.get_user(int(user_id)) or self.bot2.get_user(int(user_id))
        role = self.bot1.get_role(int(role_id)) or self.bot2.get_role(int(role_id))
        if user and role:
            user.add_roles(role)
            print(f"Cargo {role.name} adicionado ao usuário {user.name}")
        else:
            print("Usuário ou cargo não encontrado")

    def do_remove_role(self, args):
        """Remove um cargo de um usuário específico"""
        user_id, role_id = args.split()
        user = self.bot1.get_user(int(user_id)) or self.bot2.get_user(int(user_id))
        role = self.bot1.get_role(int(role_id)) or self.bot2.get_role(int(role_id))
        if user and role:
            user.remove_roles(role)
            print(f"Cargo {role.name} removido do usuário {user.name}")
        else:
            print("Usuário ou cargo não encontrado")

    def do_kick_user(self, user_id):
        """Expulsa um usuário específico do servidor"""
        user = self.bot1.get_user(int(user_id)) or self.bot2.get_user(int(user_id))
        if user:
            user.kick()
            print(f"Usuário {user.name} expulso do servidor")
        else:
            print("Usuário não encontrado")

    def do_ban_user(self, user_id):
        """Bane um usuário específico do servidor"""
        user = self.bot1.get_user(int(user_id)) or self.bot2.get_user(int(user_id))
        if user:
            user.ban()
            print(f"Usuário {user.name} banido do servidor")
        else:
            print("Usuário não encontrado")

    def do_unban_user(self, user_id):
        """Desbane um usuário específico do servidor"""
        user = self.bot1.get_user(int(user_id)) or self.bot2.get_user(int(user_id))
        if user:
            user.unban()
            print(f"Usuário {user.name} desbanido do servidor")
        else:
            print("Usuário não encontrado")

    def do_list_banned_users(self, arg):
        """Lista todos os usuários banidos do servidor"""
        print("Usuários banidos do servidor:")
        for guild in self.bot1.guilds + self.bot2.guilds:
            for ban_entry in guild.bans():
                print(f"{ban_entry.user.id} - {ban_entry.user.name}")

    def do_help(self, arg):
        """Mostra a lista de comandos disponíveis"""
        print("Comandos disponíveis:")
        for command in self.get_names():
            if command.startswith('do_'):
                print(command[3:])

if __name__ == "__main__":
    p1 = Process(target=run_bot1)
    p2 = Process(target=run_bot2)
    
    p1.start()
    p2.start()
    
    bot1 = commands.Bot(command_prefix="!", intents=intents1)
    bot2 = commands.Bot(command_prefix="!", intents=intents2)
    console = BotConsole(bot1, bot2)
    
    schedule_restarts()
    
    console.cmdloop()
    
    while True:
        schedule.run_pending()
        time.sleep(1)