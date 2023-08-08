# Базовые импорты
import asyncio
import disnake
import json

# Импорт из других файлов
from DiscordBot import SteamStatManager
from user import replace_medal_to_color, get_user_level_and_xp, get_user_name_and_avatar
from config import *
from clients import client

checking_loop_running = False

@client.bot.slash_command(name="track", description="Starts tracking users from list!")
async def track(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.defer()

    global checking_loop_running

    if checking_loop_running:
        await interaction.edit_original_response('Already tracking user(s)!')
    else:
        checking_loop_running = True

        # Чтение steam_id и xp из файла tracking_list.json
        with open('tracking_list.json', 'r') as file:
            tracking_data = json.load(file)

        # Создание и запуск асинхронных циклов для каждого steam_id
        tasks = [track_user(steam_data, interaction) for steam_data in tracking_data]
        await asyncio.gather(*tasks)

        # Сохранение обновленных данных в файл tracking_list.json
        with open('tracking_list.json', 'w') as file:
            json.dump(tracking_data, file, indent=4)

        checking_loop_running = False

async def track_user(steam_data, interaction):
    global checking_loop_running

    while checking_loop_running:

        steam_id = steam_data['id']
        prev_xp = steam_data['xp']
        prev_level = steam_data['level']

        # Получаем актуальные данные из файла
        with open('tracking_list.json', 'r') as file:
            tracking_data = json.load(file)

        # Находим текущие данные по steam_id
        for data in tracking_data:
            if data['id'] == steam_id:
                prev_xp = data['xp']
                prev_level = data['level']
                break

        # Получаем уровень и опыт пользователя с помощью функции get_user_level_and_xp
        player_level, player_cur_xp, medals = get_user_level_and_xp(steam_id)

        # Получаем имя пользователя и URL аватара
        user_name, avatar_url = get_user_name_and_avatar(steam_id, STEAM_API_KEY)

        # Определение медали
        Medals_2023 = [4873, 4874, 4875, 4876, 4877, 4878]
        Medal_in_profile = next((medal for medal in medals if medal in Medals_2023), None)

        # replace_medal_to_color переводит номер медали в соответствующий Enum
        medal_enum = replace_medal_to_color(Medal_in_profile)

        steamcommunity_link = f"https://steamcommunity.com/profiles/{steam_id}"

        # Создаем экземпляр SteamStatManager
        ssm = SteamStatManager(user_name, steamcommunity_link)

        # Если уровень повышается, то прошлый xp становится 0, чтобы 
        # не было конфликтов в gained_xp и не было отрицательных чисел
        if player_level != prev_level:
            prev_xp = 0

        # Получаем полученный опыт
        gained_xp = player_cur_xp - prev_xp

        # Получаем встраиваемое сообщение с помощью метода get_info_embed
        embed = ssm.get_info_embed(steam_id, gained_xp, player_level, player_cur_xp, avatar_url, medal_enum)

        # Проверяем, изменилось ли xp и отправляем новое сообщение с встраиваемым содержимым
        if player_cur_xp != prev_xp:

            # Обновляем значение prev_xp на новое полученное значение xp и сохраняем в json
            steam_data['xp'] = player_cur_xp

            # Обновляем значение prev_xp в данных пользователя в tracking_list.json
            for data in tracking_data:
                if data['id'] == steam_id:
                    data['xp'] = player_cur_xp
                    data['level'] = player_level
                    break

            # Сохраняем обновленные данные в файл tracking_list.json
            with open('tracking_list.json', 'w') as file:
                json.dump(tracking_data, file, indent=4)

            await interaction.followup.send(embed=embed)

        await asyncio.sleep(30)