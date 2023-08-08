# Базовые импорты
import requests

# Импорт библиотек для работы с CS:GO
from csgo.enums import ECsgoGCMsg
from steam.steamid import SteamID
import csgo

# Импорты файлов
from config import *
from clients import steam_login, csgo_client

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

def get_user_level_and_xp(steam_id):
	if csgo_client.connection_status == csgo.enums.GCConnectionStatus.NO_SESSION:
		steam_login()
		csgo_client.launch()

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