from nextcord.ext import commands
import nextcord
import asyncio

LOG_CHANNEL_ID = 1265452627068456980  # Substitua pelo ID do canal de log
INVALID_ROLE_EMOJI = "❌"  # Emoji de X (negativo)

# IDs de cargos para os cursos
CARGO_IDS = [
    "1317745632898711572", "1317745806719058001", "1317748586980835328", "1317746273511673878", "1317745723034570793",
    "1317745913678139482", "1317746167198777404", "1317748467761676341", "1317746069781745694", "1317750633117253632",
    "1317750155793137684", "1317748868078768138", "1317750048380944446", "1317750393140281415", "1317750498320711680",
    "1317749086249549824", "1317748977483120680", "1317750263368646706", "1317749209176342558", "1317742810136580096",
    "1317742633371566111", "1317751705852575744", "1317742524479311903", "1317742414529560688", "1317741717558001754",
]

# Títulos personalizados para os cursos
CURSO_TITLES = [
    "『 🥉• Curso 』• Modulação", "『 🥇• Curso 』• Conduta e Ética", "『🧑‍✈️ • Curso 』• Condução P1",
    "『⚜️ • Curso 』• Apresentação", "『 🥈• Curso 』• Formação", "『🚓 • Curso 』• Abordagem e Acompanhamento",
    "『🔱 • Curso 』• Curso - Prisão", "『 💸• Curso 』• Multa e Apreensão", "『 🚧 • Curso 』• Blitz",
    "『 👮‍♂️ 』Curso • Atirador Tático", "『 👮‍♂️ 』Curso • Patrulhamento Tático", "『 👮‍♂️ 』Curso • Comboio",
    "『 👮‍♂️ 』Curso • Montanha", "『 👮‍♂️ 』Curso • Mergulhador", "『 🪂 』Curso • Paraquedista",
    "『 👮‍♂️ 』Curso • R.O / Pacificação", "『 👮‍♂️ 』Curso • Incursão Tática", "『 👮‍♂️ 』Curso • Anti Sequestro",
    "『 👮‍♂️ 』Curso • Negociador", "『💎 • Curso』Joalheria", "『🐓• Curso』Galinheiro",
    "『🐂 • Curso』Açougue", "『 🏭• Curso 』Níobio", "『 💵• Curso 』Banco Central",
    "『 💰• Curso』Banco Paleto",
]

SPECIFIC_ROLE_ID = 1317749321395081217  # Substitua pelo ID do cargo específico

class CursoDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label=CURSO_TITLES[i], value=CARGO_IDS[i])
            for i in range(len(CARGO_IDS))
        ]
        super().__init__(placeholder="Escolha um curso...", options=options, min_values=1, max_values=len(options))

    async def callback(self, interaction: nextcord.Interaction):
        selected_courses = self.values
        modal = CursoModal(selected_courses)
        await interaction.response.send_modal(modal)

class CursoDropdownView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CursoDropdown())

class CursoModal(nextcord.ui.Modal):
    def __init__(self, cursos):
        super().__init__(title="Detalhes dos Cursos")
        self.cursos = cursos

        self.data = nextcord.ui.TextInput(
            label="DATA",
            placeholder="Insira a data",
            required=True
        )
        self.horario = nextcord.ui.TextInput(
            label="HORARIO DISPONIVEL",
            placeholder="Insira o horário disponível",
            required=True
        )

        self.add_item(self.data)
        self.add_item(self.horario)

    async def callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Detalhes dos Cursos", color=0x00ff00)
        embed.add_field(name="Data", value=self.data.value, inline=False)
        embed.add_field(name="Horário", value=self.horario.value, inline=False)
        cursos_mention = ", ".join([f"<@&{curso}>" for curso in self.cursos])
        embed.add_field(name="Cursos Selecionados", value=cursos_mention, inline=False)
        embed.add_field(name="INSTRUTOR RESPONSÁVEL", value="A ser definido", inline=False)
        embed.add_field(name="Alunos", value="Sem presenças marcadas", inline=False)
        
        # Enviar a embed para um canal diferente junto com os botões ACEITAR CURSO e NEGAR CURSO
        view = AcceptButtonView()
        channel = interaction.guild.get_channel(1330321000763752510)  # Substitua pelo ID do seu canal
        await channel.send(embed=embed, view=view)

class AcceptButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="ACEITAR CURSO", style=nextcord.ButtonStyle.primary)

    async def callback(self, interaction: nextcord.Interaction):
        if SPECIFIC_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        if embed.fields[3].value == "A ser definido":
            embed.set_field_at(3, name="INSTRUTOR RESPONSÁVEL", value=interaction.user.display_name, inline=False)
        view = PresenceButtonView()
        await interaction.response.edit_message(embed=embed, view=view)

        # Log the acceptance
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        message_url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.message.id}"
        log_message = (
            f"**Instrutor que aceitou o curso:** {interaction.user.mention}\n"
            f"**Curso aceito:** {embed.fields[2].value}\n"
            f"**Alunos:** {embed.fields[4].value}\n"
            f"[Link da mensagem]({message_url})"
        )
        await log_channel.send(log_message)

class DenyButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="NEGAR CURSO", style=nextcord.ButtonStyle.danger)

    async def callback(self, interaction: nextcord.Interaction):
        if SPECIFIC_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)
            return

        modal = DenyReasonModal()
        await interaction.response.send_modal(modal)

class DenyReasonModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Motivo da Negação do Curso")
        self.reason = nextcord.ui.TextInput(
            label="Por que vai negar o curso?",
            placeholder="Descreva o motivo",
            required=True
        )
        self.add_item(self.reason)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        embed.add_field(name="Motivo da Negação", value=self.reason.value, inline=False)
        view = AcceptButtonView()
        view.clear_items()
        view.add_item(DenyButton())
        deny_button = view.children[0]
        deny_button.label = "CURSO NEGADO"
        deny_button.disabled = True
        await interaction.response.edit_message(embed=embed, view=view)

        # Log the denial
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        message_url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.message.id}"
        log_message = (
            f"**Instrutor que negou o curso:** {interaction.user.mention}\n"
            f"**Motivo de negar o curso:** {self.reason.value}\n"
            f"[Link da mensagem]({message_url})"
        )
        await log_channel.send(log_message)

class MarkPresenceButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="MARCAR PRESENÇA", style=nextcord.ButtonStyle.success)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        if "Sem presenças marcadas" in embed.fields[4].value:
            embed.set_field_at(4, name="Alunos", value=interaction.user.display_name, inline=False)
        elif interaction.user.display_name not in embed.fields[4].value:
            embed.set_field_at(4, name="Alunos", value=embed.fields[4].value + f"\n{interaction.user.display_name}", inline=False)
        await interaction.response.edit_message(embed=embed, view=PresenceButtonView())

class RemovePresenceButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="RETIRAR PRESENÇA", style=nextcord.ButtonStyle.danger)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        alunos = embed.fields[4].value.split("\n")
        if interaction.user.display_name in alunos:
            alunos.remove(interaction.user.display_name)
            if alunos:
                embed.set_field_at(4, name="Alunos", value="\n".join(alunos), inline=False)
            else:
                embed.set_field_at(4, name="Alunos", value="Sem presenças marcadas", inline=False)
        await interaction.response.edit_message(embed=embed, view=PresenceButtonView())

class FinalizeButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="FINALIZAR CURSO", style=nextcord.ButtonStyle.secondary)

    async def callback(self, interaction: nextcord.Interaction):
        if SPECIFIC_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)
            return

        self.label = "CURSO FINALIZADO"
        self.disabled = True
        view = FinalizeButtonView()
        view.clear_items()
        view.add_item(self)
        view.add_item(RequestTagButton())
        await interaction.response.edit_message(view=view)

class RequestTagButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="PEDIR TAG", style=nextcord.ButtonStyle.secondary)

    async def callback(self, interaction: nextcord.Interaction):
        # Capturar e salvar os dados do usuário na memória do bot
        interaction.client.user_requesting_tag = interaction.user
        print(f"Pedido de tag feito por: {interaction.user.display_name} ({interaction.user.id})")

        # Criar uma nova embed com as informações do usuário e cursos feitos
        embed = nextcord.Embed(title="Pedido de Tag", color=0xffff00)
        embed.add_field(name="Usuário", value=f"{interaction.user.display_name} ({interaction.user.id})", inline=False)
        embed.add_field(name="Cursos Feitos", value=", ".join([f"<@&{curso}>" for curso in interaction.message.embeds[0].fields[2].value.split(", ")]), inline=False)

        # Enviar a nova embed para um canal específico
        channel = interaction.guild.get_channel(1306026420509737010)  # Substitua pelo ID do seu canal
        await channel.send(embed=embed)

        await interaction.response.send_message("Pedido de tag enviado!", ephemeral=True)

class SetRoleButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="SETAR CARGO", style=nextcord.ButtonStyle.primary)

    async def callback(self, interaction: nextcord.Interaction):
        pass  # Nenhuma função definida ainda

class AcceptButtonView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AcceptButton())
        self.add_item(DenyButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class PresenceButtonView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MarkPresenceButton())
        self.add_item(RemovePresenceButton())
        self.add_item(FinalizeButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class FinalizeButtonView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(FinalizeButton())
        self.add_item(RequestTagButton())
        self.add_item(SetRoleButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class Curso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_requesting_tag = None

    @commands.command(name='cursos')
    async def cursos(self, ctx):
        embed = nextcord.Embed(title="Escolha um curso", description=" - Novo BOT de solicitar aulas! Escolha um curso na lista abaixo e aguarde um Instrutor aceitar o seu Curso.", color=0xffff00)
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼 ")
        view = CursoDropdownView()
        await ctx.send(embed=embed, view=view)

    @commands.command(name='setar')
    @commands.has_role(1323359920384512119)
    async def setar(self, ctx, *args):
        members = [member for member in ctx.message.mentions if isinstance(member, nextcord.Member)]
        roles = [role for role in ctx.message.role_mentions if isinstance(role, nextcord.Role)]

        if not members or not roles:
            await ctx.send("Por favor, mencione pelo menos um usuário e um cargo.", delete_after=5)
            return

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        log_message = f"**Comando `!setar` usado por {ctx.author.mention}**\n"

        for member in members:
            log_message += f"**Usuário:** {member.mention}\n"
            log_message += "**Cargos atribuídos:**\n"
            for role in roles:
                try:
                    await member.add_roles(role)
                    await ctx.send(f"Cargo {role.mention} atribuído a {member.mention}.", delete_after=3)
                    log_message += f"- {role.mention}\n"
                except nextcord.Forbidden:
                    await ctx.message.add_reaction(INVALID_ROLE_EMOJI)
                    await asyncio.sleep(4)
                    await ctx.message.delete()
                    return

        await log_channel.send(log_message)

        await asyncio.sleep(2)
        await ctx.message.delete()
        await asyncio.sleep(2)
        await ctx.channel.purge(limit=1)

    @setar.error
    async def setar_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            try:
                await ctx.author.send("Você não tem permissão para usar este comando.")
            except nextcord.Forbidden:
                await ctx.send(f"{ctx.author.mention}, você não tem permissão para usar este comando.", delete_after=2)
            await asyncio.sleep(2)
            await ctx.message.delete()

def setup(bot):
    bot.add_cog(Curso(bot))