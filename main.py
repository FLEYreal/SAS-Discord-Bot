# Импорт конфигурационного файла, содержащего различные настройки
from DiscordBot import DiscordBot, SteamStatManager, Medals
from config import *

# Импорт библиотек для работы с CS:GO
from csgo.client import CSGOClient
from csgo.enums import ECsgoGCMsg
from steam.client import SteamClient
from steam.steamid import SteamID

# Импорт собственных классов для работы с отслеживаемыми пользователями и списком отслеживания
from TrackedUsers import TrackedUsers
from TrackingList import TrackingList

# Импорт библиотеки disnake, которая является вилкой discord.py с поддержкой команд с помощью слэша
import disnake
from disnake.ext import commands
from disnake import Option, OptionType, ApplicationCommandInteraction

# Импорт других необходимых библиотек
import csgo
import os
import datetime
import requests
import gevent

import tracemalloc
tracemalloc.start()


steam_client = SteamClient()
csgo_client = CSGOClient(steam_client)
tracking_list = TrackingList(TRACKING_LIST_PATH)
tracked_users = TrackedUsers()


client = DiscordBot(TOKEN)

checking_loop_running = False


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
    # Предполагая, что функция Replace_medal_to_color переводит номер медали в соответствующий Enum
    medal_enum = Replace_medal_to_color(Medal_in_profile)

    steamcommunity_link = f"https://steamcommunity.com/profiles/{steam_id}"

    # Создаем экземпляр SteamStatManager
    ssm = SteamStatManager(user_name, steamcommunity_link)

    # Получаем встраиваемое сообщение с помощью метода get_info_embed
    embed = ssm.get_info_embed(
        steam_id, player_cur_xp, player_level, player_cur_xp, avatar_url, medal_enum)

    await interaction.edit_original_response(embed=embed)

