from nextcord.ext import commands
import nextcord

# IDs de cargos para os cursos
CARGO_IDS = [
    "1323359920338505818", "1323359920338505819", "1323359920338505820", "1323359920338505821", "1323359920338505822",
    "1323359920338505823", "1323359920338505824", "1323359920338505825", "1323359920338505826", "1323359920338505827",
    "1323359920338505828", "1323359920338505829", "1323359920338505830", "1323359920338505831", "1323359920338505832",
    "1323359920338505833", "1323359920338505834", "1323359920338505835", "1323359920338505836", "1323359920338505837",
    "1323359920338505838", "1323359920338505839", "1323359920338505840", "1323359920338505841", "1323359920338505842"
]

class CursoDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label=f"Curso {i+1}", description=f"Descrição do Curso {i+1}", value=CARGO_IDS[i])
            for i in range(25)
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
        
        # Enviar a embed para um canal diferente junto com o botão ACEITAR CURSO
        view = AcceptButtonView()
        channel = interaction.guild.get_channel(1323359923131781213)  # Substitua pelo ID do seu canal
        await channel.send(embed=embed, view=view)

class AcceptButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="ACEITAR CURSO", style=nextcord.ButtonStyle.primary)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        if embed.fields[3].value == "A ser definido":
            embed.set_field_at(3, name="INSTRUTOR RESPONSÁVEL", value=interaction.user.display_name, inline=False)
        view = PresenceButtonView()
        await interaction.response.edit_message(embed=embed, view=view)

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
        interaction.client.user_requesting_tag = interaction.user
        await interaction.response.send_message("Pedido de tag enviado!", ephemeral=True)

class AcceptButtonView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AcceptButton())

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
        view = CursoDropdownView()
        await ctx.send("Escolha um curso:", view=view)

def setup(bot):
    bot.add_cog(Curso(bot))