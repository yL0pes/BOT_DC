import nextcord
from nextcord.ext import commands, tasks
from datetime import datetime, timedelta

ADV_ROLES = [
    1338523435902439524,  # ADV VERBAL
    1338523438742110258,  # ADV 1
    1338523454525407322   # ADV 2
]

ADV_CHANNEL_ID = 1337181666463977532
EXONERATION_CHANNEL_ID = 1337181666980134963
AUTHORIZED_ROLE_ID = 1338567039626772551

class AdvCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.adv_expirations = {}
        self.check_expirations.start()

    @commands.command(name="adv")
    @commands.has_role(AUTHORIZED_ROLE_ID)
    async def adv(self, ctx, member: nextcord.Member, days: int, *, reason: str):
        adv_channel = self.bot.get_channel(ADV_CHANNEL_ID)
        current_adv_roles = [role for role in member.roles if role.id in ADV_ROLES]

        if len(current_adv_roles) >= 3:
            await member.kick(reason="Recebeu 4 advertências")
            embed = nextcord.Embed(
                title="🚫 Usuário Expulso",
                description=f"**Nome:** {member.mention}\n**ID:** {member.id}\n**Motivo Exoneração:** Recebeu 4 advertências\n**Quem aplicou:** {ctx.author.mention}",
                color=nextcord.Color.red()
            )
            await adv_channel.send(embed=embed)
            return

        next_adv_role = ADV_ROLES[len(current_adv_roles)]
        await member.add_roles(nextcord.Object(id=next_adv_role))

        expiration_date = datetime.now() + timedelta(days=days)
        self.adv_expirations[member.id] = (next_adv_role, expiration_date)

        embed = nextcord.Embed(
            title="⚠️ Advertência Aplicada",
            description=f"**Nome:** {member.mention}\n**ID:** {member.id}\n**Motivo ADV:** {reason}\n**ADV:** {len(current_adv_roles) + 1}\n**Tempo restante para fim da Advertencia:** {days} dias\n**Quem aplicou:** {ctx.author.mention}",
            color=nextcord.Color.orange()
        )
        await adv_channel.send(embed=embed)

    @commands.command(name="exonerar")
    @commands.has_role(AUTHORIZED_ROLE_ID)
    async def exonerar(self, ctx, member: nextcord.Member, *, reason: str):
        exoneration_channel = self.bot.get_channel(EXONERATION_CHANNEL_ID)
        await member.kick(reason=reason)

        embed = nextcord.Embed(
            title="🚫 Usuário Expulso",
            description=f"**Nome:** {member.mention}\n**ID:** {member.id}\n**Motivo Exoneração:** {reason}\n**Quem aplicou:** {ctx.author.mention}",
            color=nextcord.Color.red()
        )
        await exoneration_channel.send(embed=embed)

    @commands.command(name="readv")
    @commands.has_role(AUTHORIZED_ROLE_ID)
    async def readv(self, ctx, member: nextcord.Member):
        adv_channel = self.bot.get_channel(ADV_CHANNEL_ID)
        current_adv_roles = [role for role in member.roles if role.id in ADV_ROLES]

        if not current_adv_roles:
            await ctx.send(f"{member.mention} não possui advertências.")
            return

        last_adv_role = current_adv_roles[-1]
        await member.remove_roles(last_adv_role)

        embed = nextcord.Embed(
            title="✅ Advertência Revogada",
            description=f"**Nome:** {member.mention}\n**ID:** {member.id}\n**Advertência Revogada:** {last_adv_role.name}\n**Quem revogou:** {ctx.author.mention}",
            color=nextcord.Color.green()
        )
        await adv_channel.send(embed=embed)

    @tasks.loop(minutes=1)
    async def check_expirations(self):
        now = datetime.now()
        adv_channel = self.bot.get_channel(ADV_CHANNEL_ID)
        for member_id, (role_id, expiration_date) in list(self.adv_expirations.items()):
            if now >= expiration_date:
                member = self.bot.get_user(member_id)
                role = nextcord.Object(id=role_id)
                await member.remove_roles(role)

                embed = nextcord.Embed(
                    title="⏰ Advertência Expirada",
                    description=f"**Nome:** {member.mention}\n**ID:** {member.id}\n**Advertência Expirada:** {role.name}",
                    color=nextcord.Color.green()
                )
                await adv_channel.send(embed=embed)
                del self.adv_expirations[member_id]

    @check_expirations.before_loop
    async def before_check_expirations(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(AdvCog(bot))
