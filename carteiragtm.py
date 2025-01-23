import nextcord
from nextcord.ext import commands
from nextcord import ui, File
from PIL import Image, ImageDraw, ImageFont
import os

class CarteiraGTM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class UserForm(ui.Modal):
        def __init__(self, bot):
            super().__init__("User Information Form")
            self.bot = bot
            self.qra = ui.TextInput(label="QRA")
            self.id = ui.TextInput(label="ID")
            self.tempo_prova_primeira_parte = ui.TextInput(label="Tempo de Prova Primeira Parte")
            self.tempo_prova_segunda_parte = ui.TextInput(label="Tempo de Prova Segunda Parte")
            self.add_item(self.qra)
            self.add_item(self.id)
            self.add_item(self.tempo_prova_primeira_parte)
            self.add_item(self.tempo_prova_segunda_parte)

        async def callback(self, interaction: nextcord.Interaction):
            # Load the image
            img = Image.open("template.png")
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 20)

            # Draw the text on the image
            draw.text((10, 10), f"QRA: {self.qra.value}", font=font, fill="black")
            draw.text((10, 40), f"ID: {self.id.value}", font=font, fill="black")
            draw.text((10, 70), f"Tempo de Prova Primeira Parte: {self.tempo_prova_primeira_parte.value}", font=font, fill="black")
            draw.text((10, 100), f"Tempo de Prova Segunda Parte: {self.tempo_prova_segunda_parte.value}", font=font, fill="black")

            # Save the image
            img.save("output.png")

            # Send the image to a specific channel
            channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
            channel = self.bot.get_channel(channel_id)
            await channel.send(file=File("output.png"))

    @commands.command()
    async def form(self, ctx):
        await ctx.send_modal(self.UserForm(self.bot))

def setup(bot):
    bot.add_cog(CarteiraGTM(bot))
