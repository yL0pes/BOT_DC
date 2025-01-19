from nextcord.ext import commands
import nextcord

class Acoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def acao(self, ctx):
        embed = nextcord.Embed(
            title="Título da Ação",
            description="Descrição da ação.",
            color=nextcord.Color.blue()
        )
        embed.set_footer(text="Footer da embed")

        button = nextcord.ui.Button(label="REGISTRAR AÇÃO", style=nextcord.ButtonStyle.primary)

        async def button_callback(interaction):
            class RegistrarAcaoModal(nextcord.ui.Modal):
                def __init__(self):
                    super().__init__(title="Registrar Ação")

                    self.nome_acao = nextcord.ui.TextInput(label="NOME DA AÇÃO")
                    self.qtd_policias = nextcord.ui.TextInput(label="QUANTIDADE DE POLICIAS")
                    self.nome_faccao = nextcord.ui.TextInput(label="NOME DA FACÇÃO")
                    self.horario_acao = nextcord.ui.TextInput(label="HORÁRIO DA AÇÃO")

                    self.add_item(self.nome_acao)
                    self.add_item(self.qtd_policias)
                    self.add_item(self.nome_faccao)
                    self.add_item(self.horario_acao)

                async def callback(self, interaction: nextcord.Interaction):
                    embed = nextcord.Embed(
                        title=self.nome_acao.value,
                        description=f"**Quantidade de Policiais:** {self.qtd_policias.value}\n"
                                    f"**Nome da Facção:** {self.nome_faccao.value}\n"
                                    f"**Horário da Ação:** {self.horario_acao.value}",
                        color=nextcord.Color.dark_gray()
                    )

                    marcar_presenca_button = nextcord.ui.Button(label="MARCAR PRESENÇA", style=nextcord.ButtonStyle.success)

                    view = nextcord.ui.View()
                    view.add_item(marcar_presenca_button)

                    await interaction.response.send_message(embed=embed, view=view)

            modal = RegistrarAcaoModal()
            await interaction.response.send_modal(modal)

        button.callback = button_callback

        view = nextcord.ui.View()
        view.add_item(button)

        await ctx.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Acoes(bot))