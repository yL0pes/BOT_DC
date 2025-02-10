import mysql
import nextcord
from nextcord.ext import commands
import asyncio

from config import INSTRUCTOR_ROLE_ID, DIVISION_ROLES, ROLE_ABBREVIATIONS, DIVISION_SPECIFIC_ROLES

class TransferenciaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_transfer_embed(self):
        print("TransferenciaCog: Atualizando embed de transferência.")
        channel_id = 1337181666463977530  # ID do canal de solicitação de transferência
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"Channel with ID {channel_id} not found.")
            return

        embed = nextcord.Embed(
            title="Solicitação de Transferência",
            description="Selecione a divisão para a qual deseja ser transferido no dropdown abaixo.",
            color=nextcord.Color.blue()
        )
        embed.set_footer(text="transferencia")

        async for message in channel.history(limit=10):
            if message.author == self.bot.user and message.embeds and message.embeds[0].footer.text == "transferencia":
                await message.delete()

        view = TransferDropdownView()
        await channel.send(embed=embed, view=view)

class TransferDropdownView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TransferDropdown())

class TransferDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="CIGS", description="Centro de Instrução de Guerra na Selva", value="CIGS"),
            nextcord.SelectOption(label="FAB", description="Força Aérea Brasileira", value="FAB"),
            nextcord.SelectOption(label="CMDS", description="Batalhão dos Comandos", value="CMDS"),
            nextcord.SelectOption(label="CIEX", description="Centro de Inteligência do Exército", value="CIEX"),
            nextcord.SelectOption(label="BFE", description="Batalhão de Forças Especiais", value="BFE"),
            nextcord.SelectOption(label="PE", description="Polícia do Exército", value="PE"),
            nextcord.SelectOption(label="SPEED", description="Força Speed Tática", value="SPEED")
        ]
        super().__init__(placeholder="Escolha sua nova divisão", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: nextcord.Interaction):
        division = self.values[0]
        user_id = interaction.user.id
        user_name = interaction.user.display_name

        db_connection = connect_db()
        cursor = db_connection.cursor()
        cursor.execute("UPDATE user_registrations SET division = %s WHERE discord_id = %s", (division, user_id))
        cursor.execute("SELECT user_id FROM user_ids WHERE discord_id = %s", (user_id,))
        user_id_from_db = cursor.fetchone()[0]
        db_connection.commit()
        cursor.close()
        db_connection.close()

        role_id = DIVISION_ROLES.get(division)
        role = interaction.guild.get_role(role_id)
        if role:
            await interaction.user.add_roles(role)

        await send_analysis_message(interaction.guild, user_id, user_name, division, user_id_from_db)

        await interaction.response.send_message("Divisão selecionada com sucesso! Sua solicitação de transferência foi enviada para análise.", ephemeral=True)

async def send_analysis_message(guild, user_id, user_name, division, user_id_from_db):
    analysis_channel = guild.get_channel(1337181666980134964)  # ID do canal de análise de transferência
    if analysis_channel:
        role = guild.get_role(DIVISION_ROLES[division])
        
        # Obter a divisão atual do usuário
        current_division_role = None
        for div, role_id in DIVISION_ROLES.items():
            if guild.get_role(role_id) in guild.get_member(user_id).roles:
                current_division_role = guild.get_role(role_id)
                break

        embed = nextcord.Embed(
            title="📋 Solicitação de Transferência",
            description=f"👤 **Nome:** {user_name}\n🌐 **Divisão Atual:** {current_division_role.mention if current_division_role else 'Nenhuma'}\n🌐 **Nova Divisão:** {role.mention}\n🆔 **ID:** {user_id_from_db}",
            color=nextcord.Color.blue()
        )
        embed.set_thumbnail(url=guild.get_member(user_id).avatar.url)
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")
        embed.add_field(name="📅 Data de Solicitação", value=f"{nextcord.utils.utcnow().strftime('%d/%m/%Y')}", inline=True)
        embed.add_field(name="⏰ Hora de Solicitação", value=f"{nextcord.utils.utcnow().strftime('%H:%M:%S')}", inline=True)
        view = nextcord.ui.View(timeout=None)
        accept_button = AcceptTransferButton(user_id, user_name, division)
        deny_button = DenyTransferButton(user_id, user_name, embed)
        view.add_item(accept_button)
        view.add_item(deny_button)
        await analysis_channel.send(embed=embed, view=view)

class AcceptTransferButton(nextcord.ui.Button):
    def __init__(self, user_id, user_name, division):
        super().__init__(label="ACEITAR", style=nextcord.ButtonStyle.green, custom_id=f"accept_transfer_{user_id}")
        self.user_id = user_id
        self.user_name = user_name
        self.division = division

    async def callback(self, interaction: nextcord.Interaction):
        if INSTRUCTOR_ROLE_ID in [role.id for role in interaction.user.roles]:
            view = nextcord.ui.View(timeout=None)
            dropdown = AcceptDropdown(self.user_id, self.user_name, self.division)
            view.add_item(dropdown)
            await interaction.response.send_message("Selecione a nova patente do usuário:", view=view, ephemeral=True)
        else:
            await interaction.response.send_message("Você não tem permissão para aceitar transferências.", ephemeral=True)

