from nextcord.ext import commands
import nextcord

class FormModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Formulário de Prova")

        self.qra = nextcord.ui.TextInput(
            label="QRA",
            placeholder="Insira seu QRA",
            required=True
        )
        self.id = nextcord.ui.TextInput(
            label="ID",
            placeholder="Insira seu ID",
            required=True
        )
        self.tempo_prova_1 = nextcord.ui.TextInput(
            label="TEMPO DE PROVA (PRIMEIRA PARTE)",
            placeholder="Insira o tempo da primeira parte da prova",
            required=True
        )
        self.tempo_prova_2 = nextcord.ui.TextInput(
            label="TEMPO DE PROVA (SEGUNDA PARTE)",
            placeholder="Insira o tempo da segunda parte da prova",
            required=True
        )

        self.add_item(self.qra)
        self.add_item(self.id)
        self.add_item(self.tempo_prova_1)
        self.add_item(self.tempo_prova_2)

    async def callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Formulário de Prova", color=0x00ff00)
        embed.add_field(name="QRA", value=self.qra.value, inline=False)
        embed.add_field(name="ID", value=self.id.value, inline=False)
        embed.add_field(name="Tempo de Prova (Primeira Parte)", value=self.tempo_prova_1.value, inline=False)
        embed.add_field(name="Tempo de Prova (Segunda Parte)", value=self.tempo_prova_2.value, inline=False)

        await interaction.response.send_message("Por favor, envie a imagem agora.", ephemeral=True)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.attachments

        try:
            message = await interaction.client.wait_for('message', check=check, timeout=60.0)
            if message.attachments:
                embed.set_image(url=message.attachments[0].url)
                await interaction.followup.send(embed=embed)
                await message.delete()  # Excluir a mensagem do usuário após o envio
            else:
                await interaction.followup.send("Nenhuma imagem anexada.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("Tempo esgotado para enviar a imagem.", ephemeral=True)

class FormButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="Abrir Formulário", style=nextcord.ButtonStyle.primary)

    async def callback(self, interaction: nextcord.Interaction):
        modal = FormModal()
        await interaction.response.send_modal(modal)

class FormView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(FormButton())

class Teste(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='form')
    async def form(self, ctx):
        view = FormView()
        await ctx.send("Clique no botão abaixo para abrir o formulário:", view=view)

def setup(bot):
    bot.add_cog(Teste(bot))
