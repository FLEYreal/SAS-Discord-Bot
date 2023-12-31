﻿# SAS-Discord-Bot
(SAS stands for Steam Account System)

### About
This is a discord bot, that is sending messages any time cs:go XP is updated. You can define users that bot will send messages about and use /stats to see stats of any user.

### Notation
If you are interested in collaboration, message here:
<p>Telegram: @Nikita1264</p>
<p>Discord: fley0609</p>

## How to Start

Application is made with Python so to use the bot, you need to download it from official website [here](https://www.python.org/downloads/). 

1. To Launch the bot, enter the folder of the bot in the console using following command:
```shell
cd C:/path/to/directory
```
2. Inside of the console, after entering the bot's folder, type this command to install all the dependencies:
```shell
pip install -r requirements.txt
```
4. In the root folder of the project - enter file "config.py". This is a file with all settings and important information for your bot.
```python
# Login for account that checks the XP
# This account can't be used at the same time as the checker is running
STEAM_USERNAME = ""
STEAM_PASSWORD = ""

# Steam API key for getting account name and avatar
# If you disable it, you wont see user's names or avatars
STEAM_API_KEY = ""
DISABLE_STEAM_API = False

# Path where logins for Steam will be saved
CREDENTIALS_LOCATION = "credentials"

# Path for list of users being tracked
TRACKING_LIST_PATH = "tracking_list.json"

# Send message if user is added/removed
SEND_TRACKING_LIST_UPDATES = True

# Timeout between checks (in seconds)
CHECK_TIMEOUT = 60

# Discord Token
TOKEN = ""
```
You need to setup this file properly to make this work.

4.1 Type data (username, password) from your account in these quotes
```python
STEAM_USERNAME = ""
STEAM_PASSWORD = ""
```
4.2 Type here API key for Steam
```python
STEAM_API_KEY = ""
```
4.3 Type here Token for your discord bot.
```python
TOKEN = ""
```

5. To launch the bot use:
```shell
python main.py
```

6. To Stop the application, you need yo use "ctrl + C" keys.

# A little Documentation
This is a little documentation to basics of using this script.

## Tracking users

### How to start tracking
To start tracking, use command "/track".

### Add new users to track
The script contains file "tracking_list.json". This is the list of all users that are being tracked by bot.
To add new user, you need to first add comma before last item, then add this code:
```json
{
  "id": "",
  "xp": 0,
  "level": 0
}
```
Inside of empty quotes in "id" value, add the steam Id of the user you want to track.

## Stats of users
If you want to know the statistics of any user you want, use this command:
```
/stats <steam-id>
```
