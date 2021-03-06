import configparser
import datetime
import os
import re
import time
import winsound
import pyperclip
import requests
from termcolor import colored

VERSION = "a1.0"


# internal variables
last_clipboard_hash = ""
last_clipboard_url_hash = ""
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
clear_console_log_on_startup = True


class Player:
    def __init__(self, userid: str = None, name: str = None, uniqueid: str = None, connected: str = None,
                 ping: str = None, loss: str = None, state: str = None,
                 rate: str = None):
        if userid == "BOT":
            self.is_bot = True

        self.userid = userid
        self.name = name
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
    is_bot = False

    def open_in_browser(self):
        if self.is_bot:
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
            if "csgobackpack.net" in websites:
                commands.append('start "" "' + self.get_csgobackpack_net_url() + '"')

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

    def get_csgobackpack_net_url(self):
        return str("csgobackpack.net/?nick=") + str(Player.steamid_to_64bit(self.uniqueid))

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
            a_file = open(csgo_log_file, "r", encoding="utf8")
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
        if players:
            beep(200, 250)

        if players:
            print_wrapper("Opening")
            own_players = []  # shouldn't be more than 1
            if own_names_or_steamids:
                for own_string in own_names_or_steamids:
                    for player in players:
                        try:  # bots have None set
                            if own_string in player.name or own_string in player.uniqueid or own_string in str(
                                    player.steamid_to_64bit(player.uniqueid)):
                                own_players.append(player.uniqueid)
                        except:
                            pass

            # Remove bots
            players = list(filter(lambda x: x.is_bot == False, players))

            for player in players:
                if player.uniqueid not in own_players:  # check in other team or nothing set
                    player.open_in_browser()
                else:
                    pass  # other unknown player

    if file:
        last_file_hash = hashed
    else:
        last_clipboard_hash = hashed


def check_both():
    check(False)
    if csgo_log_file:
        check(True)


def check_url_clipboard():
    global last_clipboard_url_hash
    text = pyperclip.paste()
    hashed = hash(text)
    if last_clipboard_url_hash == hashed:
        return
    last_clipboard_url_hash = hashed

    if "steamcommunity.com" not in text:
        return

    url = 'https://steamid.xyz/' + text

    x = requests.get(url)
    data = x.text
    start = data.find("Steam ID\r\n")
    end = data.find("\">", start)
    start = data.rfind("\"", start, end) + 1
    data = data[start:end]
    if not data.startswith("STEAM_"):
        return

    player = Player(uniqueid=data)

    player.open_in_browser()


def main():
    info()

    load_settings()

    if clear_console_log_on_startup and csgo_log_file:
        if os.path.exists(csgo_log_file):
            with open(csgo_log_file, 'r+') as f:
                f.truncate(0)

    while True:
        check_both()
        check_url_clipboard()
        delay = 3.0
        time.sleep(delay)


