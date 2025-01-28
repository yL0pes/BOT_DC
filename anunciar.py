import nextcord
from nextcord.ext import commands
import asyncio

LOG_CHANNEL_ID = 1331362298182500382  # Substitua pelo ID do canal de log
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

# IDs de cargos para as opções do segundo dropdown
CARGO_IDS_2 = [
    "1317741593679368193", "1317741472623104102", "1317741341463023666", "1317748735673106452", "1318741264660828210",
    "1317751204888969226", "1326562192132280393", "1317747961190547526", "1317747372402671626", "1317747695905013760",
    "1317747068118503474", "1317746949360844840", "1317746854267457547", "1317746735103082567", "1317746528672157807",
    "1317742940042297444"
]

# Títulos personalizados para as opções do segundo dropdown
CURSO_TITLES_2 = [
    "『 ✈ • Licença 』• Piloto Águia", "『🚔 • Curso 』• Piloto Speed", "『🏍 • Curso 』• Piloto GTM", "『 📖 』Curso Recrutador", 
    "💼 • CURSO JUDICIÁRIO - CÓDIGO PENAL", "『 🔫• 』Ammunation", "『 🛒• 』Lojinhas", "『 📋 』(CFSd) • Formação de Soldado",
    "『📋』(CFC) • Formação de Cabo", "『📋』(CFS • 3°) • Formação de 3° Sargento", "『📋』(CFS • 2°) • Formação de 2° Sargento", 
    "『📋』(CFS • 1°) • Formação de 1° Sargento", "『📋』(CFA) • Formação de Aspirante a Oficial", "『📋』(CFSt) • Formação de SubTenente",
    "『📋』(CFT 2°) • Formação de 2° Tenente", "『📋』(CFT 1°) • Formação de 1° Tenente", 
]

SPECIFIC_ROLE_ID = 1317749321395081217  # Substitua pelo ID do cargo específico
BLOCKED_ROLE_ID = 1261742582736621598  # Substitua pelo ID do cargo que bloqueia o uso dos comandos

class AnunciarModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Anunciar Aula",
            timeout=None
        )
        self.data = nextcord.ui.TextInput(
            label="Data",
            placeholder="Digite a data da aula",
            required=True
        )
        self.horario = nextcord.ui.TextInput(
            label="Horário",
            placeholder="Digite o horário da aula",
            required=True
        )
        self.add_item(self.data)
        self.add_item(self.horario)

    async def callback(self, interaction: nextcord.Interaction):
        view = nextcord.ui.View()
        view.add_item(CursoSelect1(self.data.value, self.horario.value))
        view.add_item(CursoSelect2(self.data.value, self.horario.value))
        await interaction.response.send_message("Selecione os cursos:", view=view, ephemeral=True)

class CursoSelect1(nextcord.ui.Select):
    def __init__(self, data, horario):
        self.data = data
        self.horario = horario
        options = [
            nextcord.SelectOption(label=CURSO_TITLES[i], value=CARGO_IDS[i]) for i in range(len(CARGO_IDS))
        ]
        super().__init__(placeholder="Escolha os cursos que deseja anunciar (1-25)", options=options, min_values=1, max_values=25)

    async def callback(self, interaction: nextcord.Interaction):
        selected_courses = ", ".join([f"<@&{value}>" for value in self.values])
        embed = nextcord.Embed(
            title="Cursos Selecionados",
            description=f"Cursos selecionados: {selected_courses}",
            color=nextcord.Color.green()
        )
        embed.add_field(name="INSTRUTOR RESPONSÁVEL", value=interaction.user.mention, inline=False)
        embed.add_field(name="Data", value=self.data, inline=False)
        embed.add_field(name="Horário", value=self.horario, inline=False)
        embed.add_field(name="Alunos", value="Sem presenças marcadas", inline=False)
        embed.add_field(name="Cursos Selecionados", value=selected_courses, inline=False)
        view = PresenceButtonView()
        await interaction.response.send_message(embed=embed, view=view)

