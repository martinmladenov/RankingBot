import discord


def build_embed_groups(embed: discord.Embed, groups: dict, inline: bool = True):
    for key in groups.keys():
        start = 0
        curr_length = 0
        curr_field = 1

        for i in range(len(groups[key])):
            curr_length += len(groups[key][i]) + 1

            if i == len(groups[key]) - 1 or curr_length + len(groups[key][i + 1]) >= 1024:
                field_name = key
                embed.add_field(name=field_name, value=('\n'.join(groups[key][start:i + 1])), inline=inline)
                start = i + 1
                curr_length = 0
                curr_field += 1
