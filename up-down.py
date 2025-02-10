import mysql.connector
import nextcord
from nextcord.ext import commands
from nextcord import Embed
import asyncio
from config import DIVISION_SPECIFIC_ROLES, ROLE_ABBREVIATIONS

SPECIFIC_ROLE_ID = 1338567039626772551  # ID do cargo específico que pode usar os comandos
UP_CHANNEL_ID = 1337181666463977529  # Canal para envio da embed de upamento
RBX_CHANNEL_ID = 1337181666463977531  # Canal para envio da embed de rebaixamento

class UpDownCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(SPECIFIC_ROLE_ID)
    async def up(self, ctx, member: nextcord.Member, *, reason: str):
        await self.change_role(ctx, member, reason, "up")
        await asyncio.sleep(2)
        await ctx.message.delete()

    @commands.command()
    @commands.has_role(SPECIFIC_ROLE_ID)
    async def rbx(self, ctx, member: nextcord.Member, *, reason: str):
        await self.change_role(ctx, member, reason, "rbx")
        await asyncio.sleep(2)
        await ctx.message.delete()

    @up.error
    @rbx.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.author.send("Você não tem permissão para usar este comando.")

    async def change_role(self, ctx, member, reason, action):
        current_role = self.get_current_role(member)
        new_role = self.get_new_role(ctx.guild, current_role, action)

        if not new_role:
            await ctx.send("Não foi possível encontrar o novo cargo.")
            return

        await member.add_roles(new_role)
        await member.remove_roles(current_role)

        await self.update_nickname(member, new_role)

        embed = self.create_embed(ctx, member, current_role, new_role, reason, action)
        channel_id = UP_CHANNEL_ID if action == "up" else RBX_CHANNEL_ID
        channel = self.bot.get_channel(channel_id)
        await channel.send(embed=embed)

    def get_current_role(self, member):
        for division_roles in DIVISION_SPECIFIC_ROLES.values():
            for role_id in division_roles.values():
                role = member.guild.get_role(role_id)
                if role in member.roles:
                    return role
        return None

    def get_new_role(self, guild, current_role, action):
        for division, roles in DIVISION_SPECIFIC_ROLES.items():
            if current_role.id in roles.values():
                role_ids = list(roles.values())
                current_index = role_ids.index(current_role.id)
                new_index = current_index + 1 if action == "up" else current_index - 1
                if 0 <= new_index < len(role_ids):
                    new_role_id = role_ids[new_index]
                    return guild.get_role(new_role_id)
        return None

    async def update_nickname(self, member, new_role):
        division = next((div for div, roles in DIVISION_SPECIFIC_ROLES.items() if new_role.id in roles.values()), None)
        role_abbreviation = ROLE_ABBREVIATIONS.get(new_role.name, new_role.name)
        db_connection = connect_db()
        cursor = db_connection.cursor()
        cursor.execute("SELECT user_id FROM user_ids WHERE discord_id = %s", (member.id,))
        result = cursor.fetchone()
        cursor.close()
        db_connection.close()
        user_id_from_db = result[0] if result else member.id
        old_nickname = member.display_name
        if old_nickname.startswith("["):
            old_nickname = old_nickname.split("] ", 1)[-1]
        if "|" in old_nickname:
            old_nickname = old_nickname.split(" | ")[0]
        new_nickname = f"[{role_abbreviation}-{division}] {old_nickname} | {user_id_from_db}"
        if len(new_nickname) > 32:
            new_nickname = new_nickname[:32]
        await member.edit(nick=new_nickname)

    def create_embed(self, ctx, member, old_role, new_role, reason, action):
        embed = Embed(
            title="📈 Upamento" if action == "up" else "📉 Rebaixamento",
            description=(
                f"👤 **Usuário:** {member.mention}\n"
                f"🆔 **ID:** {member.id}\n"
                f"📜 **Cargo Antigo:** {old_role.mention}\n"
                f"📜 **Cargo Atual:** {new_role.mention}\n"
                f"📝 **Motivo:** {reason}\n"
                f"🔒 **Autorizado por:** {ctx.author.mention}\n"
                f"📅 **Data:** {nextcord.utils.utcnow().strftime('%d/%m/%Y %H:%M:%S')}"
            ),
            color=nextcord.Color.green() if action == "up" else nextcord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        return embed

def connect_db():
    return mysql.connector.connect(
        host='172.93.104.61',
        user='u661_rRiE9itGnx',
        password='BgxrDebZCN0Uy!MBjd^1J!Wu',
        database='s661_cadastro_divisao'
    )

def setup(bot):
    bot.add_cog(UpDownCog(bot))