class CursoSelect2(nextcord.ui.Select):
    def __init__(self, data, horario):
        self.data = data
        self.horario = horario
        options = [
            nextcord.SelectOption(label=CURSO_TITLES_2[i], value=CARGO_IDS_2[i]) for i in range(len(CARGO_IDS_2))
        ]
        super().__init__(placeholder="Escolha os cursos que deseja anunciar (26-41)", options=options, min_values=1, max_values=16)

    async def callback(self, interaction: nextcord.Interaction):
        selected_courses = ", ".join([f"<@&{value}>" for value in self.values])
        embed = nextcord.Embed(
            title="Cursos Selecionados",
            description=f"Cursos selecionados: {selected_courses}",
            color=nextcord.Color.green()
        )
        embed.add_field(name="INSTRUTOR RESPONSÁVEL", value=interaction.user.mention, inline=False)
        embed.add_field(name="Data", value=self.data, inline=False)
        embed.add_field(name="Horário", value=self.horario, inline=False)
        embed.add_field(name="Alunos", value="Sem presenças marcadas", inline=False)
        embed.add_field(name="Cursos Selecionados", value=selected_courses, inline=False)
        view = PresenceButtonView()
        await interaction.response.send_message(embed=embed, view=view)

class InstrutorSelect(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Instrutor 1", value="instrutor1"),
            nextcord.SelectOption(label="Instrutor 2", value="instrutor2"),
            nextcord.SelectOption(label="Instrutor 3", value="instrutor3")
        ]
        super().__init__(placeholder="Escolha os instrutores", options=options, min_values=1, max_values=3)

    async def callback(self, interaction: nextcord.Interaction):
        selected_instrutores = ", ".join(self.values)
        embed = nextcord.Embed(
            title="Instrutores Selecionados",
            description=f"Instrutores selecionados: {selected_instrutores}",
            color=nextcord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

class AnunciarView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="SIM", style=nextcord.ButtonStyle.green)
    async def sim_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = AnunciarModal()
        await interaction.response.send_modal(modal)
        await interaction.message.delete()
        await interaction.channel.purge(limit=1, check=lambda m: m.author == interaction.user)

    @nextcord.ui.button(label="NÃO", style=nextcord.ButtonStyle.red)
    async def nao_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.message.delete()

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
        if log_channel:
            message_url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.message.id}"
            log_embed = nextcord.Embed(
                title="📋 Curso Aceito",
                color=nextcord.Color.green()
            )
            log_embed.add_field(name="Instrutor que aceitou o curso", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="Curso aceito", value=embed.fields[2].value, inline=False)
            log_embed.add_field(name="Alunos", value=embed.fields[4].value, inline=False)
            log_embed.add_field(name="Link da mensagem", value=f"[Clique aqui]({message_url})", inline=False)
            await log_channel.send(embed=log_embed)
        else:
            print(f"Erro: Canal de log com ID {LOG_CHANNEL_ID} não encontrado.")

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
        
        # Preencher o campo "INSTRUTOR RESPONSÁVEL" com o nome do usuário que negou o curso
        if embed.fields[3].value == "A ser definido":
            embed.set_field_at(3, name="INSTRUTOR RESPONSÁVEL", value=interaction.user.display_name, inline=False)
        
        view = AcceptButtonView()
        view.clear_items()
        view.add_item(DenyButton())
        deny_button = view.children[0]
        deny_button.label = "CURSO NEGADO"
        deny_button.disabled = True
        await interaction.response.edit_message(embed=embed, view=view)

        # Log the denial
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            message_url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.message.id}"
            log_embed = nextcord.Embed(
                title="📋 Curso Negado",
                color=nextcord.Color.red()
            )
            log_embed.add_field(name="Instrutor que negou o curso", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="Motivo de negar o curso", value=self.reason.value, inline=False)
            log_embed.add_field(name="Link da mensagem", value=f"[Clique aqui]({message_url})", inline=False)
            await log_channel.send(embed=log_embed)
        else:
            print(f"Erro: Canal de log com ID {LOG_CHANNEL_ID} não encontrado.")

class MarkPresenceButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="MARCAR PRESENÇA", style=nextcord.ButtonStyle.success)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        if "Sem presenças marcadas" in embed.fields[3].value:
            embed.set_field_at(3, name="Alunos", value=interaction.user.mention, inline=False)
        elif interaction.user.mention not in embed.fields[3].value:
            embed.set_field_at(3, name="Alunos", value=embed.fields[3].value + f"\n{interaction.user.mention}", inline=False)
        await interaction.response.edit_message(embed=embed, view=PresenceButtonView())

        # Log the presence
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = nextcord.Embed(
                title="📋 Presença Marcada",
                color=nextcord.Color.blue()
            )
            log_embed.add_field(name="Aluno", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="Curso", value=embed.fields[4].value, inline=False)
            await log_channel.send(embed=log_embed)
        else:
            print(f"Erro: Canal de log com ID {LOG_CHANNEL_ID} não encontrado.")

class RemovePresenceButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="RETIRAR PRESENÇA", style=nextcord.ButtonStyle.danger)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        alunos = embed.fields[3].value.split("\n")
        if interaction.user.mention in alunos:
            alunos.remove(interaction.user.mention)
            if alunos:
                embed.set_field_at(3, name="Alunos", value="\n".join(alunos), inline=False)
            else:
                embed.set_field_at(3, name="Alunos", value="Sem presenças marcadas", inline=False)
        await interaction.response.edit_message(embed=embed, view=PresenceButtonView())

        # Log the removal of presence
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = nextcord.Embed(
                title="📋 Presença Removida",
                color=nextcord.Color.orange()
            )
            log_embed.add_field(name="Aluno", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="Curso", value=embed.fields[4].value, inline=False)
            await log_channel.send(embed=log_embed)
        else:
            print(f"Erro: Canal de log com ID {LOG_CHANNEL_ID} não encontrado.")

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

        # Log the finalization
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = nextcord.Embed(
                title="📋 Curso Finalizado",
                color=nextcord.Color.purple()
            )
            log_embed.add_field(name="Instrutor responsável", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="Curso", value=interaction.message.embeds[0].fields[4].value, inline=False)
            await log_channel.send(embed=log_embed)
        else:
            print(f"Erro: Canal de log com ID {LOG_CHANNEL_ID} não encontrado.")

class RequestTagButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="PEDIR TAG", style=nextcord.ButtonStyle.secondary)

    async def callback(self, interaction: nextcord.Interaction):
        # Capturar e salvar os dados do usuário na memória do bot
        interaction.client.user_requesting_tag = interaction.user
        print(f"Pedido de tag feito por: {interaction.user.display_name} ({interaction.user.id})")

        # Criar uma nova embed com as informações do usuário e cursos feitos
        embed = nextcord.Embed(title="Pedido de Tag", color=0xffff00)
        embed.add_field(name="Usuário", value=f"{interaction.user.mention}", inline=False)
        embed.add_field(name="Cursos Feitos", value=interaction.message.embeds[0].fields[4].value, inline=False)

        # Enviar a nova embed para um canal específico
        channel = interaction.guild.get_channel(1306026420509737010)  # Substitua pelo ID do seu canal
        message = await channel.send(embed=embed)

        # Adicionar uma reação à mensagem
        await message.add_reaction("✅")

        # Esperar por uma reação de um usuário com o cargo específico
        def check(reaction, user):
            return (
                reaction.message.id == message.id
                and str(reaction.emoji) == "✅"
                and SPECIFIC_ROLE_ID in [role.id for role in user.roles]
            )

        try:
            reaction, user = await interaction.client.wait_for("reaction_add", timeout=600.0, check=check)
        except asyncio.TimeoutError:
            await channel.send("Tempo esgotado para a reação.", delete_after=10)
        else:
            # Atribuir todos os cargos mencionados ao usuário
            user_requesting_tag = interaction.client.user_requesting_tag
            role_ids = [int(curso.strip('<@&>')) for curso in embed.fields[1].value.split(", ")]
            roles = [interaction.guild.get_role(role_id) for role_id in role_ids]
            for role in roles:
                if role:
                    await user_requesting_tag.add_roles(role)

            await channel.send(f"Pedido de tag aprovado por {user.mention} e cargos atribuídos a {user_requesting_tag.mention}!", delete_after=10)

            # Log the situation
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_message = (
                    f"**Instrutor responsável:** {user.mention}\n"
                    f"**Aluno:** {user_requesting_tag.mention}\n"
                    f"**Cursos feitos:** {embed.fields[1].value}"
                )
                await log_channel.send(log_message)
            else:
                print(f"Erro: Canal de log com ID {LOG_CHANNEL_ID} não encontrado.")

