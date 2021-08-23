from discord.ext import commands
from discord_slash.context import ComponentContext

from helpers import role_helper


class RoleButtonHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        component_elements = ctx.component_id.split('_')
        if len(component_elements) == 2:
            component_type, component_data = component_elements
        else:
            component_type = component_data = None

        if component_type == 'role':
            uni, programme, student_type = component_data.split('-')
            to_add = []
            to_remove = []
            user_roles = set(ctx.author.roles)

            if student_type == 'stud':
                role_helper.process_role_assignment_student(programme, uni, user_roles, ctx.guild.roles,
                                                            to_add, to_remove)

            message = str()
            if len(to_add) > 0:
                message += f'Added {"roles" if len(to_add) > 1 else "role"}: ' \
                           f'_{", ".join(r.name for r in to_add)}_\n'
                await ctx.author.add_roles(*to_add, reason=ctx.component_id)
            if len(to_remove) > 0:
                message += f'Removed {"roles" if len(to_remove) > 1 else "role"}: ' \
                           f'_{", ".join(r.name for r in to_remove)}_\n'
                await ctx.author.remove_roles(*to_remove, reason=ctx.component_id)
            if len(to_add) == 0 and len(to_remove) == 0:
                message = 'You already have the chosen roles'
            await ctx.send(message, hidden=True)
        else:
            await ctx.send('An unexpected error occurred, please try again later', hidden=True)
            print('Unexpected component id: ' + ctx.component_id)


def setup(bot):
    bot.add_cog(RoleButtonHandler(bot))
