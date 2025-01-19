from nextcord.ext import commands
from nextcord import Embed, ButtonStyle, Interaction, SelectOption
from nextcord.ui import Button, View, Modal, TextInput, Select

class Aulas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="aulas")
    async def aulas(self, ctx):
        embed = Embed(title="Solicitação de Aula", description="Selecione o curso abaixo para solicitar uma aula.")
        select = Select(
            placeholder="Selecione o curso",
            options=[
                SelectOption(label=f"Curso {i+1}", value=str(id), description=f"ID do cargo: {id}") for i, id in enumerate([
                    1323359920338505825, 234567890123456789, 345678901234567890, 456789012345678901, 567890123456789012,
                    678901234567890123, 789012345678901234, 890123456789012345, 901234567890123456, 112345678901234567,
                    122345678901234567, 132345678901234567, 142345678901234567, 152345678901234567, 162345678901234567,
                    172345678901234567, 182345678901234567, 192345678901234567, 202345678901234567, 212345678901234567,
                    222345678901234567, 232345678901234567, 242345678901234567, 252345678901234567, 262345678901234567
                ])
            ]
        )

        async def select_callback(interaction: Interaction):
            selected_option = select.values[0]
            modal = SolicitarAulaModal(selected_option, select.options)
            await interaction.response.send_modal(modal)

        select.callback = select_callback
        view = View()
        view.add_item(select)

        # Enviar a mensagem
        await ctx.send(embed=embed, view=view)

class SolicitarAulaModal(Modal):
    def __init__(self, selected_option, options):
        super().__init__(title="Formulário de Solicitação de Aula")
        self.selected_option = selected_option
        self.options = options

        self.add_item(TextInput(label="Data", placeholder="Digite a data (DD/MM/AAAA)"))
        self.add_item(TextInput(label="Horário Disponível", placeholder="Digite o horário disponível"))

    async def callback(self, interaction: Interaction):
        data = self.children[0].value
        horario = self.children[1].value

        # Formatar o horário para HH:MM
        horario_formatado = f"{horario[:2]}:{horario[2:]}"

        # Encontrar o ID do cargo selecionado
        selected_id = self.selected_option

        response = f"Solicitação recebida!\n\nCurso: {self.selected_option}\nData: {data}\nHorário Disponível: {horario_formatado}"
        await interaction.response.send_message(response, ephemeral=True)

        # Enviar uma nova embed no chat com as informações coletadas
        embed = Embed(title="Nova Solicitação de Aula", description=f"Data: {data}\nHorário Disponível: {horario_formatado}")
        embed.add_field(name="Curso", value=f"<@&{selected_id}>", inline=False)
        embed.add_field(name="Data", value=data, inline=False)
        embed.add_field(name="Horário Disponível", value=horario_formatado, inline=False)

        # Adicionar botão ACEITAR AULA
        button_aceitar = Button(label="ACEITAR AULA", style=ButtonStyle.success)

        async def button_aceitar_callback(interaction: Interaction):
            user = interaction.user
            instrutor_responsavel = f"{user.display_name} 🎓"
            await interaction.response.send_message("Você aceitou a aula!", ephemeral=True)

            # Atualizar a embed com a informação do instrutor responsável
            embed.add_field(name="Instrutor Responsável", value=instrutor_responsavel, inline=False)

            # Adicionar botão MARCAR PRESENÇA
            button_presenca = Button(label="MARCAR PRESENÇA", style=ButtonStyle.primary)

            async def button_presenca_callback(interaction: Interaction):
                aluno = f"<@{interaction.user.id}> 🎓"
                # Verificar se o campo "Alunos" já existe
                for field in embed.fields:
                    if field.name == "Alunos":
                        if aluno not in field.value:
                            field.value += f"\n{aluno}"
                        break
                else:
                    embed.add_field(name="Alunos", value=aluno, inline=False)
                await interaction.response.send_message("Presença marcada!", ephemeral=True)
                await interaction.message.edit(embed=embed, view=view)

            button_presenca.callback = button_presenca_callback

            # Adicionar botão RETIRAR PRESENÇA
            button_retirar_presenca = Button(label="RETIRAR PRESENÇA", style=ButtonStyle.danger)

            async def button_retirar_presenca_callback(interaction: Interaction):
                aluno = f"<@{interaction.user.id}> 🎓"
                # Remover o aluno da lista de alunos na embed
                for field in embed.fields:
                    if field.name == "Alunos" and aluno in field.value:
                        field.value = field.value.replace(f"\n{aluno}", "").strip()
                        if not field.value:
                            embed.remove_field(embed.fields.index(field))
                        break
                await interaction.response.send_message("Presença retirada!", ephemeral=True)
                await interaction.message.edit(embed=embed, view=view)

            button_retirar_presenca.callback = button_retirar_presenca_callback

            # Adicionar botão FINALIZAR AULA
            button_finalizar_aula = Button(label="FINALIZAR AULA", style=ButtonStyle.danger)

            async def button_finalizar_aula_callback(interaction: Interaction):
                button_finalizar_aula.label = "AULA FINALIZADA"
                button_finalizar_aula.disabled = True
                view.clear_items()
                view.add_item(button_finalizar_aula)
                await interaction.response.send_message("Aula finalizada!", ephemeral=True)
                await interaction.message.edit(embed=embed, view=view)

                # Adicionar o cargo a todos os alunos marcados
                guild = interaction.guild
                role = guild.get_role(int(selected_id))
                for field in embed.fields:
                    if field.name == "Alunos":
                        alunos = field.value.split("\n")
                        for aluno in alunos:
                            member_id = int(aluno.split(" ")[0].strip("<@!>"))
                            member = guild.get_member(member_id)
                            if member:
                                await member.add_roles(role)

            button_finalizar_aula.callback = button_finalizar_aula_callback

            view.clear_items()
            view.add_item(button_presenca)
            view.add_item(button_retirar_presenca)
            view.add_item(button_finalizar_aula)
            await interaction.message.edit(embed=embed, view=view)

        button_aceitar.callback = button_aceitar_callback
        view = View()
        view.add_item(button_aceitar)

        # Enviar a embed no canal específico e marcar o cargo
        channel_id = 1323359923131781213  # Substitua YOUR_CHANNEL_ID pelo ID do canal desejado
        channel = interaction.guild.get_channel(channel_id)
        await channel.send(content=f"<@&{selected_id}>", embed=embed, view=view)

def setup(bot):
    bot.add_cog(Aulas(bot))