def load_settings():
    global own_names_or_steamids
    global websites
    global opening_delay
    global opening_same_player_delay
    global csgo_log_file
    global clear_console_log_on_startup

    config = configparser.ConfigParser()
    config.read("config.ini")
    try:
        own_names_or_steamids[:] = list(config["DEFAULT"]["IGNORE_PLAYERS"].split(","))
        config.set('DEFAULT', 'IGNORE_PLAYERS', ",".join(own_names_or_steamids))
    except Exception as e:
        config.set('DEFAULT', 'IGNORE_PLAYERS', ",".join(["PlayerName"]))
        print("Config Error: IGNORE_PLAYERS")

    try:
        websites[:] = list(config["DEFAULT"]["USE_WEBSITES"].split(","))
        config.set('DEFAULT', 'USE_WEBSITES', ",".join(websites))
    except Exception as e:
        config.set('DEFAULT', 'USE_WEBSITES', ",".join(["csgostats.gg"]))
        print("Config Error: USE_WEBSITES")

    try:
        opening_delay = float(config["DEFAULT"]["OPENING_DELAY"])
        config.set('DEFAULT', 'OPENING_DELAY', str(opening_delay))
    except Exception as e:
        config.set('DEFAULT', 'OPENING_DELAY', "0.1")
        print("Config Error: OPENING_DELAY")

    try:
        opening_same_player_delay = float(config["DEFAULT"]["OPENING_DELAY_SAME_PLAYER"])
        config.set('DEFAULT', 'OPENING_DELAY_SAME_PLAYER', str(opening_same_player_delay))
    except Exception as e:
        config.set('DEFAULT', 'OPENING_DELAY_SAME_PLAYER', "0.0")
        print("Config Error: OPENING_DELAY_SAME_PLAYER")

    try:
        csgo_log_file = config["DEFAULT"]["CSGO_LOG_FILE"]
        config.set('DEFAULT', 'CSGO_LOG_FILE', str(csgo_log_file))
    except Exception as e:
        config.set('DEFAULT', 'CSGO_LOG_FILE',
                   "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global "
                   "Offensive\\csgo\\console.log")
        print("Config Error: CSGO_LOG_FILE")

    try:
        clear_console_log_on_startup = config["DEFAULT"]["CLEAR_CONSOLE_LOG_ON_STARTUP"] == "True"
        config.set('DEFAULT', 'CLEAR_CONSOLE_LOG_ON_STARTUP', str(clear_console_log_on_startup))
    except Exception as e:
        config.set('DEFAULT', 'CLEAR_CONSOLE_LOG_ON_STARTUP',
                   str(True))
        print("Config Error: CLEAR_CONSOLE_LOG_ON_STARTUP")

    with open("config.ini", 'w') as configfile:
        config.write(configfile)


def info():
    print("There is a settings file, where you can control the following:"
          "\nIGNORE_PLAYERS:"
          "\n\tcomma separated values"
          "\n\tpart of a username or steamid"
          "\n\twill only open players where none of these values matches with everyone in the team"
          "\nUSE_WEBSITES:"
          "\n\tcomma separated values"
          "\n\twebsites to open"
          "\n\tcsgostats.gg,csgo-stats.net,csgo-stats.com,steamcommunity.com,steamid.uk,steamdb.info,csgobackpack.net"
          "\nOPENING_DELAY:"
          "\n\tdelay between opening each player"
          "\nOPENING_DELAY_SAME_PLAYER:"
          "\n\tdelay between different websites for same player"
          "\nCSGO_LOG_FILE:"
          "\n\tcsgo console log file path"
          "\n\tset with: 'con_logfile console.log'"
          "\n"
          "\n"
          "\noptional csgo commands: bind f11 status; con_logfile console.log"
          "\n"
          "\n")


def check_update():
    update_url = "https://github.com/Beat2er/CsGoStatsOpener/raw/{version}/CsGoStatsOpener.exe"
    version_url = "https://raw.githubusercontent.com/Beat2er/CsGoStatsOpener/master/.latest-version"
    x = requests.get(version_url)
    data = x.text
    data = data.split("\n")[0]

    if " " in data:
        print(colored("Can't check current version: " +
                      "https://raw.githubusercontent.com/Beat2er/CsGoStatsOpener/master/.latest-version " + data,
                      "red"))
        print("\n\n\n\n\n\n")
        time.sleep(3)
        return

    if data != VERSION:
        update_url = update_url.replace("{version}", data)
        print(colored("Current version is " + VERSION + ", but new Version is " + data + ".", "yellow"))
        print(colored("Download the new version here: " + update_url, "green"))
        print("\n\n\n\n\n\n")
        time.sleep(3)
        return


def print_wrapper(*args):
    now = datetime.datetime.now()
    args = list(args)
    args.insert(0, now.strftime("%Y-%m-%d %H:%M:%S"))
    print(*args)


if __name__ == "__main__":
    # execute only if run as a script
    check_update()
    main()
