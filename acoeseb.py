import nextcord
from nextcord.ext import commands
from nextcord import Interaction, ButtonStyle
from nextcord.ui import Button, View

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# !hi
# !hello

@bot.command(name="oi")
async def SendMessage(ctx):
    await ctx.send('Olá!')

@bot.command(name="acao")
async def acao(ctx):
    button = Button(label="Mark presence", style=ButtonStyle.green)

    async def button_callback(interaction: Interaction):
        user = interaction.user
        await interaction.response.send_message(f"{user.name} ✅ ({user.id})", ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    await ctx.send("Click the button to mark your presence:", view=view)

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")

if __name__ == '__main__':
    bot.run("YOUR_BOT_TOKEN_HERE")