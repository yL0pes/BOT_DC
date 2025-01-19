from nextcord.ext import commands
import nextcord

# Define role IDs as variables
role_id_1 = 123456789012345678
role_id_2 = 223456789012345678
role_id_3 = 323456789012345678
role_id_4 = 423456789012345678
role_id_5 = 523456789012345678
role_id_6 = 623456789012345678
role_id_7 = 723456789012345678
role_id_8 = 823456789012345678
role_id_9 = 923456789012345678
role_id_10 = 1023456789012345678
role_id_11 = 1123456789012345678
role_id_12 = 1223456789012345678
role_id_13 = 1323456789012345678
role_id_14 = 1423456789012345678
role_id_15 = 1523456789012345678
role_id_16 = 1623456789012345678
role_id_17 = 1723456789012345678
role_id_18 = 1823456789012345678
role_id_19 = 1923456789012345678
role_id_20 = 2023456789012345678
role_id_21 = 2123456789012345678
role_id_22 = 2223456789012345678
role_id_23 = 2323456789012345678
role_id_24 = 2423456789012345678
role_id_25 = 2523456789012345678

class RoleDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label=f"Role {i}", value=str(eval(f'role_id_{i}')))
            for i in range(1, 26)
        ]
        super().__init__(placeholder="Escolha um cargo...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.send_modal(ScheduleForm(self.values[0]))

class ScheduleForm(nextcord.ui.Modal):
    def __init__(self, role_id):
        super().__init__(title="Formulário de Agendamento")
        self.role_id = role_id

        self.add_item(nextcord.ui.TextInput(label="Data", placeholder="DD/MM/YYYY"))
        self.add_item(nextcord.ui.TextInput(label="Horário Disponível", placeholder="HH:MM"))

    async def callback(self, interaction: nextcord.Interaction):
        data = self.children[0].value
        horario = self.children[1].value

        embed = nextcord.Embed(title="Informações de Agendamento", color=0x2F3136)
        embed.add_field(name="Cargo ID", value=self.role_id, inline=False)
        embed.add_field(name="Data", value=data, inline=False)
        embed.add_field(name="Horário Disponível", value=horario, inline=False)

        await interaction.response.send_message(embed=embed)

class DropdownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RoleDropdown())

class Alunos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='alunos')
    async def alunos(self, ctx):
        embed = nextcord.Embed(title="Lista de Alunos", description="João, Maria, Pedro, Ana", color=0x2F3136)  # Gray color
        view = DropdownView()
        await ctx.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Alunos(bot))