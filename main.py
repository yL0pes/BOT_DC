import nextcord
from nextcord.ext import commands
from nextcord import Interaction, ButtonStyle
from nextcord.ui import Button, View, Modal, TextInput

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CourseModal(Modal):
    def __init__(self, user):
        super().__init__(title="CRIAR AULA")
        self.user = user

        self.course_name = TextInput(label="Nome do curso")
        self.date = TextInput(label="Data")
        self.time = TextInput(label="Horário do curso (HHMM)")
        self.location = TextInput(label="Local de Alinhamento")
        self.notes = TextInput(label="Observações", required=False)

        self.add_item(self.course_name)
        self.add_item(self.date)
        self.add_item(self.time)
        self.add_item(self.location)
        self.add_item(self.notes)

    async def callback(self, interaction: nextcord.Interaction):
        formatted_time = f"{self.time.value[:2]}:{self.time.value[2:]}"
        embed = nextcord.Embed(title=f"📚 {self.course_name.value}", description="Detalhes do Curso")
        embed.add_field(name="📅 DATA", value=self.date.value, inline=False)
        embed.add_field(name="⏰ Horário", value=formatted_time, inline=False)
        embed.add_field(name="📍 LOCAL de Alinhamento", value=self.location.value, inline=False)
        embed.add_field(name="📝 Observações", value=self.notes.value or "Nenhuma", inline=False)
        embed.add_field(name="👨‍🏫 INSTRUTOR RESPONSÁVEL", value=self.user.mention, inline=False)
        
        view = AnnounceView()
        await interaction.response.send_message(embed=embed, view=view)

class CourseView(View):
    def __init__(self, role_id):
        super().__init__()
        self.role_id = role_id

    @nextcord.ui.button(label="CRIAR AULA", style=nextcord.ButtonStyle.primary)
    async def announce_button(self, button: Button, interaction: nextcord.Interaction):
        if self.role_id in [role.id for role in interaction.user.roles]:
            modal = CourseModal(interaction.user)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)

