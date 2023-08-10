# Импорт конфигурационного файла, содержащего различные настройки
from config import *
from enum import Enum

import disnake
import datetime
from disnake.ext import commands

from datetime import datetime

# ssm = SteamStatManager(user_name, steamcommunity_link). <- Реализуй объект так

class Medals(Enum):
    WHITE = "<:2023_1:1128338078835159100>"
    GREEN = "<:2023_2:1128338080877785098>"
    BLUE = "<:2023_3:1128338084833009715>"
    PURPLE = "<:2023_4:1128338089471922268>"
    PINK = "<:2023_5:1128338093066424360>"
    RED = "<:2023_6:1128338143268044830>"

class SteamStatManager:

    def __init__(self, user_name: str, steamcommunity_link: str):
        self.__user_name = user_name
        self.__steamcommunity_link = steamcommunity_link

    @staticmethod
    def __get_lvl_emoji(lvl: int):
        lvls_dict = {
			
            1: "<:1rank:1128332539845689506>",
            2: "<:2rank:1128332542269984868>",
            3: "<:3rank:1128332544102899874>",
            4: "<:4rank:1128332546812432424>",
            5: "<:5rank:1128332548397858996>",
            6: "<:6rank:1128332550570512534>",
            7: "<:7rank:1128332552051105833>",
            8: "<:8rank:1128332553368129696>",
            9: "<:9rank:1128332556316704858>",
            10: "<:10rank:1128332558099296286>",
            11: "<:11rank:1128332560406163577>",
            12: "<:12rank:1128332561748340886>",
            13: "<:13rank:1128333983361536010>",
            14: "<:14rank:1128332571420401684>",
            15: "<:15rank:1128332574142513224>",
            16: "<:16rank:1128332575727964321>",
            17: "<:17rank:1128332578173235210>",
            18: "<:18rank:1128332579649622016>",
            19: "<:19rank:1128333985936850954>",
            20: "<:20rank:1128332584187854918>",
            21: "<:21rank:1128332586834477238>",
            22: "<:22rank:1128333987526488195>",
            23: "<:23rank:1128332589674020925>",
            24: "<:24rank:1128333988881240095>",
            25: "<:25rank:1128332596045164554>",
            26: "<:26rank:1128332599509659710>",
            27: "<:27rank:1128332601397096589>",
            28: "<:28rank:1128332604286971975>",
            29: "<:29rank:1128333991276204092>",
            30: "<:30rank:1128332606551892098>",
            31: "<:31rank:1128333992521900043>",
            32: "<:32rank:1128332610167373875>",
            33: "<:33rank:1128333998679146517>",
            34: "<:34rank:1128332613745123348>",
            35: "<:35rank:1128334001661288489>",
            36: "<:36rank:1128332618602119179>",
            37: "<:37rank:1128332625904418876>",
            38: "<:38rank:1128332629083697258>",
            39: "<:39rank:1128332630744629368>",
            40: "<:40rank:1128332633370263593>"

        }
        return lvls_dict[lvl]

    def __calculate_progress_percents(self, progress: int):
        return int((progress / 5000) * 100)

    def __render_progress_line(self, progress: int) -> str:
        filled = "▰"
        null = "▱"
        segments_count = 26
        
        percents = self.__calculate_progress_percents(progress)

        segments_filled_count = (segments_count * percents) // 100
        segments_null_count = (segments_count - segments_filled_count)

        return str(filled * segments_filled_count + null * segments_null_count + f" {percents}%")

    def get_info_embed(self, steam_id: str, gained_xp: int, lvl: int, progress: int, avatar_url: str, medal: Medals) -> disnake.Embed:
        """Сгенерировать Embed со статистикой в CS:GO"""
        shown_xp = str(gained_xp)
        if gained_xp > 0:
            shown_xp = "+" + str(gained_xp)

        xp_left = "Need " + str(5000 - progress) + " XP for next level"

        embed = disnake.Embed(
            description=f"**[{self.__user_name}]({self.__steamcommunity_link})** {medal}",
            colour=0xff3838
        )
        embed.add_field(name="<:steam:1129754230492758118> SteamID",
                        value=steam_id, inline=True)
        embed.add_field(name="<:xp:1129758227375079454> Gained XP",
                        value=shown_xp, inline=True)
        embed.add_field(name=f"{self.__get_lvl_emoji(lvl)} Level {lvl} |  Progress: {progress}/5000",
                        value=self.__render_progress_line(progress), inline=False)
        embed.add_field(name=xp_left, value='', inline=False)
        embed.set_thumbnail(url=avatar_url)
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f"XP Tracker")
        return embed

class DiscordBot:
    def __init__(self, token):
        self.token = token
        self.bot = commands.InteractionBot(intents=disnake.Intents.all())

    def run(self):
        self.bot.run(self.token)
