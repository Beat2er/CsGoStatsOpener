import configparser
import datetime
import os
import re
import time
import winsound
from functools import cmp_to_key

import pyperclip

# internal variables
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
dont_open_own = False
delay_between_teams = 0.0
url_between_teams = ""
beep_between_teams = False


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
        if players:
            beep(200, 250)

        if players:
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

            # sort players:
            def compare(item1: Player, item2: Player):
                if item1.rate < item2.rate:
                    return -1
                elif item1.rate > item2.rate:
                    return 1
                else:
                    return 0

            # Remove bots
            players = list(filter(lambda x: x.is_bot == False, players))

            # Sorting
            players.sort(key=cmp_to_key(compare))
            if players[0].rate != players[len(players) - 1].rate and own_rates:  # check if multiple teams
                last_rate = players[len(players) - 1]
                if last_rate in own_rates:
                    pass
                else:  # invert because we want enemies first
                    players.reverse()

            last_rate = players[0].rate
            for player in players:
                if player.rate not in own_rates and own_rates:  # check in other team or nothing set
                    player.open_in_browser()
                else:
                    if last_rate != player.rate and last_rate:  # new team just started
                        if url_between_teams:
                            os.system('start "" "' + url_between_teams + '"')
                        if beep_between_teams:
                            beep(200, 220)
                        time.sleep(delay_between_teams)
                    last_rate = player.rate

                    if not dont_open_own:
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
        global dont_open_own
        global delay_between_teams
        global url_between_teams
        global beep_between_teams
        own_names_or_steamids[:] = list(config["DEFAULT"]["IGNORE_PLAYERS_TEAM"].split(","))
        config.set('DEFAULT', 'IGNORE_PLAYERS_TEAM', ",".join(own_names_or_steamids))
        websites[:] = list(config["DEFAULT"]["USE_WEBSITES"].split(","))
        config.set('DEFAULT', 'USE_WEBSITES', ",".join(websites))
        opening_delay = float(config["DEFAULT"]["OPENING_DELAY"])
        config.set('DEFAULT', 'OPENING_DELAY', str(opening_delay))
        opening_same_player_delay = float(config["DEFAULT"]["OPENING_DELAY_SAME_PLAYER"])
        config.set('DEFAULT', 'OPENING_DELAY_SAME_PLAYER', str(opening_same_player_delay))
        csgo_log_file = config["DEFAULT"]["CSGO_LOG_FILE"]
        config.set('DEFAULT', 'CSGO_LOG_FILE', str(csgo_log_file))
        dont_open_own = config["DEFAULT"]["DONT_OPEN_OWN_TEAM"] == "True"
        config.set('DEFAULT', 'DONT_OPEN_OWN_TEAM', str(dont_open_own))
        delay_between_teams = float(config["DEFAULT"]["TEAM_DELAY"])
        config.set('DEFAULT', 'TEAM_DELAY', str(delay_between_teams))
        url_between_teams = config["DEFAULT"]["TEAM_SEPARATOR_URL"]
        config.set('DEFAULT', 'TEAM_SEPARATOR_URL', str(url_between_teams))
        beep_between_teams = config["DEFAULT"]["TEAM_SWITCH_BEEP"] == "True"
        config.set('DEFAULT', 'TEAM_SWITCH_BEEP', str(beep_between_teams))
    except Exception as e:
        config.set('DEFAULT', 'IGNORE_PLAYERS_TEAM', ",".join(["PlayerName"]))
        config.set('DEFAULT', 'USE_WEBSITES', ",".join(["csgostats.gg"]))
        config.set('DEFAULT', 'OPENING_DELAY', "0.1")
        config.set('DEFAULT', 'OPENING_DELAY_SAME_PLAYER', "0.0")
        config.set('DEFAULT', 'CSGO_LOG_FILE',
                   "C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\console.log")
        config.set('DEFAULT', 'DONT_OPEN_OWN_TEAM', "False")
        config.set('DEFAULT', 'TEAM_DELAY', "1.0")
        config.set('DEFAULT', 'TEAM_SEPARATOR_URL', "https://random.dog/")
        config.set('DEFAULT', 'TEAM_SWITCH_BEEP', "True")

    with open("config.ini", 'w') as configfile:
        config.write(configfile)

    while True:
        check_both()
        delay = 3.0
        time.sleep(delay)


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
          "\nDONT_OPEN_OWN_TEAM:"
          "\n\twont open any player in your team"
          "\nTEAM_DELAY:"
          "\n\tdelay between 2 different teams"
          "\nTEAM_SEPARATOR_URL:"
          "\n\turl between 2 different teams"
          "\nTEAM_SWITCH_BEEP:"
          "\n\tbeep between 2 different teams"
          "\noptional csgo commands: bind f11 status; con_logfile console.log")


def print_wrapper(*args):
    now = datetime.datetime.now()
    args = list(args)
    args.insert(0, now.strftime("%Y-%m-%d %H:%M:%S"))
    print(*args)


if __name__ == "__main__":
    # execute only if run as a script
    main()
