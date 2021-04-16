import discord


def build_embed_groups(embed: discord.Embed, groups: dict, inline: bool = True):
    for key in groups.keys():
        start = 0
        curr_length = 0
        curr_field = 1

        char_count = sum(len(groups[key][i]) + 1 for i in range(len(groups[key])))
        max_chars = char_count // ((char_count // 1024) + 1)

        for i in range(len(groups[key])):
            curr_length += len(groups[key][i]) + 1

            if i < len(groups[key]) - 1:
                next_length = curr_length + len(groups[key][i + 1])

            if i == len(groups[key]) - 1 or next_length >= 1024 or curr_length > max_chars:
                field_name = key
                embed.add_field(name=field_name, value=('\n'.join(groups[key][start:i + 1])), inline=inline)
                start = i + 1
                curr_length = 0
                curr_field += 1
