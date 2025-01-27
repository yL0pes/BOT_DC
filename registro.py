import mysql.connector
from mysql.connector import Error
from nextcord.ext import commands
import nextcord
import os
from dotenv import load_dotenv

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

CARGO_IDS = [
    "1333469693180252185", "1333469693180252184", "1333469693159411740", "1333469693159411739", "1333469693121396885",
    "1333469693121396884", "1333469693121396877", "1333469693121396876", "1333469693083783282", "1333469693083783281",
    "1333469693041709151", "1333469693041709150", "1333469693029253147", "1333469693029253146"
]

class Registro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            if self.conn.is_connected():
                print("Conectado ao banco de dados com sucesso")
            self.cursor = self.conn.cursor()
            self.create_table()
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def create_table(self):
        # Criar tabela se não existir
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                user_id BIGINT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                divisao VARCHAR(255) NOT NULL
            )
        ''')
        self.conn.commit()

    @commands.command()
    async def registro(self, ctx):
        embed = nextcord.Embed(
            title="Registro de Usuário",
            description="Clique no botão abaixo para iniciar o registro.",
            color=nextcord.Color.blue()
        )
        button = nextcord.ui.Button(label="Registrar", style=nextcord.ButtonStyle.green)
        button.callback = self.button_callback
        view = nextcord.ui.View(timeout=None)  # Definir timeout para None
        view.add_item(button)
        await ctx.send(embed=embed, view=view)

    async def button_callback(self, interaction):
        user_id = interaction.user.id
        
        # Verificar se o usuário já está registrado
        self.cursor.execute('SELECT * FROM registros WHERE user_id = %s', (user_id,))
        result = self.cursor.fetchone()
        if result:
            await interaction.response.send_message("Erro: Você já está registrado.", ephemeral=True)
            return
        
        modal = nextcord.ui.Modal(
            title="Registro de Usuário",
            custom_id="registro_modal"
        )
        modal.add_item(nextcord.ui.TextInput(
            label="Digite seu Nome",
            custom_id="nome",
            style=nextcord.TextInputStyle.short
        ))
        modal.callback = self.modal_callback
        await interaction.response.send_modal(modal)

    async def modal_callback(self, interaction):
        user_id = interaction.user.id
        nome = interaction.data['components'][0]['components'][0]['value']
        print(f"Modal callback: user_id={user_id}, nome={nome}")
        
        # Enviar mensagem com dropdown para selecionar a divisão
        embed = nextcord.Embed(
            title="Escolha sua Divisão",
            description="Selecione sua divisão no dropdown abaixo.",
            color=nextcord.Color.blue()
        )
        select = nextcord.ui.Select(
            placeholder="Escolha sua Divisão",
            custom_id="divisao_select",
            options=[
                nextcord.SelectOption(label="CIGS", description="Centro de Instrução de Guerra na Selva", value=os.getenv('ROLE_CIGS')),
                nextcord.SelectOption(label="FAB", description="Força Áerea Brasileira", value=os.getenv('ROLE_FAB')),
                nextcord.SelectOption(label="CMDS", description="Batalhão dos Comandos", value=os.getenv('ROLE_CMDS')),
                nextcord.SelectOption(label="CIEX", description="Centro de Inteligência do Exército", value=os.getenv('ROLE_CIEX')),
                nextcord.SelectOption(label="BFE", description="Batalhão de Forças Especiais", value=os.getenv('ROLE_BFE')),
                nextcord.SelectOption(label="PE", description="Polícia do Exército", value=os.getenv('ROLE_PE')),
                nextcord.SelectOption(label="SPEED", description="Força Speed Tática", value=os.getenv('ROLE_SPEED')),
            ]
        )
        select.callback = lambda i: self.select_callback(i, nome, user_id)
        view = nextcord.ui.View(timeout=None)  # Definir timeout para None
        view.add_item(select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def select_callback(self, interaction, nome, user_id):
        divisao = interaction.data['values'][0]
        print(f"Select callback: user_id={user_id}, nome={nome}, divisao={divisao}")
        
        # Obter o ID digitado da base de dados
        self.cursor.execute('SELECT id_digitado FROM verificacoes WHERE user_id = %s', (user_id,))
        result = self.cursor.fetchone()
        if result:
            id_digitado = result[0]
        else:
            await interaction.response.send_message("Erro: ID não encontrado na base de dados. Por favor, verifique seu ID primeiro.", ephemeral=True)
            return
        
        # Obter o nome da label da seleção no dropdown
        divisao_label = next(option.label for option in interaction.message.components[0].children[0].options if option.value == divisao)
        print(f"Select callback: divisao_label={divisao_label}, id_digitado={id_digitado}")
        
        self.cursor.execute('REPLACE INTO registros (user_id, nome, divisao) VALUES (%s, %s, %s)', (user_id, nome, divisao_label))
        self.conn.commit()
        
        # Enviar embed ao canal de solicitações
        solicitacao_channel = interaction.guild.get_channel(int(os.getenv('SOLICITACAO_CHANNEL_ID')))
        solicitacao_embed = nextcord.Embed(
            title="Nova Solicitação de Registro",
            description=f"Usuário: <@{user_id}>\nNome: {nome}\nID Digitado: {id_digitado}\nDivisão: {divisao_label}\nCargo: <@&{divisao}>",
            color=nextcord.Color.green()
        )
        aceitar_button = nextcord.ui.Button(label="ACEITAR SOLICITAÇÃO", style=nextcord.ButtonStyle.green)
        aceitar_button.callback = self.aceitar_solicitacao_callback
        solicitacao_view = nextcord.ui.View(timeout=None)
        solicitacao_view.add_item(aceitar_button)
        await solicitacao_channel.send(embed=solicitacao_embed, view=solicitacao_view)
        
        await interaction.response.send_message("Sua solicitação foi enviada para aprovação.", ephemeral=True)

    async def aceitar_solicitacao_callback(self, interaction):
        print("Aceitar solicitação callback iniciado")
        
        # Verificar se o usuário tem permissão para aceitar a solicitação
        approver_role_id = int(os.getenv('ROLE_APPROVER'))
        if approver_role_id not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("Você não tem permissão para aceitar esta solicitação.", ephemeral=True)
            return
        
        # Obter o membro do guild pela menção na embed
        user_mention = interaction.message.embeds[0].description.split('\n')[0].split(': ')[1]
        user_id = int(user_mention.strip('<@!>'))
        print(f"Aceitar solicitação callback: user_mention={user_mention}, user_id={user_id}")
        
        guild_member = await interaction.guild.fetch_member(user_id)
        if guild_member is None:
            print(f"Erro: Usuário com ID '{user_id}' não encontrado.")
            await interaction.response.send_message(f"Erro: Usuário com ID '{user_id}' não encontrado.", ephemeral=True)
            return
        print(f"Guild member encontrado: {guild_member.name}")
        
        # Obter a divisão pela menção na embed
        divisao_label = interaction.message.embeds[0].description.split('\n')[3].split(': ')[1]
        print(f"Aceitar solicitação callback: divisao_label={divisao_label}")

        # Obter o cargo pela menção na embed
        role_mention = interaction.message.embeds[0].description.split('\n')[4].split(': ')[1]
        role_id = int(role_mention.strip('<@&>'))
        print(f"Aceitar solicitação callback: role_mention={role_mention}, role_id={role_id}")
        
        role = interaction.guild.get_role(role_id)
        if role is None:
            print(f"Erro: Cargo com ID '{role_id}' não encontrado.")
            await interaction.response.send_message(f"Erro: Cargo com ID '{role_id}' não encontrado.", ephemeral=True)
            return
        print(f"Role encontrado: {role.name}")
        
        # Obter nome e id_digitado da embed
        nome = interaction.message.embeds[0].description.split('\n')[1].split(': ')[1]
        id_digitado = interaction.message.embeds[0].description.split('\n')[2].split(': ')[1]
        print(f"Aceitar solicitação callback: nome={nome}, id_digitado={id_digitado}")
        
        # Atribuir o cargo ao usuário
        await guild_member.add_roles(role)
        print(f"Cargo {role.name} atribuído ao usuário {guild_member.name}")
        
        # Atribuir o cargo específico ao usuário
        role_membro_id = int(os.getenv('ROLE_MEMBRO'))
        role_membro = interaction.guild.get_role(role_membro_id)
        if role_membro:
            await guild_member.add_roles(role_membro)
            print(f"Cargo {role_membro.name} também atribuído ao usuário {guild_member.name}")
        
        # Alterar o apelido do usuário
        novo_apelido = f"[{divisao_label}] {nome} | {id_digitado}"
        if len(novo_apelido) > 32:
            # Truncar o nome e o ID digitado para caber no limite de 32 caracteres
            max_length = 32 - len(f"[{divisao_label}]  | ")
            truncated_nome = nome[:max_length // 2]
            truncated_id_digitado = str(id_digitado)[:max_length // 2]
            novo_apelido = f"[{divisao_label}] {truncated_nome} | {truncated_id_digitado}"
            if len(novo_apelido) > 32:
                novo_apelido = novo_apelido[:32]
        
        print(f"Tentando definir apelido: {novo_apelido}")
        try:
            # Verificar se o bot tem permissão para alterar o apelido e se o papel do bot está acima do papel do usuário
            bot_member = interaction.guild.get_member(interaction.client.user.id)
            if bot_member.top_role.position > guild_member.top_role.position:
                await guild_member.edit(nick=novo_apelido)
                await interaction.response.send_message(f"Registro completo! O novo apelido de <@{user_id}> é {novo_apelido}", ephemeral=True)
                print(f"Apelido alterado para: {novo_apelido}")
            else:
                await interaction.response.send_message("Erro: O bot não pode alterar o apelido de um usuário com um papel igual ou superior ao seu.", ephemeral=True)
                print("Erro: O bot não pode alterar o apelido de um usuário com um papel igual ou superior ao seu.")
        except nextcord.errors.Forbidden:
            await interaction.response.send_message("Erro: O bot não tem permissão para alterar o apelido.", ephemeral=True)
            print("Erro: O bot não tem permissão para alterar o apelido.")
        except nextcord.errors.HTTPException as e:
            await interaction.response.send_message(f"Erro ao alterar o apelido: {e}", ephemeral=True)
            print(f"Erro ao alterar o apelido: {e}")

    @commands.command(name='reset', aliases=['resetar'])
    async def reset(self, ctx, member: nextcord.Member):
        # Verificar se o usuário tem permissão para resetar os dados
        approver_role_id = int(os.getenv('ROLE_APPROVER'))
        if approver_role_id not in [role.id for role in ctx.author.roles]:
            await ctx.send("Você não tem permissão para resetar os dados deste usuário.")
            return
        
        user_id = member.id
        
        # Remover os dados do usuário da tabela de registros
        self.cursor.execute('DELETE FROM registros WHERE user_id = %s', (user_id,))
        self.conn.commit()
        
        # Remover o ID digitado da base de dados
        self.cursor.execute('DELETE FROM verificacoes WHERE user_id = %s', (user_id,))
        self.conn.commit()
        
        await ctx.send(f"Os dados de registro do usuário <@{user_id}> foram resetados. Ele pode realizar a verificação e o registro novamente.", delete_after=3)

    @commands.command()
    async def transfer(self, ctx):
        # Verificar se o usuário tem permissão para usar o comando de transferência
        allowed_roles = [int(role_id) for role_id in CARGO_IDS]
        if not any(role.id in allowed_roles for role in ctx.author.roles):
            await ctx.send("Você não tem permissão para usar este comando.")
            return

        embed = nextcord.Embed(
            title="Solicitação de Transferência",
            description="Selecione a divisão para a qual deseja ser transferido no dropdown abaixo.",
            color=nextcord.Color.blue()
        )
        select = nextcord.ui.Select(
            placeholder="Escolha sua nova Divisão",
            custom_id="transfer_select",
            options=[
                nextcord.SelectOption(label="CIGS", description="Centro de Instrução de Guerra na Selva", value=os.getenv('ROLE_CIGS')),
                nextcord.SelectOption(label="FAB", description="Força Áerea Brasileira", value=os.getenv('ROLE_FAB')),
                nextcord.SelectOption(label="CMDS", description="Batalhão dos Comandos", value=os.getenv('ROLE_CMDS')),
                nextcord.SelectOption(label="CIEX", description="Centro de Inteligência do Exército", value=os.getenv('ROLE_CIEX')),
                nextcord.SelectOption(label="BFE", description="Batalhão de Forças Especiais", value=os.getenv('ROLE_BFE')),
                nextcord.SelectOption(label="PE", description="Polícia do Exército", value=os.getenv('ROLE_PE')),
                nextcord.SelectOption(label="SPEED", description="Força Speed Tática", value=os.getenv('ROLE_SPEED')),
            ]
        )
        select.callback = self.transfer_callback
        view = nextcord.ui.View(timeout=None)  # Definir timeout para None
        view.add_item(select)
        await ctx.send(embed=embed, view=view)

    async def transfer_callback(self, interaction):
        user_id = interaction.user.id
        new_division = interaction.data['values'][0]
        print(f"Transfer callback: user_id={user_id}, new_division={new_division}")
        
        # Obter o nome da label da seleção no dropdown
        new_division_label = next(option.label for option in interaction.message.components[0].children[0].options if option.value == new_division)
        print(f"Transfer callback: new_division_label={new_division_label}")
        
        # Obter a divisão atual do usuário
        self.cursor.execute('SELECT divisao FROM registros WHERE user_id = %s', (user_id,))
        result = self.cursor.fetchone()
        if result:
            current_division_label = result[0]
        else:
            await interaction.response.send_message("Erro: Divisão atual não encontrada na base de dados.", ephemeral=True)
            return
        
        # Enviar embed ao canal de transferências
        transfer_channel = interaction.guild.get_channel(int(os.getenv('SOLICITACAO_CHANNEL_ID2')))
        transfer_embed = nextcord.Embed(
            title="Nova Solicitação de Transferência",
            description=f"Usuário: <@{interaction.user.id}>\nDivisão Atual: {current_division_label}\nNova Divisão: {new_division_label}\nCargo: <@&{new_division}>",
            color=nextcord.Color.orange()
        )
        accept_button = nextcord.ui.Button(label="ACEITAR TRANSFERÊNCIA", style=nextcord.ButtonStyle.green)
        accept_button.callback = lambda i: self.accept_transfer_callback(i, interaction.user.id, new_division, new_division_label)
        transfer_view = nextcord.ui.View(timeout=None)
        transfer_view.add_item(accept_button)
        await transfer_channel.send(embed=transfer_embed, view=transfer_view)
        
        await interaction.response.send_message("Sua solicitação de transferência foi enviada para aprovação.", ephemeral=True)

    async def accept_transfer_callback(self, interaction, user_id, new_division, new_division_label):
        print("Aceitar transferência callback iniciado")
        
        # Verificar se o usuário tem permissão para aceitar a transferência
        approver_roles = [int(role_id) for role_id in CARGO_IDS]
        if not any(role.id in approver_roles for role in interaction.user.roles):
            await interaction.response.send_message("SOMENTE COMANDO OU SUB COMANDO DA DIVISÃO PODE ACEITAR A TRANSFERÊNCIA", ephemeral=True)
            return
        
        # Obter o membro do guild pela menção na embed
        guild_member = await interaction.guild.fetch_member(user_id)
        if guild_member is None:
            print(f"Erro: Usuário com ID '{user_id}' não encontrado.")
            await interaction.response.send_message(f"Erro: Usuário com ID '{user_id}' não encontrado.", ephemeral=True)
            return
        print(f"Guild member encontrado: {guild_member.name}")
        
        # Obter o cargo pela menção na embed
        new_role = interaction.guild.get_role(int(new_division))
        if new_role is None:
            print(f"Erro: Cargo com ID '{new_division}' não encontrado.")
            await interaction.response.send_message(f"Erro: Cargo com ID '{new_division}' não encontrado.", ephemeral=True)
            return
        print(f"Role encontrado: {new_role.name}")
        
        # Remover todos os cargos antigos do usuário
        old_roles = [role for role in guild_member.roles if role.id in [int(os.getenv('ROLE_CIGS')), int(os.getenv('ROLE_FAB')), int(os.getenv('ROLE_CMDS')), int(os.getenv('ROLE_CIEX')), int(os.getenv('ROLE_BFE')), int(os.getenv('ROLE_PE')), int(os.getenv('ROLE_SPEED'))]]
        await guild_member.remove_roles(*old_roles)
        print(f"Cargos antigos removidos: {[role.name for role in old_roles]}")
        
        # Atribuir o novo cargo ao usuário
        await guild_member.add_roles(new_role)
        print(f"Cargo {new_role.name} atribuído ao usuário {guild_member.name}")
        
        # Alterar o apelido do usuário, removendo qualquer divisão antiga
        apelido_atual = guild_member.display_name
        novo_apelido = f"[{new_division_label}] {apelido_atual.split('] ')[-1]}"
        if len(novo_apelido) > 32:
            novo_apelido = novo_apelido[:32]
        
        print(f"Tentando definir apelido: {novo_apelido}")
        try:
            # Verificar se o bot tem permissão para alterar o apelido e se o papel do bot está acima do papel do usuário
            bot_member = interaction.guild.get_member(interaction.client.user.id)
            if bot_member.top_role.position > guild_member.top_role.position:
                await guild_member.edit(nick=novo_apelido)
                await interaction.response.send_message(f"Transferência completa! O novo apelido de <@{user_id}> é {novo_apelido}", ephemeral=True)
                print(f"Apelido alterado para: {novo_apelido}")
            else:
                await interaction.response.send_message("Erro: O bot não pode alterar o apelido de um usuário com um papel igual ou superior ao seu.", ephemeral=True)
                print("Erro: O bot não pode alterar o apelido de um usuário com um papel igual ou superior ao seu.")
        except nextcord.errors.Forbidden:
            await interaction.response.send_message("Erro: O bot não tem permissão para alterar o apelido.", ephemeral=True)
            print("Erro: O bot não tem permissão para alterar o apelido.")
        except nextcord.errors.HTTPException as e:
            await interaction.response.send_message(f"Erro ao alterar o apelido: {e}", ephemeral=True)
            print(f"Erro ao alterar o apelido: {e}")

def setup(bot):
    bot.add_cog(Registro(bot))
