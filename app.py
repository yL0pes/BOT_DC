import nextcord
from nextcord.ext import commands
from nextcord import Interaction, ButtonStyle
from nextcord.ui import Button, View, Modal, TextInput

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# !hi
# !hello

@bot.command(name="oi")
async def SendMessage(ctx):
    await ctx.send('Olá!')

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
        embed.add_field(name="Nome da Ação", value=self.action_name.value, inline=False)
        embed.add_field(name="Total de Policiais", value=self.total_police.value, inline=False)
        embed.add_field(name="Nome da Facção", value=self.faction_name.value, inline=False)
        embed.add_field(name="Horário da Ação", value=action_time_formatted, inline=False)

        button = Button(label="Marcar Presença", style=ButtonStyle.green)
        user_list = []

        async def button_callback(interaction: Interaction):
            user = interaction.user
            user_info = f"{user.display_name} ✅ ({user.id})"
            if user_info not in user_list:
                user_list.append(user_info)
                description = "\n".join(user_list)
                embed.clear_fields()
                embed.add_field(name="Nome da Ação", value=self.action_name.value, inline=False)
                embed.add_field(name="Total de Policiais", value=self.total_police.value, inline=False)
                embed.add_field(name="Nome da Facção", value=self.faction_name.value, inline=False)
                embed.add_field(name="Horário da Ação", value=action_time_formatted, inline=False)
                embed.add_field(name="Presenças", value=description, inline=False)
                await interaction.message.edit(embed=embed)

        button.callback = button_callback
        view = View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)

@bot.command(name="acao")
async def acao(ctx):
    button = Button(label="Registrar Ação", style=ButtonStyle.green)

    async def button_callback(interaction: Interaction):
        modal = ActionModal()
        await interaction.response.send_modal(modal)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    await ctx.send("Clique no botão para registrar uma ação:", view=view)

@bot.event
async def on_ready():
    print(f"LOGADO COMO: {bot.user.name}")

if __name__ == '__main__':
    bot.run("MTMwOTk2OTMyNTc1MDQ4NTA4NA.GQhfBY.V3Abkw2laoEMuQCLZv9Fqiy-Ma813CAboK5xik")