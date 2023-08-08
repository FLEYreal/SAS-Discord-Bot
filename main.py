# Базовые импорты
import gevent
import disnake.ext.commands as commands
import tracemalloc
tracemalloc.start()

# Импорт из файла config.py
from config import *

# Импорт из файла client.py
from clients import steam_client, csgo_client, client, steam_login

# Лог в консоль, когда бот загружен
@client.bot.event
async def on_ready():
    print(f'We have logged in as {client.bot.user}')

# Импорт команд

#   - Команда /stats
from stats import *

#   - Команда /track
from track import *

# Стим клиент залогинен
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
