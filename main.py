##sample:


#   Richard'Nixon connected.
#   ] status
#   Connected to =[A:1:1078862852:17988]:0
#   hostname: Valve CS:GO EU West Server (srcds216-fra2.272.174)
#   version : 1.37.9.5 secure
#   os      :  Linux
#   type    :  official dedicated
#   map     : de_cbble
#   players : 21 humans, 0 bots (20/0 max) (not hibernating)
#
#   # userid name uniqueid connected ping loss state rate
#   # 354 2 "三流剑士" STEAM_1:0:506023587 33:37 190 0 active 196608
#   # 403 3 "她与残局皆遗憾" STEAM_1:0:609176872 00:42 215 1 active 196608
#   # 364 4 "G@mbit" STEAM_1:1:301389 33:25 64 0 active 786432
#   # 384 5 "AlfiQue" STEAM_1:0:5483984 16:14 51 0 active 196608
#   # 351 6 "robbeddc" STEAM_1:1:57138719 43:38 62 0 active 196608
#   # 404 7 "MadMannitou" STEAM_1:1:69300517 00:37 62 0 active 196608
#   # 405 8 "YoungCashRegister/LilBroomstick" STEAM_1:0:97570223 00:32 33 0 active 196608
#   # 400 9 "Slug" STEAM_1:1:164676156 06:26 62 0 active 786432
#   # 385 10 "鹤川." STEAM_1:0:436950471 16:13 182 0 active 196608
#   # 321 11 "masQuerade" STEAM_1:0:494004  1:01:35 40 0 active 196608
#   # 398 12 "bistouille" STEAM_1:0:516605178 13:43 48 0 active 196608
#   # 368 13 "等着我爆你头.88" STEAM_1:0:529610243 32:55 187 0 active 196608
#   # 406 14 "Papaya" STEAM_1:0:456426944 00:32 139 0 active 196608
#   # 338 15 "童年面包" STEAM_1:0:444402450  1:00:19 173 0 active 196608
#   # 371 16 "Kath" STEAM_1:0:608614675 32:32 62 0 active 196608
#   # 402 17 "𝒜𝓁𝒾𝓃𝒫" STEAM_1:1:541605367 01:19 107 0 active 196708
#   # 407 18 "Master Garavel" STEAM_1:0:167900695 00:32 68 76 spawning 196608
#   # 401 19 "Silly" STEAM_1:1:613890838 06:26 58 0 active 196608
#   # 408 20 "Beat2er™" STEAM_1:0:92446511 00:20 49 0 active 786432
#   # 417 21 "Richard'Nixon" STEAM_1:0:34505004 00:13 2462 78 active 196608
#   # 397 31 "Ghost_piranha" STEAM_1:0:466971370 16:08 109 0 spawning 196608
#   #end
#   Model 'chicken/chicken.mdl' has skin but thinks it can render fastpath
#
import re
import time
import winsound
import configparser
import pyperclip
import os
import datetime

# internal variables
last_found_players = list([])
last_clipboard_hash = ""
keys_pressed = list([])
starting_string = "# userid name uniqueid connected ping loss state rate"
ending_string = "#end"

# settings:
own_names_or_steamids = []
opening_delay = 0


class Player:
    def __init__(self, userid: str = None, name: str = None, uniqueid: str = None, connected: str = None, ping: str = None, loss: str = None, state: str = None,
                 rate: str = None):
        self.userid = userid
        self.name = name
        if userid == "BOT":
            self._is_bot = True
            return
        self.uniqueid = uniqueid
        self.connected = connected
        self.ping = ping
        self.loss = loss
        self.state = state
        self.rate = rate

    userid = None
    name = None
    uniqueid = None
    connected = None
    ping = None
    loss = None
    state = None
    rate = None
    _is_bot = False

    def open_in_browser(self):
        if self._is_bot:
            print_wrapper(self.name + " is a bot")
        else:
            command = 'start "" "' + self.get_url() + '"'
            os.system(command)

    def get_url(self):
        return str("https://csgostats.gg/player/") + str(Player.steamid_to_64bit(self.uniqueid))

    @staticmethod
    def steamid_to_64bit(steamid: str):
        steam64id = 76561197960265728  # I honestly don't know where
        # this came from, but it works...
        id_split = steamid.split(":")
        steam64id += int(id_split[2]) * 2  # again, not sure why multiplying by 2...
        if id_split[1] == "1":
            steam64id += 1
        return steam64id


