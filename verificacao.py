import mysql.connector
from mysql.connector import Error
from nextcord.ext import commands
import nextcord
import os
from dotenv import load_dotenv

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

class Verificacao(commands.Cog):
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
            CREATE TABLE IF NOT EXISTS verificacoes (
                user_id BIGINT PRIMARY KEY,
                id_digitado VARCHAR(255) NOT NULL
            )
        ''')
        self.conn.commit()

    @commands.command()
    async def verificacao(self, ctx):
        embed = nextcord.Embed(
            title="Verificação",
            description="Clique no botão abaixo para verificar seu ID.",
            color=nextcord.Color.green()
        )
        embed.set_footer(text="Criado por - 𝓛𝓸𝓮𝓼")
        button = nextcord.ui.Button(label="VERIFICAÇÃO", style=nextcord.ButtonStyle.green)
        button.callback = self.button_callback
        view = nextcord.ui.View(timeout=None)  # Definir timeout para None
        view.add_item(button)
        await ctx.send(embed=embed, view=view)

    async def button_callback(self, interaction):
        modal = nextcord.ui.Modal(
            title="Verificação de ID",
            custom_id="verificacao_modal"
        )
        modal.add_item(nextcord.ui.TextInput(
            label="Digite seu ID",
            custom_id="id_digitado",
            style=nextcord.TextInputStyle.short
        ))
        modal.callback = self.modal_callback
        await interaction.response.send_modal(modal)

    async def modal_callback(self, interaction):
        user_id = interaction.user.id
        id_digitado = interaction.data['components'][0]['components'][0]['value']
        
        # Verificar se o ID já está registrado
        self.cursor.execute('SELECT * FROM verificacoes WHERE user_id = %s', (user_id,))
        result = self.cursor.fetchone()
        if result:
            await interaction.response.send_message(f"Erro: O ID {id_digitado} já está registrado.", ephemeral=True)
        else:
            self.cursor.execute('REPLACE INTO verificacoes (user_id, id_digitado) VALUES (%s, %s)', (user_id, id_digitado))
            self.conn.commit()
            await interaction.response.send_message(f"ID {id_digitado} salvo com sucesso!", ephemeral=True)
            
            # Atribuir cargo específico ao usuário
            role_id = int(os.getenv('ROLE_VERIFICADO'))  # Adicione o ID do cargo específico no arquivo .env
            role = interaction.guild.get_role(role_id)
            if role:
                guild_member = await interaction.guild.fetch_member(user_id)
                await guild_member.add_roles(role)
                await interaction.followup.send(f"Você recebeu o cargo <@&{role_id}>.", ephemeral=True)
            else:
                await interaction.followup.send("Erro: Cargo não encontrado.", ephemeral=True)

def setup(bot):
    bot.add_cog(Verificacao(bot))
