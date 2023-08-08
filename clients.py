# Базовые импорты
import os

# Steam & CS:GO
from csgo.client import CSGOClient
from steam.client import SteamClient

# Импорты из файлов
from config import *
from DiscordBot import DiscordBot

# Клиенты
steam_client = SteamClient()
csgo_client = CSGOClient(steam_client)
client = DiscordBot(TOKEN)

# Функция входа в стим
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