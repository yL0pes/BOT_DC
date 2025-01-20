from nextcord.ext import commands
import nextcord

class Curso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cursos')
    async def cursos(self, ctx):
        await ctx.send("Aqui estão os cursos disponíveis: Curso 1, Curso 2, Curso 3")

def setup(bot):
    bot.add_cog(Curso(bot))