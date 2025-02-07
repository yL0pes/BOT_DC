import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import mysql.connector

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

TOKEN2 = os.getenv('DISCORD_TOKEN2')

DB_HOST = '172.93.104.61'
DB_USER = 'u661_rRiE9itGnx'
DB_PASSWORD = 'BgxrDebZCN0Uy!MBjd^1J!Wu'
DB_NAME = 's661_cadastro_divisao'
VERIFIED_ROLE_ID = 1337181664106778675  # Substitua pelo ID do cargo de verificado
ADMIN_ROLE_ID = 1337181664693981217  # Substitua pelo ID do cargo de administrador para !reset e !list_ids
SUPER_ADMIN_ROLE_ID = 1337181664693981220  # Substitua pelo ID do cargo de super administrador para !reset_all_ids
ANALYSIS_CHANNEL_ID = 1337181666040483881  # Substitua pelo ID do canal de análise
INSTRUCTOR_ROLE_ID = 1337181664190795808  # ID do cargo de instrutor
MEMBER_ROLE_ID = 1337181664190795807  # ID do cargo padrão "Membro"
LOG_CHANNEL_ID = 1337181665545420827  # ID do canal de logs

DIVISION_ROLES = {
    "CIGS": 1337181664656363597,  # Substitua pelo ID do cargo de CIGS
    "FAB": 1337181664656363596,  # Substitua pelo ID do cargo de FAB
    "CMDS": 1337181664656363595,  # Substitua pelo ID do cargo de CMDS
    "CIEX": 1337181664656363594,  # Substitua pelo ID do cargo de CIEX
    "BFE": 1337181664656363593,  # Substitua pelo ID do cargo de BFE
    "PE": 1337181664656363592,  # Substitua pelo ID do cargo de PE
    "SPEED": 1337181664656363591  # Substitua pelo ID do cargo de SPEED
}

DIVISION_SPECIFIC_ROLES = {
    "CIGS": {
        "ALUNO": 1337181664589381705,
        "SOLDADO": 1337181664589381706,
        "ELITE": 1337181664589381707,
        "INSTRUTOR": 1337181664589381708,
        "SUPERVISOR": 1337181664589381709,
        "SUPERVISOR-GERAL": 1337181664589381710
    },
    "FAB": {
        "PILOTO": 1337181664563957837,
        "PILOTO ELITE": 1337181664563957838,
        "INSTRUTOR": 1337181664563957839,
        "SUPERVISOR": 1337181664563957840,
        "SUPERVISOR-GERAL": 1337181664563957841
    },
    "CMDS": {
        "SOLDADO": 1337181664467619977,
        "ELITE": 1337181664467619978,
        "INSTRUTOR": 1337181664467619979,
        "SUPERVISOR": 1337181664467619980,
        "SUPERVISOR-GERAL": 1337181664563957833
    },
    "CIEX": {
        "INVESTIGADOR": 1337181664375472246,
        "INSTRUTOR": 1337181664375472247,
        "INVESTIGADOR GERAL": 1337181664467619971,
        "SUPERVISOR": 1337181664467619972,
        "SUPERVISOR-GERAL": 1337181664467619973
    },
    "BFE": {
        "ESTAGIARIO": 1337181664266162250,
        "SOLDADO": 1337181664266162251,
        "ELITE": 1337181664266162252,
        "INSTRUTOR": 1337181664266162253,
        "SUPERVISOR": 1337181664266162254,
        "SUPERVISOR-GERAL": 1337181664266162255
    },
    "PE": {
        "SOLDADO": 1337181664375472238,
        "ELITE": 1337181664375472239,
        "INSTRUTOR": 1337181664375472240,
        "SUPERVISOR": 1337181664375472241,
        "SUPERVISOR-GERAL": 1337181664375472242
    },
    "SPEED": {
        "SOLDADO": 1337181664190795810,
        "ELITE": 1337181664190795811,
        "INSTRUTOR": 1337181664190795812,
        "SUPERVISOR": 1337181664190795813,
        "SUPERVISOR-GERAL": 1337181664190795814
    }
}

