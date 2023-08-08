# Базовые импорты
import disnake

# Импорт из других файлов
from config import *
from DiscordBot import SteamStatManager
from user import replace_medal_to_color, get_user_level_and_xp, get_user_name_and_avatar
from clients import client

@client.bot.slash_command(name="stats", description="Shows statistics of the user")
async def stats(interaction: disnake.ApplicationCommandInteraction, steam_id: str):
    await interaction.response.defer()

    # Получаем уровень и опыт пользователя с помощью функции get_user_level_and_xp
    player_level, player_cur_xp, medals = get_user_level_and_xp(steam_id)

    # Получаем имя пользователя и URL аватара
    user_name, avatar_url = get_user_name_and_avatar(
        steam_id, STEAM_API_KEY)

    # Определение медали
    Medals_2023 = [4873, 4874, 4875, 4876, 4877, 4878]
    Medal_in_profile = next(
        (medal for medal in medals if medal in Medals_2023), None)
    # Предполагая, что функция replace_medal_to_color переводит номер медали в соответствующий Enum
    medal_enum = replace_medal_to_color(Medal_in_profile)

    steamcommunity_link = f"https://steamcommunity.com/profiles/{steam_id}"

    # Создаем экземпляр SteamStatManager
    ssm = SteamStatManager(user_name, steamcommunity_link)

    # Получаем встраиваемое сообщение с помощью метода get_info_embed
    embed = ssm.get_info_embed(
        steam_id, player_cur_xp, player_level, player_cur_xp, avatar_url, medal_enum)

    await interaction.edit_original_response(embed=embed)