class FinalizeButtonView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(FinalizeButton())
        self.add_item(RequestTagButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

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

class Anunciar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="anunciarAula")
    async def anunciar_aula(self, ctx):
        if SPECIFIC_ROLE_ID not in [role.id for role in ctx.author.roles]:
            await ctx.send("Você não tem permissão para usar este comando.")
            return

        embed = nextcord.Embed(
            title="VOCÊ DESEJA ANUNCIAR UMA AULA?",
            description="Clique em SIM para continuar ou NÃO para cancelar.",
            color=nextcord.Color.blue()
        )
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")
        view = AnunciarView()
        await ctx.send(embed=embed, view=view)

    @commands.command(name="tutorial")
    async def tutorial(self, ctx):
        tutorial_messages = [
            (
                "**# 🥸 Tutorial de Comandos - BOT do 𝓛𝓸𝓹𝓮𝓼**\n\n"
                "**- !anunciarAula**\n"
                "`Use este comando para anunciar uma aula. Apenas usuários com o cargo específico (INSTRUTOR CURSOS) podem usar este comando.`\n\n"
                "**- !curso**\n"
                "`Caso a mensagem de Solicitar-aula sumir, esse comando envia ela de novo... Apenas usuários com o cargo específico (INSTRUTOR CURSOS)`\n\n"
                "**- !carteira**\n"
                "`Use este comando para gerenciar sua carteira e visualizar informações financeiras. Apenas usuários com o cargo específico (INSTRUTOR CURSOS)`\n"
            ),
            (
                "#  🌐 Comandos do bot Projeto Null404 🌐\n"
                "**Criar uma nova QSV**\n"
                "```!qsv [Nome QSV]```\n"
                "🛠️  **Remover ID [DISCORD] da blacklist**\n"
                "```!Removerdc [id do discord]```\n"
                "🛠️  **Adicionar ID [JOGO] na blacklist**\n"
                "```!addbl [ID] [Motivo]```\n"
                "🛠️  **Remover ID [JOGO] da blacklist**\n"
                "```!rebl [ID] [Motivo]```\n"
                "🛠️  **Consultar ID na blacklist**\n"
                "```!verid [ID]```\n"
                "🛠️  **Desbugar Membros**\n"
                "```!desbugar [ID do discord do membro]```\n"
            ),
            (
                "> remover da db:\n"
                "- __Tickets abertos__\n"
                "- __Adicionar ou remover membros nos tickets__\n"
                "- __Remover membro da QSV__\n"
                "- __Análise bateponto ou análise verificação__\n"
                "- __Remover ausência__\n"
                "- __Remover de QSV__\n"
                "- __Adicionar horas ao membro__\n"
                "```!addhoras [Mencionar membro] [tempo em horas]```\n"
                "🛠️  **Remover horas do membro**\n"
                "```!rehoras [Mencionar membro] [tempo em horas]```\n"
                "🛠️  **Advertir membro**\n"
                "```!adv [Mencionar membro] [tempo em dias] [motivo]```\n"
                "🛠️  **Remover advertência membro**\n"
                "```!readv [Mencionar membro] [motivo]```\n"
            ),
            (
                "🛠️  **Exonerar membro**\n"
                "```!exonerar [Mencionar membro] [motivo]```\n"
                "🛠️  **Setar membros para sua subdivisão / setagem de cursos**\n"
                "```!set [Mencionar Membro] [Mencionar Cargo]```\n"
                "🛠️  **Puxar a ficha de qualquer membro**\n"
                "```!ficha [Mencionar Membro]```\n"
                "🛠️  **Remover Id antigo do membro**\n"
                "```!reid [Mencionar Membro]```\n"
                "🛠️  **Verificar conclusão dos cursos dentro do tempo prédefinido (todos membros)**\n"
                "```!verificarCursos```\n"
                "🛠️  **Verificar conclusão dos cursos dentro do tempo prédefinido (cargo especifico)**\n"
                "```!verificarCursos [Mencionar Cargo]```\n"
                "🛠️  **Remover ID salvo na database**\n"
                "```!reid [Mencionar o membro]```\n"
                "🛠️  **Anunciar para todos membros na DM**\n"
                "```!anuncio [mensagem]```\n"
            )
        ]
        
        for message in tutorial_messages:
            await ctx.author.send(message)

def setup(bot):
    bot.add_cog(Anunciar(bot))
