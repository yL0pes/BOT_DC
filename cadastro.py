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

DIVISION_ROLES = {
    "CIGS": 1337181664693981221,  # Substitua pelo ID do cargo de CIGS
    "FAB": 1337181664693981222,  # Substitua pelo ID do cargo de FAB
    "CMDS": 1337181664693981223,  # Substitua pelo ID do cargo de CMDS
    "CIEX": 1337181664693981224,  # Substitua pelo ID do cargo de CIEX
    "BFE": 1337181664693981225,  # Substitua pelo ID do cargo de BFE
    "PE": 1337181664693981226,  # Substitua pelo ID do cargo de PE
    "SPEED": 1337181664693981227  # Substitua pelo ID do cargo de SPEED
}

intents2 = nextcord.Intents.default()
intents2.message_content = True
intents2.guilds = True
intents2.members = True  # Ativar intents para membros

bot2 = commands.Bot(command_prefix="!", intents=intents2)

@bot2.event
async def on_ready():
    print(f'Bot 2 logado como {bot2.user}')
    await asyncio.sleep(10)  # Wait for 10 seconds to ensure the bot is fully ready
    await purge_channels(bot2)
    bot2.loop.create_task(schedule_embed_updates(bot2))

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
            await interaction.followup.send("Selecione sua divisão:", view=DivisionSelectView(user_id, user_name))
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

        self.add_item(nextcord.ui.Select(
            placeholder="Escolha sua Divisão",
            options=[
                nextcord.SelectOption(label="CIGS", description="Centro de Instrução de Guerra na Selva", value="CIGS"),
                nextcord.SelectOption(label="FAB", description="Força Áerea Brasileira", value="FAB"),
                nextcord.SelectOption(label="CMDS", description="Batalhão dos Comandos", value="CMDS"),
                nextcord.SelectOption(label="CIEX", description="Centro de Inteligência do Exército", value="CIEX"),
                nextcord.SelectOption(label="BFE", description="Batalhão de Forças Especiais", value="BFE"),
                nextcord.SelectOption(label="PE", description="Polícia do Exército", value="PE"),
                nextcord.SelectOption(label="SPEED", description="Força Speed Tática", value="SPEED")
            ],
            min_values=1,
            max_values=1
        ))

    @nextcord.ui.select()
    async def select_callback(self, select, interaction: nextcord.Interaction):
        division = select.values[0]

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
                description=f"Nome: {self.user_name}\nDivisão: {division}",
                color=nextcord.Color.blue()
            )
            embed.set_footer(text="Criado por - 𝓛𝓸𝓮𝓼")
            view = nextcord.ui.View(timeout=None)
            view.add_item(nextcord.ui.Button(label="ACEITAR", style=nextcord.ButtonStyle.green, custom_id=f"accept_{self.user_id}"))
            view.add_item(nextcord.ui.Button(label="NEGAR", style=nextcord.ButtonStyle.red, custom_id=f"deny_{self.user_id}"))
            await analysis_channel.send(embed=embed, view=view)

        await interaction.response.send_message("Divisão selecionada com sucesso! Seu registro foi enviado para análise.", ephemeral=True)

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

@bot2.command()
@commands.has_role(ADMIN_ROLE_ID)
async def list_ids(ctx):
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

@bot2.command()
@commands.has_role(ADMIN_ROLE_ID)
async def reset(ctx, member: nextcord.Member):
    db_connection = connect_db()
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM user_ids WHERE discord_id = %s", (member.id,))
    cursor.execute("DELETE FROM user_registrations WHERE discord_id = %s", (member.id,))
    db_connection.commit()
    cursor.close()
    db_connection.close()

    role = member.guild.get_role(VERIFIED_ROLE_ID)
    if role:
        await member.remove_roles(role)

    await ctx.send(f"Verificação e registro do usuário {member.mention} foram resetados.")

@bot2.command()
@commands.has_role(SUPER_ADMIN_ROLE_ID)
async def reset_all_ids(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Você tem certeza que deseja resetar todos os IDs? Responda com 'aceitar' ou 'negar'.")

    try:
        msg = await bot2.wait_for('message', check=check, timeout=30)
        if msg.content.lower() == 'aceitar':
            db_connection = connect_db()
            cursor = db_connection.cursor()
            cursor.execute("DELETE FROM user_ids")
            cursor.execute("DELETE FROM user_registrations")
            db_connection.commit()
            cursor.close()
            db_connection.close()
            await ctx.send("Todos os IDs foram resetados.")
        else:
            await ctx.send("Operação cancelada.")
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.")

if __name__ == "__main__":
    db_connection = connect_db()
    if db_connection.is_connected():
        print("Conectado ao banco de dados")
    else:
        print("Falha ao conectar ao banco de dados")
    
    bot2.run(TOKEN2)
