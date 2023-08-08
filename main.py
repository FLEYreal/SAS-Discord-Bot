import gevent
import asyncio

# Импорт конфигурационного файла, содержащего различные настройки
from DiscordBot import DiscordBot, SteamStatManager
from config import *

# Импорт библиотек для работы с CS:GO
from csgo.client import CSGOClient
from csgo.enums import ECsgoGCMsg
from steam.client import SteamClient
from steam.steamid import SteamID

# Импорт библиотеки disnake, которая является вилкой discord.py с поддержкой команд с помощью слэша
import disnake

# Импорт других необходимых библиотек
import csgo
import os
import requests
import json

import tracemalloc
tracemalloc.start()

# Клиенты
steam_client = SteamClient()
csgo_client = CSGOClient(steam_client)
client = DiscordBot(TOKEN)

checking_loop_running = False

# Лог в консоль, когда бот загружен
@client.bot.event
async def on_ready():
    print(f'We have logged in as {client.bot.user}')

@client.bot.slash_command(name="stat", description="Shows statistics of the user")
async def stat(interaction: disnake.ApplicationCommandInteraction, steam_id: str):
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

        # Предполагая, что функция replace_medal_to_color переводит номер медали в соответствующий Enum
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

def steam_login():
    print(f"Logging in to Steam as {STEAM_USERNAME}")

    if steam_client.logged_on:
        return

    if not os.path.exists(CREDENTIALS_LOCATION):
        os.makedirs(CREDENTIALS_LOCATION)
    steam_client.set_credential_location(CREDENTIALS_LOCATION)

    if steam_client.relogin_available:
        steam_client.relogin()
    elif steam_client.login_key is not None:
        steam_client.login(username=STEAM_USERNAME, ogin_key=steam_client.login_key)
    else:
        steam_client.cli_login(username=STEAM_USERNAME, password=STEAM_PASSWORD)

def replace_medal_to_color(medal):
    Medals_2023_color = {
        4873: "<:2023_1:1128338078835159100>",
        4874: "<:2023_2:1128338080877785098>",
        4875: "<:2023_3:1128338084833009715>",
        4876: "<:2023_4:1128338089471922268>",
        4877: "<:2023_5:1128338093066424360>",
        4878: "<:2023_6:1128338143268044830>",
    }
    if medal in Medals_2023_color:
        return Medals_2023_color[medal]
    else:
        return "Without medal"

def launch_csgo():
	if csgo_client.connection_status == csgo.enums.GCConnectionStatus.NO_SESSION:
		steam_login()
		csgo_client.launch()

def get_user_level_and_xp(steam_id):
	launch_csgo()

	inspect_params = { "account_id": SteamID(steam_id).as_32, "request_level": 32 }
	csgo_client.send(ECsgoGCMsg.EMsgGCCStrike15_v2_ClientRequestPlayersProfile, inspect_params)
	response = csgo_client.wait_event(ECsgoGCMsg.EMsgGCCStrike15_v2_PlayersProfile, timeout=5)

	if response is None:
		raise Exception("CS:GO sent an empty response.")
	
	profile = response[0].account_profiles[0]

	medals = profile.medals.display_items_defidx
	#Определение какая у профиля медаль, перевод её номера в текст и вывод в консоль
	Medals_2023 = [4873, 4874, 4875, 4876, 4877, 4878]
	Medal_in_profile = 0

	if profile.player_level == 0:
		profile.player_level = 1

	if max(0, profile.player_cur_xp - 327680000) == 0:
		return profile.player_level, 1, medals

	return profile.player_level, max(0, profile.player_cur_xp - 327680000), medals

def get_user_name_and_avatar(steam_id, api_key):
    if DISABLE_STEAM_API:
        raise Exception("Steam API is disabled")

    params = {
        "key": api_key,
        "steamids": steam_id
    }

    response = requests.get(
        "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/", params=params)
    response.raise_for_status()

    json = response.json()
    for player in json["response"]["players"]:
        if player["steamid"] != str(steam_id):
            continue
        return player["personaname"], player["avatarfull"]

    raise Exception(f"Could't find {steam_id} in response.")

@steam_client.on("logged_on")
def steam_client_logged_on():
    print("Steam client logged on")
    csgo_client.launch()

# Лог в консоль, когда csgo клиент загружен
@csgo_client.on("ready")
def csgo_client_ready():
    print("CS:GO client ready")

# Отлов ошибок CSGO
@csgo_client.on("error")
def csgo_client_error(error):
    print(f"CS:GO client error: {error}")

# Отлов ошибок Steam
@steam_client.on("error")
def steam_client_error(error):
    print(f"Steam client error: {error}")

# Главная функция для загрузки всего нужного
def main():
    # Логин стима
    steam_login()

    # Запускаем steam_client в фоновом режиме
    gevent.spawn(steam_client.run_forever)

    # Ждем 1 секунду
    gevent.sleep(1)

    # Запускаем client в фоновом режиме
    gevent.spawn(client.run)

    # Ждем некоторое время, чтобы убедиться, что бот успешно запустился
    gevent.sleep(5)

# Запускаем главный событийный цикл
if __name__ == "__main__":
    main()
    gevent.wait()
