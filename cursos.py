import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal, TextInput

intents = nextcord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class CourseModal(Modal):
    def __init__(self, user):
        super().__init__(title="Anunciar Aula")
        self.user = user

        self.course_name = TextInput(label="Nome do curso")
        self.date = TextInput(label="DATA")
        self.time = TextInput(label="Horário (ex: 2200)")
        self.location = TextInput(label="LOCAL de Alinhamento")
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

    @nextcord.ui.button(label="ANUNCIAR AULA", style=nextcord.ButtonStyle.primary)
    async def announce_button(self, button: Button, interaction: nextcord.Interaction):
        if self.role_id in [role.id for role in interaction.user.roles]:
            modal = CourseModal(interaction.user)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)

class AnnounceView(View):
    @nextcord.ui.button(label="📢 ANUNCIAR AULA", style=nextcord.ButtonStyle.primary)
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
    embed = nextcord.Embed(title="Cursos", description="Descrição dos cursos disponíveis.")
    view = CourseView(role_id=1323359921093345318)  # Substitua pelo ID do cargo específico
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f'{bot.user} está logado e pronto para uso!')

bot.run('MTMwOTk2OTMyNTc1MDQ4NTA4NA.GQhfBY.V3Abkw2laoEMuQCLZv9Fqiy-Ma813CAboK5xik')