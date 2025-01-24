from nextcord.ext import commands
import nextcord
import asyncio
from datetime import datetime, timedelta
import aiohttp
import io  # Adicione esta linha para importar o módulo io

SPECIFIC_ROLE_ID = 1323359921114447887  # Substitua pelo ID do cargo específico
LOG_CHANNEL_ID = 1323359927166701622  # Substitua pelo ID do canal de logs

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
        embed.add_field(name="👮 QRA", value=self.qra.value, inline=False)
        embed.add_field(name="🪪 ID", value=self.id.value, inline=False)
        embed.add_field(name="⏲️ Tempo de Prova (Primeira Parte)", value=self.tempo_prova_1.value, inline=False)
        embed.add_field(name="⏲️ Tempo de Prova (Segunda Parte)", value=self.tempo_prova_2.value, inline=False)

        # Calcular a data de vencimento
        data_vencimento = datetime.now() + timedelta(days=30)
        data_vencimento_str = data_vencimento.strftime("%d/%m/%Y")
        embed.add_field(name="📝 DATA DE VENCIMENTO", value=data_vencimento_str, inline=False)

        await interaction.response.send_message("Por favor, envie a imagem agora.", ephemeral=True)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.attachments

        try:
            message = await interaction.client.wait_for('message', check=check, timeout=60.0)
            if message.attachments:
                attachment = message.attachments[0]
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status != 200:
                            await interaction.followup.send("Falha ao baixar a imagem.", ephemeral=True)
                            return
                        data = await resp.read()
                        file = nextcord.File(io.BytesIO(data), filename=attachment.filename)
                        embed.set_image(url=f"attachment://{attachment.filename}")
                        channel = interaction.guild.get_channel(self.channel_id)
                        await channel.send(embed=embed, file=file)
                        await message.delete()  # Excluir a mensagem do usuário após o envio
                        await interaction.followup.send("Imagem enviada com sucesso.", ephemeral=True)

                        # Enviar log para o canal de logs
                        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
                        if log_channel:
                            log_embed = nextcord.Embed(title="📜 Log de Envio de Imagem", color=0x00ff00)
                            log_embed.add_field(name="👤 Usuário", value=interaction.user.mention, inline=False)
                            log_embed.add_field(name="📅 Data de Envio", value=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), inline=False)
                            log_embed.add_field(name="📄 QRA", value=self.qra.value, inline=False)
                            log_embed.add_field(name="🪪 ID", value=self.id.value, inline=False)
                            log_embed.add_field(name="⏲️ Tempo de Prova (Primeira Parte)", value=self.tempo_prova_1.value, inline=False)
                            log_embed.add_field(name="⏲️ Tempo de Prova (Segunda Parte)", value=self.tempo_prova_2.value, inline=False)
                            log_embed.add_field(name="📝 Data de Vencimento", value=data_vencimento_str, inline=False)
                            log_embed.set_image(url=f"attachment://{attachment.filename}")
                            await log_channel.send(embed=log_embed, file=file)
            else:
                await interaction.followup.send("Nenhuma imagem anexada.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("Tempo esgotado para enviar a imagem.", ephemeral=True)

class FormDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Carteira SPEED 🚔", value="speed"),
            nextcord.SelectOption(label="Carteira GTM 🏍️", value="gtm"),
            nextcord.SelectOption(label="Carteira ÁGUIA 🚁", value="aguia")
        ]
        super().__init__(placeholder="Escolha uma opção...", options=options)

    async def callback(self, interaction: nextcord.Interaction):
        if self.values[0] == "speed":
            modal = FormModal("Carteira SPEED", 1323359923559465088)  # Substitua pelo ID do canal SPEED
        elif self.values[0] == "gtm":
            modal = FormModal("Carteira GTM", 1323359923559465089)  # Substitua pelo ID do canal GTM
        else:
            modal = FormModal("Carteira ÁGUIA", 1332380388638724117)  # Substitua pelo ID do canal ÁGUIA
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
