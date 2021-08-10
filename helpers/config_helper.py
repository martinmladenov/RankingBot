import os
import re


def get_guild_ids():
    if os.getenv('DEBUG_SERVER_IDS') is None:
        return None
    else:
        if len(re.findall(r"\d+", os.environ['DEBUG_SERVER_IDS'])) == 0:
            return None
        else:
            return re.findall(r"\d+", os.environ['DEBUG_SERVER_IDS'])
