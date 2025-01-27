import mysql.connector
from mysql.connector import Error
from nextcord.ext import commands

class Setagem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.conn = mysql.connector.connect(
                host='172.93.104.61',
                user='u661_s5CHL4GM9X',
                password='dc^g9UPViLsp^H+j.Ngdiq.k',
                database='s661_SETAGEM'
            )
            if self.conn.is_connected():
                print("Conectado ao banco de dados com sucesso")
            self.cursor = self.conn.cursor()
            self.create_table()
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def create_table(self):
        # Corrigir erro de sintaxe SQL
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                `key` VARCHAR(255) PRIMARY KEY,
                `value` TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    @commands.command()
    async def set(self, ctx, key: str = None, value: str = None):
        if key is None or value is None:
            await ctx.send("Erro: Ambos os argumentos 'key' e 'value' são obrigatórios.")
            return
        # Implementação do comando !set
        self.cursor.execute('REPLACE INTO settings (`key`, `value`) VALUES (%s, %s)', (key, value))
        self.conn.commit()
        await ctx.send(f'Configuração {key} definida para {value}')

def setup(bot):
    bot.add_cog(Setagem(bot))