class AnnounceView(View):
    @nextcord.ui.button(label="📢 CRIAR AULA", style=nextcord.ButtonStyle.primary)
    async def announce_class(self, button: Button, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        view = PresenceView()
        await interaction.message.edit(embed=embed, view=view)
        
        # Enviar mensagem privada para todos os membros do servidor
        for member in interaction.guild.members:
            if not member.bot:
                try:
                    await member.send(f"Uma nova aula foi anunciada: {embed.title}\n{embed.description}")
                except:
                    pass

class PresenceView(View):
    @nextcord.ui.button(label="MARCAR PRESENÇA", style=nextcord.ButtonStyle.success)
    async def mark_presence(self, button: Button, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        field_name = "📚 ALUNOS"
        student_info = f"{interaction.user.mention} (ID: {interaction.user.id}) 📖"
        
        if any(field.name == field_name for field in embed.fields):
            for field in embed.fields:
                if field.name == field_name:
                    field.value += f"\n{student_info}"
        else:
            embed.add_field(name=field_name, value=student_info, inline=False)
        
        await interaction.message.edit(embed=embed)

    @nextcord.ui.button(label="RETIRAR PRESENÇA", style=nextcord.ButtonStyle.danger)
    async def remove_presence(self, button: Button, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        field_name = "📚 ALUNOS"
        student_info = f"{interaction.user.mention} (ID: {interaction.user.id}) 📖"
        
        if any(field.name == field_name for field in embed.fields):
            for field in embed.fields:
                if field.name == field_name:
                    field.value = "\n".join([line for line in field.value.split("\n") if line != student_info])
                    if not field.value.strip():
                        embed.remove_field(embed.fields.index(field))
        
        await interaction.message.edit(embed=embed)

    @nextcord.ui.button(label="FECHAR CURSO", style=nextcord.ButtonStyle.primary)
    async def close_course(self, button: Button, interaction: nextcord.Interaction):
        role_id = 1323359921093345318  # Substitua pelo ID do cargo específico
        if role_id in [role.id for role in interaction.user.roles]:
            button.label = "CURSO FINALIZADO"
            button.disabled = True
            for item in self.children:
                if isinstance(item, Button) and item.label != "CURSO FINALIZADO":
                    item.disabled = True
            await interaction.message.edit(view=self)
        else:
            await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)

@bot.command(name='cursos')
async def cursos(ctx):
    embed = nextcord.Embed(title=" 📢 CLIQUE NO BOTÃO ABAIXO PARA ANUNCIAR UMA AULA", description="Novo BOT de anunciar aulas: prático, rápido e eficiente para divulgar suas aulas com facilidade!")
    view = CourseView(role_id=1323359921093345318)  # Substitua pelo ID do cargo específico
    await ctx.send(embed=embed, view=view)


class ActionModal(Modal):
    def __init__(self):
        super().__init__(title="Registrar Ação")
        self.action_name = TextInput(label="Nome da Ação", max_length=100)
        self.total_police = TextInput(label="Total de Policiais", max_length=100)
        self.faction_name = TextInput(label="Nome da Facção", max_length=100)
        self.action_time = TextInput(label="Horário da Ação (HHMM)", max_length=100)
        self.add_item(self.action_name)
        self.add_item(self.total_police)
        self.add_item(self.faction_name)
        self.add_item(self.action_time)

    async def callback(self, interaction: Interaction):
        action_time_formatted = f"{self.action_time.value[:2]}:{self.action_time.value[2:]}"
        embed = nextcord.Embed(title="Ação Registrada", color=0x00ff00)
        embed.add_field(name="📝 Nome da Ação", value=self.action_name.value, inline=True)
        embed.add_field(name="👮 Total de Policiais", value=self.total_police.value, inline=True)
        embed.add_field(name="💩 Nome da Facção", value=self.faction_name.value, inline=True)
        embed.add_field(name="⏱️ Horário da Ação", value=action_time_formatted, inline=True)
        embed.add_field(name="🪪 Presenças", value="Nenhuma presença marcada", inline=False)

        user_list = []

        async def mark_presence_callback(interaction: Interaction):
            user = interaction.user
            user_info = f"{user.display_name} ✅ ({user.id})"
            if user_info not in user_list:
                user_list.append(user_info)
                description = "\n".join(user_list)
                embed.set_field_at(4, name="🪪 Presenças", value=description, inline=False)
                await interaction.message.edit(embed=embed)

        async def remove_presence_callback(interaction: Interaction):
            user = interaction.user
            user_info = f"{user.display_name} ✅ ({user.id})"
            if user_info in user_list:
                user_list.remove(user_info)
                description = "\n".join(user_list) if user_list else "Nenhuma presença marcada"
                embed.set_field_at(4, name="🪪 Presenças", value=description, inline=False)
                await interaction.message.edit(embed=embed)

        async def close_action_callback(interaction: Interaction):
            embed.add_field(name="🌐 Status", value="Ação Finalizada", inline=False)
            view = View()
            finished_button = Button(label="AÇÃO FINALIZADA", style=ButtonStyle.gray, disabled=True)
            view.add_item(finished_button)

            victory_button = Button(label="VITÓRIA", style=ButtonStyle.green)
            defeat_button = Button(label="DERROTA", style=ButtonStyle.red)

            async def victory_callback(interaction: Interaction):
                if 1323359919814086704 in [role.id for role in interaction.user.roles]:  # Replace ROLE_ID with the actual role ID
                    embed.color = 0x00ff00
                    embed.set_field_at(5, name="🌐 Status", value="Vitória", inline=False)
                    view = View()
                    finished_button = Button(label="VITÓRIA", style=ButtonStyle.green, disabled=True)
                    view.add_item(finished_button)
                    await interaction.message.edit(embed=embed, view=view)

            async def defeat_callback(interaction: Interaction):
                if 1323359919814086704 in [role.id for role in interaction.user.roles]:  # Replace ROLE_ID with the actual role ID
                    embed.color = 0xff0000
                    embed.set_field_at(5, name="🌐 Status", value="Derrota", inline=False)
                    view = View()
                    finished_button = Button(label="DERROTA", style=ButtonStyle.red, disabled=True)
                    view.add_item(finished_button)
                    await interaction.message.edit(embed=embed, view=view)

            victory_button.callback = victory_callback
            defeat_button.callback = defeat_callback

            view.add_item(victory_button)
            view.add_item(defeat_button)
            await interaction.message.edit(embed=embed, view=view)

        mark_presence_button = Button(label="Marcar Presença", style=ButtonStyle.green)
        mark_presence_button.callback = mark_presence_callback

        remove_presence_button = Button(label="Retirar Presença", style=ButtonStyle.red)
        remove_presence_button.callback = remove_presence_callback

        close_action_button = Button(label="Fechar Ação", style=ButtonStyle.gray)
        close_action_button.callback = close_action_callback

        view = View()
        view.add_item(mark_presence_button)
        view.add_item(remove_presence_button)
        view.add_item(close_action_button)
    
        # Send the embed to a different channel
        target_channel_id = 1323359925681913981  # Replace with your target channel ID
        target_channel = bot.get_channel(target_channel_id)
        if target_channel:
            await target_channel.send(embed=embed, view=view)
        else:
            await interaction.response.send_message("O canal alvo não foi encontrado.", ephemeral=True)

@bot.command(name="acao")
@commands.has_role(1323359919814086704)  # Replace ROLE_ID with the actual role ID
async def acao(ctx):
    button = Button(label="Registrar Ação", style=ButtonStyle.green)

    async def button_callback(interaction: Interaction):
        if 1323359919814086704 in [role.id for role in interaction.user.roles]:  # Replace ROLE_ID with the actual role ID
            modal = ActionModal()
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    
    embed = nextcord.Embed(title="CLIQUE NO BOTÃO PARA REGISTRAR UMA AÇÃO:", description="- Lembre-se de utilizar apenas números para informar a quantidade de membros e o horário da ação. \n**Unidos pela missão, prontos para a vitória!**", color=0x00ff00)
    embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")
    await ctx.send(embed=embed, view=view)

@acao.error
async def acao_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Você não tem permissão para usar este comando.")

@bot.event
async def on_ready():
    print(f"LOGADO COMO: {bot.user.name}")

if __name__ == '__main__':
    bot.run("MTMwOTk2OTMyNTc1MDQ4NTA4NA.GQhfBY.V3Abkw2laoEMuQCLZv9Fqiy-Ma813CAboK5xik")