@client.bot.slash_command(name="track", description="Starts tracking users from list!")
async def stat(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.defer()
    await interaction.edit_original_response('Starting to track users from list!')

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


def launch_csgo():
    print(csgo_client.connection_status == csgo.enums.GCConnectionStatus.NO_SESSION)
    if csgo_client.connection_status == csgo.enums.GCConnectionStatus.NO_SESSION:
        steam_login()
        csgo_client.launch()


def Replace_medal_to_color(medal):
    Medals_2023_color = {
        4873: "Grey",
        4874: "Green",
        4875: "Blue",
        4876: "Purple",
        4877: "Pink",
        4878: "Red",
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

	for medal in medals:
		if medal in Medals_2023:
			Medal_in_profile = medal

	print(f"{Replace_medal_to_color(Medal_in_profile)} Service medal 2023")
    
    ################################################################################

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


def calculate_difference(now, previous, _max):
    difference = now - previous
    if difference < 0:
        difference += _max
    return difference


# def user_xp_changed(tracked_user):
#     if tracked_user.first_check:
#         print(
#             f"First change for {tracked_user.steam_id}. Not sending message.")
#         return

#     print(f"Change for {tracked_user.steam_id}. Sending message.")

#     username = f"`{tracked_user.steam_id}`"
#     avatar = ""

#     try:
#         username, avatar = get_user_name_and_avatar(
#             tracked_user.steam_id, STEAM_API_KEY)
#     except Exception as e:
#         print(
#             f"Could't get username and avatar for {tracked_user.steam_id}: {e}")
#         pass

#     # EMBED
#     embed = DiscordEmbed()
#     embed.set_title(f"{username}")
#     embed.set_url(
#         f"https://steamcommunity.com/profiles/{tracked_user.steam_id}")
#     embed.set_thumbnail(avatar)
#     embed.set_timestamp(datetime.datetime.utcnow())

#     if tracked_user.level != tracked_user.previous_level:
#         level_difference = calculate_difference(
#             tracked_user.level, tracked_user.previous_level, 40)
#         embed.add_field(
#             name="Level", value=f"Was: *{tracked_user.previous_level}*\nNow: *{tracked_user.level}*\nDifference: *{level_difference:+}*")
#     else:
#         embed.add_field(name="Level (unchanged)",
#                         value=f"Now: *{tracked_user.level}*")

#     if tracked_user.xp != tracked_user.previous_xp:
#         XP_PER_LEVEL = 5000
#         xp_difference = calculate_difference(
#             tracked_user.xp, tracked_user.previous_xp, XP_PER_LEVEL)
#         embed.add_field(
#             name="XP", value=f"Was: *{tracked_user.previous_xp}*\nNow: *{tracked_user.xp}*/5000\nDifference: *{xp_difference:+}*\nNeed *{XP_PER_LEVEL - tracked_user.xp}* XP for next level")
#     else:
#         embed.add_field(name="XP (unchanged)",
#                         value=f"Now: *{tracked_user.xp}*/5000")

#     gevent.spawn(client.send, embed=embed, channel_id=CHANNEL_ID)

#     #################################################################################


# def check_user(steam_id):
#     tracked_user = tracked_users.find_tracked_user_by_steam_id(steam_id)

#     try:
#         level, xp, medals = get_user_level_and_xp(tracked_user.steam_id)
#     except Exception as e:
#         print(f"Couldn't get level and XP for {tracked_user.steam_id}: {e}")
#         return

#     print(f"Got level and xp for {steam_id}: {level=} {xp=} Medals: {medals=}")
#     tracked_user.update_level_and_xp(level, xp, user_xp_changed)


def get_tracking_list_difference():
    old_tracking_list = tracking_list.get_tracking_list()
    tracking_list.read_tracking_list_from_file()
    new_tracking_list = tracking_list.get_tracking_list()

    tracking_added = [
        steam_id for steam_id in new_tracking_list if steam_id not in old_tracking_list]
    tracking_removed = [
        steam_id for steam_id in old_tracking_list if steam_id not in new_tracking_list]
    return tracking_added, tracking_removed


def send_tracking_list_difference_if_needed(tracking_added, tracking_removed):
    if not SEND_TRACKING_LIST_UPDATES:
        return

    if len(tracking_added) == 0 and len(tracking_removed) == 0:
        print(f"No difference in tracking list.")
        return

    print(
        f"Tracking list difference: {len(tracking_added)=} {len(tracking_removed)=}")

    embed = DiscordEmbed()
    embed.set_title("XP Tracker users changed")

    if len(tracking_added):
        steam_ids_list = "\n".join(tracking_added)
        embed.add_field(name="Users Added", value=f"```{steam_ids_list}```")

    if len(tracking_removed):
        steam_ids_list = "\n".join(tracking_removed)
        embed.add_field(name="Users Removed", value=f"```{steam_ids_list}```")

    embed.set_timestamp(datetime.datetime.utcnow())
    gevent.spawn(client.send, embed=embed, channel_id=CHANNEL_ID)


# def check_users():
#     global checking_loop_running

#     if checking_loop_running:
#         return

#     checking_loop_running = True

#     while True:
#         tracking_added, tracking_removed = get_tracking_list_difference()
#         send_tracking_list_difference_if_needed(
#             tracking_added, tracking_removed)

#         for steam_id in tracking_list.get_tracking_list():
#             print(f"Checking {steam_id}")
#             check_user(steam_id)

#         print(f"Next check in {CHECK_TIMEOUT} seconds.")
#         gevent.sleep(CHECK_TIMEOUT)


@steam_client.on("logged_on")
def steam_client_logged_on():
    print("Steam client logged on")
    csgo_client.launch()


@csgo_client.on("ready")
def csgo_client_ready():
    print("CS:GO client ready")

    # embed = DiscordEmbed()
    # embed.set_title("XP Tracker started")
    # embed.add_field(name="Users", value=f"Tracking {len(tracking_list.get_tracking_list())} user(s)")
    # embed.add_field(name="Checking", value=f"Checking every {CHECK_TIMEOUT} seconds")
    # embed.set_timestamp(datetime.datetime.utcnow().isoformat())

    # gevent.spawn(client.send, embed=embed, channel_id=CHANNEL_ID)

    # check_users()


@csgo_client.on("error")
def csgo_client_error(error):
    print(f"CS:GO client error: {error}")


@steam_client.on("error")
def steam_client_error(error):
    print(f"Steam client error: {error}")


def do_first_setup():
    global tracking_list
    if os.path.exists(TRACKING_LIST_PATH):
        return

    print("This seems to be your first time launching the program.")

    setup_tracking_list = input(
        "Do you want to set up the tracking list now? [Y/n] ") in ("Y", "y")
    if not setup_tracking_list:
        print(f"Okay. Resuming execution as normal")
        return

    print("Enter a Steam ID to start tracking or enter \"save\" to save tracking list and continue.")

    temp_tracking_list = []
    save = False

    while not save:
        steamid_to_add = input("Steam ID to add: ")
        if steamid_to_add == "save":
            save = True
            continue

        if not steamid_to_add.isdigit() or int(steamid_to_add) < 0x0110000100000000 or int(steamid_to_add) >= 0x01100001FFFFFFFF:
            add_anyways = input(
                f"{steamid_to_add} doesn't seem to be a valid SteamID64. Add anyways? [Y/n] ") in ("Y", "y")
            if not add_anyways:
                continue

        if steamid_to_add in temp_tracking_list:
            print(f"Already added {steamid_to_add}.")
            continue

        temp_tracking_list.append(steamid_to_add)
        print(f"Added {steamid_to_add} to tracking list.")
        print(f"Current list: {', '.join(temp_tracking_list)}")

    print(f"Saving list to {TRACKING_LIST_PATH}")
    for entry in temp_tracking_list:
        tracking_list.add_to_tracking_list(entry)
    print(f"Saved tracking list. Resuming execution as normal.")


def main():
    do_first_setup()
    steam_login()

    # Запускаем steam_client в фоновом режиме
    gevent.spawn(steam_client.run_forever)

    # Ждем 1 секунду
    gevent.sleep(1)

    # Запускаем client в фоновом режиме
    gevent.spawn(client.run)

    # Ждем некоторое время, чтобы убедиться, что бот успешно запустился
    gevent.sleep(5)

    # embed = DiscordEmbed()
    # embed.set_title(f"XP Tracker started")
    # gevent.spawn(client.send, embed=embed, channel_id=CHANNEL_ID)


# Запускаем главный событийный цикл
if __name__ == "__main__":
    main()
    gevent.wait()
