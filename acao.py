from nextcord.ext import commands
import nextcord

class Acoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def acao(self, ctx):
        role_id = 1323359921093345318  # Substitua pelo ID do cargo específico
        if role_id not in [role.id for role in ctx.author.roles]:
            await ctx.send("Você não tem permissão para usar este comando.")
            return

        embed = nextcord.Embed(
            title="REGISTRO DE AÇÕES DO EXÉRCITO BRASILEIRO",
            description=" - Lembre-se de utilizar apenas números para informar a quantidade de membros e o horário da ação. Unidos pela missão, prontos para a vitória!",
            color=nextcord.Color.blue()
        )
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")

        button = nextcord.ui.Button(label="REGISTRAR AÇÃO", style=nextcord.ButtonStyle.primary)

        async def button_callback(interaction):
            if role_id not in [role.id for role in interaction.user.roles]:
                await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)
                return

            class RegistrarAcaoModal(nextcord.ui.Modal):
                def __init__(self, bot):
                    super().__init__(title="Registrar Ação")
                    self.bot = bot

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
                        color=nextcord.Color.dark_gray()
                    )
                    embed.add_field(name="👮‍♂️ QUANTIDADE DE POLICIAS", value=self.qtd_policias.value, inline=True)
                    embed.add_field(name="⛔ NOME DA FACÇÃO", value=self.nome_faccao.value, inline=True)
                    embed.add_field(name="⏲ HORÁRIO DA AÇÃO", value=self.horario_acao.value, inline=True)

                    marcar_presenca_button = nextcord.ui.Button(label="MARCAR PRESENÇA", style=nextcord.ButtonStyle.success)
                    retirar_presenca_button = nextcord.ui.Button(label="RETIRAR PRESENÇA", style=nextcord.ButtonStyle.danger)
                    fechar_inscricao_button = nextcord.ui.Button(label="FECHAR INSCRIÇÃO", style=nextcord.ButtonStyle.secondary)

                    async def marcar_presenca_callback(interaction):
                        user = interaction.user
                        presenca = f"{user.display_name} ({user.id}) 💎"
                        if embed.fields[-1].name == "📋 PRESENÇAS":
                            if presenca not in embed.fields[-1].value:
                                embed.set_field_at(index=len(embed.fields) - 1, name="📋 PRESENÇAS", value=embed.fields[-1].value + "\n" + presenca, inline=False)
                        else:
                            embed.add_field(name="📋 PRESENÇAS", value=presenca, inline=False)
                        await interaction.response.edit_message(embed=embed, view=view)

                    async def retirar_presenca_callback(interaction):
                        user = interaction.user
                        presenca = f"{user.display_name} ({user.id}) 💎"
                        if embed.fields[-1].name == "📋 PRESENÇAS":
                            novas_presencas = "\n".join([p for p in embed.fields[-1].value.split("\n") if p != presenca])
                            embed.set_field_at(index=len(embed.fields) - 1, name="📋 PRESENÇAS", value=novas_presencas, inline=False)
                        await interaction.response.edit_message(embed=embed, view=view)

                    async def fechar_inscricao_callback(interaction):
                        if role_id not in [role.id for role in interaction.user.roles]:
                            await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)
                            return
                        fechar_inscricao_button.disabled = True
                        fechar_inscricao_button.label = "AÇÃO FINALIZADA"
                        view.clear_items()
                        view.add_item(fechar_inscricao_button)

                        vitoria_button = nextcord.ui.Button(label="💚 VITÓRIA", style=nextcord.ButtonStyle.success)
                        derrota_button = nextcord.ui.Button(label="💥 DERROTA", style=nextcord.ButtonStyle.danger)

                        async def vitoria_callback(interaction):
                            if role_id not in [role.id for role in interaction.user.roles]:
                                await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)
                                return
                            vitoria_button.disabled = True
                            view.clear_items()
                            view.add_item(fechar_inscricao_button)
                            view.add_item(vitoria_button)
                            embed.color = nextcord.Color.green()
                            if embed.fields[-1].name == "STATUS":
                                embed.set_field_at(index=len(embed.fields) - 1, name="STATUS", value="AÇÃO GANHA", inline=False)
                            else:
                                embed.add_field(name="🌐 STATUS", value="AÇÃO GANHA", inline=False)
                            await interaction.response.edit_message(embed=embed, view=view)

                        async def derrota_callback(interaction):
                            if role_id not in [role.id for role in interaction.user.roles]:
                                await interaction.response.send_message("Você não tem permissão para usar este botão.", ephemeral=True)
                                return
                            derrota_button.disabled = True
                            view.clear_items()
                            view.add_item(fechar_inscricao_button)
                            view.add_item(derrota_button)
                            embed.color = nextcord.Color.red()
                            if embed.fields[-1].name == "STATUS":
                                embed.set_field_at(index=len(embed.fields) - 1, name="STATUS", value="AÇÃO PERDIDA", inline=False)
                            else:
                                embed.add_field(name="STATUS", value="AÇÃO PERDIDA", inline=False)
                            await interaction.response.edit_message(embed=embed, view=view)

                        vitoria_button.callback = vitoria_callback
                        derrota_button.callback = derrota_callback

                        view.add_item(vitoria_button)
                        view.add_item(derrota_button)

                        await interaction.response.edit_message(view=view)

                    marcar_presenca_button.callback = marcar_presenca_callback
                    retirar_presenca_button.callback = retirar_presenca_callback
                    fechar_inscricao_button.callback = fechar_inscricao_callback

                    view = nextcord.ui.View(timeout=None)  # Set timeout to None to keep the view active indefinitely
                    view.add_item(marcar_presenca_button)
                    view.add_item(retirar_presenca_button)
                    view.add_item(fechar_inscricao_button)

                    canal_id = 1323359925681913981  # Substitua pelo ID do canal específico
                    canal = self.bot.get_channel(canal_id)
                    if canal is not None:
                        await canal.send(embed=embed, view=view)
                    else:
                        await interaction.response.send_message("Canal não encontrado.", ephemeral=True)

            modal = RegistrarAcaoModal(self.bot)
            await interaction.response.send_modal(modal)

        button.callback = button_callback

        view = nextcord.ui.View(timeout=None)  # Set timeout to None to keep the view active indefinitely
        view.add_item(button)

        await ctx.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Acoes(bot))