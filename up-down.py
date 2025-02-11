import nextcord
from nextcord.ext import commands
from config import DIVISION_ROLES, ROLE_ABBREVIATIONS, DIVISION_SPECIFIC_ROLES
import mysql.connector

AUTHORIZED_ROLE_ID = 1338650814545137774  # Substitua pelo ID do cargo autorizado

class UpDownCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="up")
    async def up(self, ctx, member: nextcord.Member, *, reason: str = None):
        # Verificar se o usuário que executou o comando tem o cargo autorizado
        if AUTHORIZED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            await ctx.message.delete()
            await ctx.send("Você não tem permissão para usar este comando.", delete_after=5)
            return

        # Verificar se o comando foi digitado corretamente
        if not member or not reason:
            await ctx.message.delete()
            await ctx.send("Comando incorreto. Use: !up @usuario Motivo", delete_after=5)
            return

        division = self.get_division(member)
        if division == "Nenhuma":
            await ctx.send("Divisão não encontrada para o usuário.")
            return

        old_role = self.get_old_role(member)
        if old_role == "Nenhum":
            await ctx.send("Cargo antigo não encontrado para o usuário.")
            return

        new_role_name = self.get_next_role(old_role, division)
        new_role = ctx.guild.get_role(DIVISION_SPECIFIC_ROLES[division][new_role_name])
        if new_role:
            await member.remove_roles(ctx.guild.get_role(DIVISION_SPECIFIC_ROLES[division][old_role]))
            await member.add_roles(new_role)
            await ctx.send(f"{member.mention} foi upado com sucesso!")
            await self.send_embed(ctx, member, "upado", reason, old_role, new_role_name)
        else:
            await ctx.send(f"Cargo '{new_role_name}' não encontrado.")

    @commands.command(name="rbx")
    async def rbx(self, ctx, member: nextcord.Member, *, reason: str = None):
        # Verificar se o usuário que executou o comando tem o cargo autorizado
        if AUTHORIZED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            await ctx.message.delete()
            await ctx.send("Você não tem permissão para usar este comando.", delete_after=5)
            return

        # Verificar se o comando foi digitado corretamente
        if not member or not reason:
            await ctx.message.delete()
            await ctx.send("Comando incorreto. Use: !rbx @usuario Motivo", delete_after=5)
            return

        division = self.get_division(member)
        if division == "Nenhuma":
            await ctx.send("Divisão não encontrada para o usuário.")
            return

        old_role = self.get_old_role(member)
        if old_role == "Nenhum":
            await ctx.send("Cargo antigo não encontrado para o usuário.")
            return

        new_role_name = self.get_previous_role(old_role, division)
        new_role = ctx.guild.get_role(DIVISION_SPECIFIC_ROLES[division][new_role_name])
        if new_role:
            await member.remove_roles(ctx.guild.get_role(DIVISION_SPECIFIC_ROLES[division][old_role]))
            await member.add_roles(new_role)
            await ctx.send(f"{member.mention} foi rebaixado com sucesso!")
            await self.send_embed(ctx, member, "rebaixado", reason, old_role, new_role_name)
        else:
            await ctx.send(f"Cargo '{new_role_name}' não encontrado.")

    async def send_embed(self, ctx, member, action, reason, old_role, new_role):
        division = self.get_division(member)
        channel_id = 1315845308894281839 if action == "upado" else 1315845427706204261
        channel = ctx.guild.get_channel(channel_id)

        embed = nextcord.Embed(
            title=f"📋 {action.capitalize()}",
            color=nextcord.Color.green() if action == "upado" else nextcord.Color.red()
        )
        embed.add_field(name="👤 Nome:", value=member.display_name, inline=True)
        embed.add_field(name="🆔 ID:", value=member.id, inline=True)
        embed.add_field(name="📌 Cargo Antigo:", value=old_role, inline=True)
        embed.add_field(name="📌 Cargo Atual:", value=new_role, inline=True)
        embed.add_field(name="👮 Autorizado por:", value=ctx.author.display_name, inline=True)
        embed.add_field(name="📅 Data:", value=nextcord.utils.utcnow().strftime('%d/%m/%Y'), inline=True)
        embed.add_field(name="⏰ Hora:", value=nextcord.utils.utcnow().strftime('%H:%M:%S'), inline=True)
        embed.add_field(name="📝 Motivo:", value=reason, inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="Criado por - 𝓛𝓸𝓹𝓮𝓼")

        await channel.send(embed=embed)
        await self.update_nickname(member, new_role, division)

    def get_division(self, member):
        for div, role_id in DIVISION_ROLES.items():
            if member.guild.get_role(role_id) in member.roles:
                return div
        return "Nenhuma"

    def get_old_role(self, member):
        for div_roles in DIVISION_SPECIFIC_ROLES.values():
            for role_name, role_id in div_roles.items():
                if member.guild.get_role(role_id) in member.roles:
                    return role_name
        return "Nenhum"

    def get_next_role(self, current_role, division):
        roles = list(DIVISION_SPECIFIC_ROLES[division].keys())
        current_index = roles.index(current_role)
        return roles[current_index + 1] if current_index + 1 < len(roles) else current_role

    def get_previous_role(self, current_role, division):
        roles = list(DIVISION_SPECIFIC_ROLES[division].keys())
        current_index = roles.index(current_role)
        return roles[current_index - 1] if current_index - 1 >= 0 else current_role

    async def update_nickname(self, member, new_role, division):
        user_id_from_db = self.get_user_id_from_db(member.id)
        role_abbreviation = ROLE_ABBREVIATIONS.get(new_role, new_role)
        old_nickname = member.display_name
        if old_nickname.startswith("["):
            old_nickname = old_nickname.split("] ", 1)[-1]
        if "|" in old_nickname:
            old_nickname = old_nickname.split(" | ")[0]
        new_nickname = f"[{role_abbreviation}-{division}] {old_nickname} | {user_id_from_db}"
        if len(new_nickname) > 32:
            new_nickname = new_nickname[:32]
        await member.edit(nick=new_nickname)

    def get_user_id_from_db(self, discord_id):
        db_connection = mysql.connector.connect(
            host='172.93.104.61',
            user='u661_rRiE9itGnx',
            password='BgxrDebZCN0Uy!MBjd^1J!Wu',
            database='s661_cadastro_divisao'
        )
        cursor = db_connection.cursor()
        cursor.execute("SELECT user_id FROM user_ids WHERE discord_id = %s", (discord_id,))
        result = cursor.fetchone()
        cursor.close()
        db_connection.close()
        return result[0] if result else discord_id

def setup(bot):
    bot.add_cog(UpDownCog(bot))