intents2 = nextcord.Intents.default()
intents2.message_content = True
intents2.guilds = True
intents2.members = True  # Ativar intents para membros

bot2 = commands.Bot(command_prefix="!", intents=intents2)

class CadastroCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot 2 logado como {self.bot.user}')
        await asyncio.sleep(10)  # Wait for 10 segundos to ensure the bot is fully ready
        await purge_channels(self.bot)
        self.bot.loop.create_task(schedule_embed_updates(self.bot))

    @commands.command()
    @commands.has_role(ADMIN_ROLE_ID)
    async def list_ids(self, ctx):
        db_connection = connect_db()
        cursor = db_connection.cursor()
        cursor.execute("SELECT discord_id, user_id FROM user_ids")
        rows = cursor.fetchall()
        cursor.close()
        db_connection.close()

        if rows:
            response = "IDs salvos no banco de dados:\n"
            for row in rows:
                response += f"Discord ID: {row[0]}, User ID: {row[1]}\n"
        else:
            response = "Nenhum ID salvo no banco de dados."

        await ctx.send(response)

    @commands.command()
    @commands.has_role(ADMIN_ROLE_ID)
    async def reset(self, ctx, member: nextcord.Member):
        db_connection = connect_db()
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM user_ids WHERE discord_id = %s", (member.id,))
        cursor.execute("DELETE FROM user_registrations WHERE discord_id = %s", (member.id,))
        db_connection.commit()
        cursor.close()
        db_connection.close()

        roles_to_remove = [VERIFIED_ROLE_ID] + list(DIVISION_ROLES.values()) + [role_id for division in DIVISION_SPECIFIC_ROLES.values() for role_id in division.values()]
        roles = [member.guild.get_role(role_id) for role_id in roles_to_remove if member.guild.get_role(role_id)]
        await member.remove_roles(*roles)

        # Voltar o apelido original do usuário
        await member.edit(nick=None)

        await ctx.send(f"Verificação e registro do usuário {member.mention} foram resetados.")

    @commands.command()
    @commands.has_role(SUPER_ADMIN_ROLE_ID)
    async def reset_all_ids(self, ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("Você tem certeza que deseja resetar todos os IDs? Responda com 'aceitar' ou 'negar'.")

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
            if msg.content.lower() == 'aceitar':
                db_connection = connect_db()
                cursor = db_connection.cursor()
                cursor.execute("DELETE FROM user_ids")
                cursor.execute("DELETE FROM user_registrations")
                db_connection.commit()
                cursor.close()
                db_connection.close()

                guild = ctx.guild
                roles_to_remove = [VERIFIED_ROLE_ID] + list(DIVISION_ROLES.values()) + [role_id for division in DIVISION_SPECIFIC_ROLES.values() for role_id in division.values()]
                roles = [guild.get_role(role_id) for role_id in roles_to_remove if guild.get_role(role_id)]
                for role in roles:
                    for member in role.members:
                        await member.remove_roles(role)
                        # Voltar o apelido original do usuário
                        await member.edit(nick=None)

                await ctx.send("Todos os IDs foram resetados e os cargos foram removidos de todos os usuários.")
            else:
                await ctx.send("Operação cancelada.")
        except asyncio.TimeoutError:
            await ctx.send("Tempo esgotado. Operação cancelada.")

async def purge_channels(bot):
    channel_ids = [1337181665545420826, 1337181666040483880, 1337181666463977530]
    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.purge()

async def update_embed(bot, channel_id, title, description, color, tag, button=None):
    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"Channel with ID {channel_id} not found.")
        return

    embed = nextcord.Embed(
        title=title,
        description=description,
        color=color
    )
    embed.set_footer(text=tag)

    async for message in channel.history(limit=10):
        if message.author == bot.user and message.embeds and message.embeds[0].footer.text == tag:
            await message.delete()

    if button:
        view = nextcord.ui.View(timeout=None)
        view.add_item(button)
        await channel.send(embed=embed, view=view)
    else:
        await channel.send(embed=embed)

class VerificationModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Verificação de ID",
            timeout=None
        )
        self.id_input = nextcord.ui.TextInput(
            label="Digite seu ID",
            placeholder="ID",
            required=True
        )
        self.add_item(self.id_input)

    async def callback(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        user_input = self.id_input.value

        db_connection = connect_db()
        cursor = db_connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS user_ids (discord_id BIGINT PRIMARY KEY, user_id VARCHAR(255))")
        cursor.execute("SELECT * FROM user_ids WHERE discord_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            await interaction.response.send_message("Você já está verificado! Agora, faça o seu Registro.", ephemeral=True)
        else:
            cursor.execute("INSERT INTO user_ids (discord_id, user_id) VALUES (%s, %s)", (user_id, user_input))
            db_connection.commit()
            role = interaction.guild.get_role(VERIFIED_ROLE_ID)
            if role:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"ID {user_input} salvo com sucesso e cargo atribuído!", ephemeral=True)
            else:
                await interaction.response.send_message(f"ID {user_input} salvo com sucesso, mas o cargo não foi encontrado.", ephemeral=True)

        cursor.close()
        db_connection.close()

class RegistrationModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Registro de Usuário",
            timeout=None
        )
        self.name_input = nextcord.ui.TextInput(
            label="Digite seu nome",
            placeholder="Nome",
            required=True
        )
        self.add_item(self.name_input)

    async def callback(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        user_name = self.name_input.value

        db_connection = connect_db()
        cursor = db_connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS user_registrations (discord_id BIGINT PRIMARY KEY, user_name VARCHAR(255), division VARCHAR(255))")
        try:
            cursor.execute("INSERT INTO user_registrations (discord_id, user_name) VALUES (%s, %s)", (user_id, user_name))
            db_connection.commit()
            await interaction.response.send_message("Nome salvo com sucesso! Agora, selecione sua divisão.", ephemeral=True)
            await interaction.followup.send(content="Selecione sua divisão:", view=DivisionSelectView(user_id, user_name), ephemeral=True)
        except mysql.connector.errors.IntegrityError:
            await interaction.response.send_message("Você já está registrado!", ephemeral=True)
        finally:
            cursor.close()
            db_connection.close()

class DivisionSelectView(nextcord.ui.View):
    def __init__(self, user_id, user_name):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.user_name = user_name

        self.select = nextcord.ui.Select(
            placeholder="Escolha sua Divisão",
            options=[
                nextcord.SelectOption(label="CIGS", description="Centro de Instrução de Guerra na Selva", value="CIGS"),
                nextcord.SelectOption(label="FAB", description="Força Aérea Brasileira", value="FAB"),
                nextcord.SelectOption(label="CMDS", description="Batalhão dos Comandos", value="CMDS"),
                nextcord.SelectOption(label="CIEX", description="Centro de Inteligência do Exército", value="CIEX"),
                nextcord.SelectOption(label="BFE", description="Batalhão de Forças Especiais", value="BFE"),
                nextcord.SelectOption(label="PE", description="Polícia do Exército", value="PE"),
                nextcord.SelectOption(label="SPEED", description="Força Speed Tática", value="SPEED")
            ],
            min_values=1,
            max_values=1
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: nextcord.Interaction):
        division = self.select.values[0]

        db_connection = connect_db()
        cursor = db_connection.cursor()
        cursor.execute("UPDATE user_registrations SET division = %s WHERE discord_id = %s", (division, self.user_id))
        db_connection.commit()
        cursor.close()
        db_connection.close()

        role_id = DIVISION_ROLES.get(division)
        role = interaction.guild.get_role(role_id)
        if role:
            await interaction.user.add_roles(role)

        analysis_channel = interaction.guild.get_channel(ANALYSIS_CHANNEL_ID)
        if analysis_channel:
            embed = nextcord.Embed(
                title="Novo Registro de Usuário",
                description=f"👮 Nome: {self.user_name}\n🌐 Divisão: {division}\n🪪 ID: {self.user_id}",
                color=nextcord.Color.blue()
            )
            embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")
            view = nextcord.ui.View(timeout=None)
            accept_button = AcceptButton(self.user_id, self.user_name, division)
            deny_button = DenyButton(self.user_id, self.user_name, embed)
            view.add_item(accept_button)
            view.add_item(deny_button)
            await analysis_channel.send(embed=embed, view=view)

        await interaction.response.send_message("Divisão selecionada com sucesso! Seu registro foi enviado para análise.", ephemeral=True)

class AcceptDropdown(nextcord.ui.Select):
    def __init__(self, user_id, user_name, division, accept_button, deny_button):
        self.user_id = user_id
        self.user_name = user_name
        self.division = division
        self.accept_button = accept_button
        self.deny_button = deny_button

        options = [
            nextcord.SelectOption(label=role_name, value=role_name)
            for role_name in DIVISION_SPECIFIC_ROLES[self.division].keys()
        ]

        super().__init__(
            placeholder="Escolha o cargo específico",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: nextcord.Interaction):
        specific_role = self.values[0]
        specific_role_id = DIVISION_SPECIFIC_ROLES[self.division][specific_role]
        user = interaction.guild.get_member(self.user_id)
        if user:
            division_role_id = DIVISION_ROLES[self.division]
            division_role = interaction.guild.get_role(division_role_id)
            specific_role_obj = interaction.guild.get_role(specific_role_id)
            member_role = interaction.guild.get_role(MEMBER_ROLE_ID)
            if division_role and specific_role_obj and member_role:
                await user.add_roles(division_role, specific_role_obj, member_role)
                db_connection = connect_db()
                cursor = db_connection.cursor()
                cursor.execute("SELECT user_id FROM user_ids WHERE discord_id = %s", (self.user_id,))
                result = cursor.fetchone()
                cursor.close()
                db_connection.close()
                user_id_from_db = result[0] if result else self.user_id
                new_nickname = f"[{specific_role[:3]}-{self.division}] {self.user_name} | {user_id_from_db}"
                if len(new_nickname) > 32:
                    new_nickname = new_nickname[:32]
                await user.edit(nick=new_nickname)
                self.accept_button.disabled = True
                self.accept_button.label = "ACEITO!"
                self.deny_button.disabled = True
                new_view = nextcord.ui.View(timeout=None)
                new_view.add_item(self.accept_button)
                new_view.add_item(self.deny_button)
                await interaction.response.edit_message(view=new_view)
                
                # Enviar log no canal de logs
                log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    log_embed = nextcord.Embed(
                        title="Novo membro verificado",
                        description=f"**Apelido:** {new_nickname}\n**ID:** {self.user_id}\n**Divisão:** {self.division}\n**ACEITO POR:** {interaction.user.mention}",
                        color=nextcord.Color.green()
                    )
                    await log_channel.send(embed=log_embed)
                
                # Excluir mensagens no canal de análise
                analysis_channel = interaction.guild.get_channel(ANALYSIS_CHANNEL_ID)
                if analysis_channel:
                    async for message in analysis_channel.history(limit=100):
                        if message.author == bot2.user:
                            await message.delete()

                await interaction.followup.send("Usuário setado com sucesso.", ephemeral=True)
            else:
                await interaction.response.send_message("Cargo ou divisão não encontrado.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)

class AcceptButton(nextcord.ui.Button):
    def __init__(self, user_id, user_name, division):
        super().__init__(label="ACEITAR", style=nextcord.ButtonStyle.green, custom_id=f"accept_{user_id}")
        self.user_id = user_id
        self.user_name = user_name
        self.division = division

    async def callback(self, interaction: nextcord.Interaction):
        if INSTRUCTOR_ROLE_ID in [role.id for role in interaction.user.roles]:
            view = nextcord.ui.View(timeout=None)
            dropdown = AcceptDropdown(self.user_id, self.user_name, self.division, self, interaction.message.components[0].children[1])
            view.add_item(dropdown)
            await interaction.response.send_message("Selecione o cargo específico:", view=view, ephemeral=True)
        else:
            await interaction.response.send_message("Você não tem permissão para aceitar registros.", ephemeral=True)

class DenyReasonModal(nextcord.ui.Modal):
    def __init__(self, user_id, user_name, message, accept_button, deny_button):
        super().__init__(title="Motivo da Negação", timeout=None)
        self.user_id = user_id
        self.user_name = user_name
        self.message = message
        self.accept_button = accept_button
        self.deny_button = deny_button
        self.reason_input = nextcord.ui.TextInput(
            label="Motivo",
            placeholder="Digite o motivo da negação",
            required=True,
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.reason_input)

    async def callback(self, interaction: nextcord.Interaction):
        reason = self.reason_input.value
        user = interaction.guild.get_member(self.user_id)
        if user:
            try:
                await user.send(f"Seu pedido de setagem foi negado pelo seguinte motivo: {reason}")
                await self.message.delete()
                self.accept_button.disabled = True
                self.deny_button.disabled = True
                new_view = nextcord.ui.View(timeout=None)
                new_view.add_item(self.accept_button)
                new_view.add_item(self.deny_button)
                await interaction.response.edit_message(view=new_view)
                
                # Excluir mensagens no canal de análise
                analysis_channel = interaction.guild.get_channel(ANALYSIS_CHANNEL_ID)
                if analysis_channel:
                    async for message in analysis_channel.history(limit=100):
                        if message.author == bot2.user:
                            await message.delete()

                await interaction.followup.send("Motivo enviado com sucesso e embed excluída.", ephemeral=True)
            except nextcord.Forbidden:
                await interaction.response.send_message("Não foi possível enviar a mensagem privada ao usuário.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)

class DenyButton(nextcord.ui.Button):
    def __init__(self, user_id, user_name, message):
        super().__init__(label="NEGAR", style=nextcord.ButtonStyle.red, custom_id=f"deny_{user_id}")
        self.user_id = user_id
        self.user_name = user_name
        self.message = message

    async def callback(self, interaction: nextcord.Interaction):
        if INSTRUCTOR_ROLE_ID in [role.id for role in interaction.user.roles]:
            modal = DenyReasonModal(self.user_id, self.user_name, self.message, interaction.message.components[0].children[0], self)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Você não tem permissão para negar registros.", ephemeral=True)

class RegistrationButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="Iniciar Registro 🪪", style=nextcord.ButtonStyle.green, custom_id="register_button")

    async def callback(self, interaction: nextcord.Interaction):
        modal = RegistrationModal()
        await interaction.response.send_modal(modal)

class VerificationButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="VERIFICAR ✅", style=nextcord.ButtonStyle.green, custom_id="verify_button")

    async def callback(self, interaction: nextcord.Interaction):
        modal = VerificationModal()
        await interaction.response.send_modal(modal)

async def schedule_embed_updates(bot):
    while True:
        verify_button = VerificationButton()
        register_button = RegistrationButton()
        await update_embed(bot, 1337181665545420826, "Verificação", "Clique no botão abaixo para verificar seu ID.", nextcord.Color.green(), "verificacao", verify_button)
        await update_embed(bot, 1337181666040483880, "Registro de Usuário", "Clique no botão abaixo para iniciar o registro.", nextcord.Color.blue(), "registro", register_button)
        await update_embed(bot, 1337181666463977530, "Solicitação de Transferência", "Selecione a divisão para a qual deseja ser transferido no dropdown abaixo.", nextcord.Color.blue(), "transferencia")
        await asyncio.sleep(3600)  # 1 hour

def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def setup(bot):
    bot.add_cog(CadastroCog(bot))

if __name__ == "__main__":
    db_connection = connect_db()
    if db_connection.is_connected():
        print("Conectado ao banco de dados")
    else:
        print("Falha ao conectar ao banco de dados")
    
    bot2.run(TOKEN2)