class AcceptDropdown(nextcord.ui.Select):
    def __init__(self, user_id, user_name, division):
        self.user_id = user_id
        self.user_name = user_name
        self.division = division

        options = [
            nextcord.SelectOption(label=role_name, value=role_name)
            for role_name in DIVISION_SPECIFIC_ROLES[self.division].keys()
        ]

        super().__init__(
            placeholder="Escolha a nova patente do usuário",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: nextcord.Interaction):
        specific_role = self.values[0]
        specific_role_id = DIVISION_SPECIFIC_ROLES[self.division][specific_role]
        user = interaction.guild.get_member(self.user_id)
        if user:
            # Remover divisões antigas e cargos de patente
            old_roles = [role for role in user.roles if role.id in DIVISION_ROLES.values() or role.id in [role_id for division in DIVISION_SPECIFIC_ROLES.values() for role_id in division.values()]]
            await user.remove_roles(*old_roles)

            # Adicionar nova divisão e patente
            division_role = interaction.guild.get_role(DIVISION_ROLES[self.division])
            specific_role_obj = interaction.guild.get_role(specific_role_id)
            if division_role and specific_role_obj:
                await user.add_roles(division_role, specific_role_obj)

                # Redefinir e definir novo apelido
                await update_nickname(user, specific_role, self.division)

                # Atualizar a mensagem original para mostrar o botão "SETADO"
                setado_button = nextcord.ui.Button(label="SETADO", style=nextcord.ButtonStyle.gray, disabled=True)
                new_view = nextcord.ui.View(timeout=None)
                new_view.add_item(setado_button)
                try:
                    await interaction.message.edit(view=new_view)
                except nextcord.errors.NotFound:
                    print("Mensagem não encontrada para edição.")

                # Enviar log no canal de logs
                log_channel = interaction.guild.get_channel(1337181665545420827)  # ID do canal de logs
                if log_channel:
                    log_embed = nextcord.Embed(
                        title="Transferência de Divisão Aceita",
                        description=f"**Nome:** {self.user_name}\n**Nova Divisão:** {division_role.mention}\n**Nova Patente:** {specific_role_obj.mention}\n**Aceito por:** {interaction.user.mention}",
                        color=nextcord.Color.green()
                    )
                    await log_channel.send(embed=log_embed)

                await interaction.response.send_message("Transferência aceita com sucesso.", ephemeral=True)
            else:
                await interaction.response.send_message("Cargo ou divisão não encontrado.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)

async def update_nickname(user, specific_role, division):
    db_connection = connect_db()
    cursor = db_connection.cursor()
    cursor.execute("SELECT user_id FROM user_ids WHERE discord_id = %s", (user.id,))
    result = cursor.fetchone()
    cursor.close()
    db_connection.close()
    user_id_from_db = result[0] if result else user.id
    role_abbreviation = ROLE_ABBREVIATIONS.get(specific_role, specific_role)
    # Remover a parte [PATENTE-DIVISAO] do apelido antigo
    old_nickname = user.display_name
    if old_nickname.startswith("["):
        old_nickname = old_nickname.split("] ", 1)[-1]
    new_nickname = f"[{role_abbreviation}-{division}] {old_nickname} | {user_id_from_db}"
    if len(new_nickname) > 32:
        new_nickname = new_nickname[:32]
    await user.edit(nick=new_nickname)  # Definir novo apelido

class DenyTransferButton(nextcord.ui.Button):
    def __init__(self, user_id, user_name, message):
        super().__init__(label="NEGAR", style=nextcord.ButtonStyle.red, custom_id=f"deny_transfer_{user_id}")
        self.user_id = user_id
        self.user_name = user_name
        self.message = message

    async def callback(self, interaction: nextcord.Interaction):
        if INSTRUCTOR_ROLE_ID in [role.id for role in interaction.user.roles]:
            modal = DenyTransferReasonModal(self.user_id, self.user_name, self.message)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Você não tem permissão para negar transferências.", ephemeral=True)

class DenyTransferReasonModal(nextcord.ui.Modal):
    def __init__(self, user_id, user_name, message):
        super().__init__(title="Motivo da Negação", timeout=None)
        self.user_id = user_id
        self.user_name = user_name
        self.message = message
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
                await user.send(f"Sua solicitação de transferência foi negada pelo seguinte motivo: {reason}")

                # Atualizar a mensagem original para mostrar o botão "SETADO"
                setado_button = nextcord.ui.Button(label="SETADO", style=nextcord.ButtonStyle.gray, disabled=True)
                new_view = nextcord.ui.View(timeout=None)
                new_view.add_item(setado_button)
                try:
                    await self.message.edit(view=new_view)
                except nextcord.errors.NotFound:
                    print("Mensagem não encontrada para edição.")

                await interaction.response.send_message("Motivo enviado com sucesso e embed atualizada.", ephemeral=True)
            except nextcord.Forbidden:
                await interaction.response.send_message("Não foi possível enviar a mensagem privada ao usuário.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)

def connect_db():
    return mysql.connector.connect(
        host='172.93.104.61',
        user='u661_rRiE9itGnx',
        password='BgxrDebZCN0Uy!MBjd^1J!Wu',
        database='s661_cadastro_divisao'
    )

def setup(bot):
    print("TransferenciaCog: Carregando cog.")
    bot.add_cog(TransferenciaCog(bot))
