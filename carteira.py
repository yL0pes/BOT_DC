from nextcord.ext import commands
import nextcord
import asyncio

SPECIFIC_ROLE_ID = 1323359921114447887  # Substitua pelo ID do cargo específico

class FormModal(nextcord.ui.Modal):
    def __init__(self, title, channel_id):
        super().__init__(title=title)
        self.channel_id = channel_id

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
        embed = nextcord.Embed(title=self.title, color=0x00ff00)
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
                channel = interaction.guild.get_channel(self.channel_id)
                await channel.send(embed=embed)
                await message.delete()  # Excluir a mensagem do usuário após o envio
            else:
                await interaction.followup.send("Nenhuma imagem anexada.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("Tempo esgotado para enviar a imagem.", ephemeral=True)

class FormDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Carteira SPEED", value="speed"),
            nextcord.SelectOption(label="Carteira GTM", value="gtm")
        ]
        super().__init__(placeholder="Escolha uma opção...", options=options)

    async def callback(self, interaction: nextcord.Interaction):
        if self.values[0] == "speed":
            modal = FormModal("Formulário de Carteira SPEED", 1323359923559465088)  # Substitua pelo ID do canal SPEED
        else:
            modal = FormModal("Formulário de Carteira GTM", 1323359923559465089)  # Substitua pelo ID do canal GTM
        await interaction.response.send_modal(modal)

class FormView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Defina o timeout como None para manter a View ativa indefinidamente
        self.add_item(FormDropdown())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class Teste(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='form')
    @commands.has_role(SPECIFIC_ROLE_ID)
    async def form(self, ctx):
        embed = nextcord.Embed(
            title="Escolha a carteira que quer enviar",
            description="Escolha uma das opções abaixo para abrir o formulário correspondente.",
            color=0x00ff00
        )
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")
        view = FormView()
        message = await ctx.send(embed=embed, view=view)
        view.message = message  # Salve a mensagem na View para poder editá-la mais tarde

    @form.error
    async def form_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("Você não tem permissão para usar este comando.", delete_after=5)

def setup(bot):
    bot.add_cog(Teste(bot))