def parse_line_as_player(line):
    parts = line.split(" ")
    parts.pop(0)  # remove first (#)
    parts.pop(0)  # remove first because unknown to me (#)

    newparts = []
    for part in parts:
        if len(newparts) == 2:
            if newparts[1].endswith('"'):
                newparts.append(part)
            else:
                newparts[1] = newparts[1] + part
        else:
            newparts.append(part)

    parts = newparts

    try:
        player = None
        if parts[0] == "BOT":   # weird because "remove first (#)" doesn't work because of missing space
            player = Player(parts[0], line.split(" ")[1])
        else:
            player = Player(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7])
        return player
    except Exception as e:
        print(str(e))
        return False


def parse_input(input_text: str):
    count = input_text.count(starting_string)
    players = []
    if count > 0:

        for m in re.finditer(starting_string, input_text):
            count -= 1
            if count == 0:
                start = m.start()
                end = input_text.find(ending_string, start)
                if start < end:
                    input_text = input_text[start:end]
                    lines = input_text.splitlines()
                    lines.pop(0)
                    for line in lines:
                        if not line.startswith("#"):
                            print_wrapper("'" + line + "' doesn't start with #")
                        player = parse_line_as_player(line)
                        if player:
                            players.append(player)
                        else:
                            if player != None:
                                print_wrapper("'" + line + "' couldn't be parsed as a player")

                else:
                    print_wrapper("No end found")
    else:
        print_wrapper("No occurrence found")
        return False
    return players


def beep(duration: int, frequency: int):  # in ms; in Hertz
    winsound.Beep(frequency, duration)


def check():
    clipboard = pyperclip.paste()
    players = parse_input(clipboard)
    if players and not last_found_players:
        beep(200, 250)

    clipboard_hash = hash(clipboard)
    global last_clipboard_hash

    if players:
        last_found_players[:] = players
        if last_clipboard_hash != clipboard_hash:
            print_wrapper("Opening")
            own_rates = []  # shouldn't be more than 1
            if own_names_or_steamids:
                for own_string in own_names_or_steamids:
                    for player in players:
                        try:    # bots have None set
                            if own_string in player.name or own_string in player.uniqueid or own_string in str(player.steamid_to_64bit(player.uniqueid)):
                                own_rates.append(player.rate)
                        except:
                            pass
            for player in last_found_players:
                if player.rate not in own_rates or not own_rates:  # check in other team or nothing set
                    player.open_in_browser()

    last_clipboard_hash = clipboard_hash


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    try:
        global opening_delay
        own_names_or_steamids[:] = list(config["DEFAULT"]["IGNORE_PLAYERS_TEAM"].split(","))
        config.set('DEFAULT', 'IGNORE_PLAYERS_TEAM', ",".join(own_names_or_steamids))
        opening_delay = int(config["DEFAULT"]["OPENING_DELAY"])
        config.set('DEFAULT', 'IGNORE_PLAYERS_TEAM', ",".join(own_names_or_steamids))
    except:
        config.set('DEFAULT', 'IGNORE_PLAYERS_TEAM', ",".join(["PlayerName"]))
        config.set('DEFAULT', 'OPENING_DELAY', "0")

    with open("config.ini", 'w') as configfile:
        config.write(configfile)

    start_time = time.time()
    while True:
        check()
        delay = 3.0
        time.sleep(delay - ((time.time() - start_time) % delay))


def print_wrapper(*args):
    now = datetime.datetime.now()
    args = list(args)
    args.insert(0, now.strftime("%Y-%m-%d %H:%M:%S"))
    print(*args)

if __name__ == "__main__":
    # execute only if run as a script
    main()
