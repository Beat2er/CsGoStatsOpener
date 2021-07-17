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
last_file_hash = ""
keys_pressed = list([])
starting_string = "# userid name uniqueid connected ping loss state rate"
ending_string = "#end"

# settings:
own_names_or_steamids = []
opening_delay = 0.0
opening_same_player_delay = 0.0
csgo_log_file = ""
websites = []


class Player:
    def __init__(self, userid: str = None, name: str = None, uniqueid: str = None, connected: str = None,
                 ping: str = None, loss: str = None, state: str = None,
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
            commands = []
            if "csgostats.gg" in websites:
                commands.append('start "" "' + self.get_csgostats_gg_url() + '"')
            if "csgo-stats.net" in websites:
                commands.append('start "" "' + self.get_csgo_stats_net_url() + '"')
            if "csgo-stats.com" in websites:
                commands.append('start "" "' + self.get_csgo_stats_com_url() + '"')
            if "steamcommunity.com" in websites:
                commands.append('start "" "' + self.get_steam_url() + '"')
            if "steamid.uk" in websites:
                commands.append('start "" "' + self.get_steamid_uk_url() + '"')
            if "steamdb.info" in websites:
                commands.append('start "" "' + self.get_steamdb_info_url() + '"')

            for command in commands:
                os.system(command)
                if len(commands) > 1:
                    time.sleep(opening_same_player_delay)

            time.sleep(opening_delay)

    def get_csgostats_gg_url(self):
        return str("https://csgostats.gg/player/") + str(Player.steamid_to_64bit(self.uniqueid))

    def get_csgo_stats_net_url(self):
        return str("https://csgo-stats.net/search?q=") + str(Player.steamid_to_64bit(self.uniqueid))

    def get_csgo_stats_com_url(self):
        return str("https://csgostats.gg/player/") + str(Player.steamid_to_64bit(self.uniqueid))

    def get_steam_url(self):
        return str("http://steamcommunity.com/profiles/") + str(Player.steamid_to_64bit(self.uniqueid))

    def get_steamid_uk_url(self):
        return str("https://steamid.uk/profile/") + str(Player.steamid_to_64bit(self.uniqueid))

    def get_steamdb_info_url(self):
        return str("https://steamdb.info/calculator/") + str(Player.steamid_to_64bit(self.uniqueid))

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
        if parts[0] == "BOT":  # weird because "remove first (#)" doesn't work because of missing space
            player = Player(parts[0], line.split(" ")[1])
        else:
            player = Player(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7])
        return player
    except Exception as e:
        print(str(e))
        return False


def get_last_occurance(input_text: str):
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
                    return input_text
                else:
                    print_wrapper("No end found")
    return False


def parse_input(input_text: str):
    players = []
    lines = input_text.splitlines()
    lines = [line for line in lines if line]
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

    return players


def beep(duration: int, frequency: int):  # in ms; in Hertz
    winsound.Beep(frequency, duration)


def check(file: bool = False):
    global last_clipboard_hash
    global last_file_hash
    text = ""
    last_hash = ""
    if file:
        last_hash = last_file_hash
        try:
            a_file = open(csgo_log_file, "r")
            lines = a_file.readlines()
            text = lines[-80:]
            text = "\n".join(text)
        except IOError:
            print_wrapper("Couldn't read " + csgo_log_file)
            return False
    else:
        last_hash = last_clipboard_hash
        text = pyperclip.paste()

    short_text = get_last_occurance(text)



    hashed = hash(short_text)
    if last_hash != hashed and short_text:
        players = parse_input(short_text)
        if players and not last_found_players:
            beep(200, 250)

        if players:
            last_found_players[:] = players
            print_wrapper("Opening")
            own_rates = []  # shouldn't be more than 1
            if own_names_or_steamids:
                for own_string in own_names_or_steamids:
                    for player in players:
                        try:  # bots have None set
                            if own_string in player.name or own_string in player.uniqueid or own_string in str(
                                    player.steamid_to_64bit(player.uniqueid)):
                                own_rates.append(player.rate)
                        except:
                            pass
            for player in last_found_players:
                if player.rate not in own_rates or not own_rates:  # check in other team or nothing set
                    player.open_in_browser()

    if file:
        last_file_hash = hashed
    else:
        last_clipboard_hash = hashed


def check_both():
    check(False)
    if csgo_log_file:

        check(True)


def main():
    info()

    config = configparser.ConfigParser()
    config.read("config.ini")
    try:
        global websites
        global opening_delay
        global opening_same_player_delay
        global csgo_log_file
        own_names_or_steamids[:] = list(config["DEFAULT"]["IGNORE_PLAYERS_TEAM"].split(","))
        config.set('DEFAULT', 'IGNORE_PLAYERS_TEAM', ",".join(own_names_or_steamids))
        websites[:] = list(config["DEFAULT"]["USE_WEBSITES"].split(","))
        config.set('DEFAULT', 'USE_WEBSITES', ",".join(websites))
        opening_delay = float(config["DEFAULT"]["OPENING_DELAY"])
        config.set('DEFAULT', 'OPENING_DELAY', opening_delay)
        opening_same_player_delay = float(config["DEFAULT"]["OPENING_DELAY_SAME_PLAYER"])
        config.set('DEFAULT', 'OPENING_DELAY_SAME_PLAYER', opening_same_player_delay)
        csgo_log_file = config["DEFAULT"]["CSGO_LOG_FILE"]
        config.set('DEFAULT', 'CSGO_LOG_FILE',
                   csgo_log_file)
    except:
        config.set('DEFAULT', 'IGNORE_PLAYERS_TEAM', ",".join(["PlayerName"]))
        config.set('DEFAULT', 'USE_WEBSITES', ",".join(["csgostats.gg"]))
        config.set('DEFAULT', 'OPENING_DELAY', "0.1")
        config.set('DEFAULT', 'OPENING_DELAY_SAME_PLAYER', "0.0")
        config.set('DEFAULT', 'CSGO_LOG_FILE', "C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\console.log")

    with open("config.ini", 'w') as configfile:
        config.write(configfile)

    start_time = time.time()
    while True:
        check_both()
        delay = 3.0
        time.sleep(delay - ((time.time() - start_time) % delay))


def info():
    print("There is a settings file, where you can control the following:"
          "\nIGNORE_PLAYERS_TEAM:"
          "\n\tcomma separated values"
          "\n\tpart of a username or steamid"
          "\n\twill only open players where none of these values matches with everyone in the team"
          "\nUSE_WEBSITES:"
          "\n\tcomma separated values"
          "\n\twebsites to open"
          "\n\tcsgostats.gg,csgo-stats.net,csgo-stats.com,steamcommunity.com,steamid.uk,steamdb.info"
          "\nOPENING_DELAY:"
          "\n\tdelay between opening each player"
          "\nOPENING_DELAY_SAME_PLAYER:"
          "\n\tdelay between different websites for same player"
          "\nCSGO_LOG_FILE:"
          "\n\tcsgo console log file path"
          "\n\tset with: 'con_logfile console.log'"
          "\n\t"
          "\noptional keybind: bind f11 status")

def print_wrapper(*args):
    now = datetime.datetime.now()
    args = list(args)
    args.insert(0, now.strftime("%Y-%m-%d %H:%M:%S"))
    print(*args)


if __name__ == "__main__":
    # execute only if run as a script
    main()
