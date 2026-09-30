import json
import os

DATA_STORAGE_FILE = "retro_bowl_data.json"

################################ GAME STATS AND SUBCLASSES ###############################
class Player_Game:
    def __init__(self, week, opponent, fum):
        self.week = week
        self.opponent = opponent
        self.fum = fum

    def calculate_passing_fpts(self):
        # 25 pass yd = 1 pt, 4pts per pass td, -2pts per int
        return (0.04 * self.pass_yds) + (4 * self.pass_tds) - (2 * self.ints)

    def calculate_rushing_fpts(self):
        return (0.1 * self.rush_yds) + (6 * self.rush_tds)
    
    def calculate_receiving_fpts(self):
        # PPR format
        return (1 * self.rec) + (0.1 * self.rec_yds) + (6 * self.rec_tds)

class Quarterback_Game(Player_Game):
    def __init__(self, week, opponent, cmp, att, pass_yds, pass_tds, pass_lng, ints,
                 sacks, carries, rush_yds, rush_tds, rush_lng, fum):
        
        super().__init__(week, opponent, fum)

        # Passing stats initialization
        self.att = att
        self.cmp = cmp
        self.cmp_pct = 0 if self.att == 0 else round(self.cmp / self.att, ndigits=2)
        self.pass_yds = pass_yds
        self.pass_tds = pass_tds
        self.pass_avg = 0 if self.att == 0 else round(self.pass_yds / self.att, ndigits=2)
        self.pass_lng = pass_lng
        self.ints = ints
        self.sacks = sacks

        # Rushing stats initialization
        self.carries = carries
        self.rush_yds = rush_yds
        self.rush_avg = 0 if self.carries == 0 else round(self.rush_yds / self.carries, ndigits=2)
        self.rush_tds = rush_tds
        self.rush_lng = rush_lng

        self.fpts = self.calculate_fpts()
    
    def calculate_fpts(self):
        return self.calculate_passing_fpts() + self.calculate_rushing_fpts() - (2 * self.fum)

    def to_dict(self):
        return {
            "__type__": "Quarterback_Game",
            "week": self.week,
            "opponent": self.opponent,
            "att": self.att,
            "cmp": self.cmp,
            "pass_yds": self.pass_yds,
            "pass_tds": self.pass_tds,
            "pass_lng": self.pass_lng,
            "ints": self.ints,
            "sacks": self.sacks,
            "carries": self.carries,
            "rush_yds": self.rush_yds,
            "rush_tds": self.rush_tds,
            "rush_lng": self.rush_lng,
            "fum": self.fum
        }

    @classmethod
    def from_dict(cls, d: dict):
        return Quarterback_Game(d["week"], d["opponent"], d["cmp"], d["att"], 
                                d["pass_yds"], d["pass_tds"], d["pass_lng"], d["ints"], d["sacks"],
                                d["carries"], d["rush_yds"], d["rush_tds"], d["rush_lng"], d["fum"])

class Runningback_Game(Player_Game):
    def __init__(self, week, opponent, carries, rush_yds, rush_tds, rush_lng,
                 rec, rec_yds, rec_tds, rec_lng, fum):
        
        super().__init__(week, opponent, fum)

        # Rushing stats initialization
        self.carries = carries
        self.rush_yds = rush_yds
        self.rush_tds = rush_tds
        self.rush_avg = 0 if self.carries == 0 else round(self.rush_yds / self.carries, ndigits=2)
        self.rush_lng = rush_lng

        # Receiving stats initialization
        self.rec = rec
        self.rec_yds = rec_yds
        self.rec_tds = rec_tds
        self.rec_avg = 0 if self.rec == 0 else round(self.rec_yds / self.rec, ndigits=2)
        self.rec_lng = rec_lng

        self.fpts = self.calculate_fpts()
        

    def calculate_fpts(self):
        return self.calculate_rushing_fpts() + self.calculate_receiving_fpts() - (2 * self.fum)

    def to_dict(self):
        return {
            "__type__": "Runningback_Game",
            "week": self.week,
            "opponent": self.opponent,
            "carries": self.carries,
            "rush_yds": self.rush_yds,
            "rush_tds": self.rush_tds,
            "rush_lng": self.rush_lng,
            "rec": self.rec,
            "rec_yds": self.rec_yds,
            "rec_tds": self.rec_tds,
            "rec_lng": self.rec_lng,
            "fum": self.fum,
            }

    @classmethod
    def from_dict(cls, d):
        return Runningback_Game(d["week"], d["opponent"], d["carries"], d["rush_yds"], d["rush_tds"],
                                d["rush_lng"], d["rec"], d["rec_yds"], d["rec_tds"], d["rec_lng"], d["fum"])

class Receiver_Game(Player_Game):
    def __init__(self, week: int, opponent: str, rec, rec_yds, rec_tds, rec_lng, fum):
        
        super().__init__(week, opponent, fum)

        self.rec = rec
        self.rec_yds = rec_yds
        self.rec_avg = 0 if self.rec == 0 else round(self.rec_yds / self.rec, ndigits=2)
        self.rec_tds = rec_tds
        self.rec_lng = rec_lng
        self.fpts = self.calculate_fpts()

    def __repr__(self):
        if type(self.week) == int:
            return f"Week {self.week} vs {self.opponent}"
        else:
            return f"{self.week} round vs {self.opponent}"

    def to_dict(self) -> dict:
        return {
            "__type__": "Receiver_Game",
            "week": self.week,
            "opponent": self.opponent,
            "rec": self.rec,
            "rec_yds": self.rec_yds,
            "rec_tds": self.rec_tds,
            "rec_lng": self.rec_lng,
            "fum": self.fum,
        }

    @classmethod
    def from_dict(cls, d):
        return Receiver_Game(d["week"], d["opponent"], d["rec"], d["rec_yds"], d["rec_tds"], d["rec_lng"], d["fum"])
    
    def calculate_fpts(self):
        return round(self.calculate_receiving_fpts() - (2 * self.fum), ndigits=2)

################################ SEASON RECORD AND SUBCLASSES ###############################
class Player_Season():
    def __init__(self, regular_season: list[Player_Game] = None, postseason: dict = None):
        if regular_season is not None:
            self.reg_season_games = regular_season
            self.num_reg_season_games = sum(1 for game in self.reg_season_games if game is not None)
        else:
            self.reg_season_games = [None] * 18
            self.num_reg_season_games = 0

        if postseason is not None:
            self.ps_games = postseason
            self.num_ps_games = sum(1 for v in self.ps_games.values() if v is not None)
        else:
            self.ps_games = {
                "wild card": None,
                "divisional": None,
                "conference": None,
                "super bowl": None
            }
            self.num_ps_games = 0

    def __repr__(self):
        if self.num_ps_games == 1:
            ps_phrase = "1 postseason game"
        else:
            ps_phrase = f"{self.num_ps_games} postseason games"
        return (f"Season with {self.num_reg_season_games} regular season games and " + ps_phrase)

    def to_dict(self):
        return {
            "__type__": "Player_Season",
            "reg_season": self.reg_season_games,
            "postseason": self.ps_games,
        }

    @classmethod
    def from_dict(cls, d):
        return Player_Season(d["reg_season"], d["postseason"])

################################ PLAYER CLASS AND SUBCLASSES ###############################
class Player:
    def __init__(self, name: str, position: str, age: int,
                 speed: int, stamina: int, career: list[Player_Season] = None):
        
        self.name = name
        self.position = position
        self.age = age
        self.experience = 0

        self.speed = speed
        self.stamina = stamina

        if career is not None:
            self.career_stats = career
        else:
            self.career_stats = [Player_Season()]

    def __repr__(self):
        return f"{self.name}, {self.age}-yr old {self.position}"

    def summary(self):
        if self.experience == 0:
            experience_phrase = "rookie season"
        elif self.experience == 1:
            experience_phrase = "2nd season"
        elif self.experience == 2:
            experience_phrase = "3rd season"
        else:
            experience_phrase = f"{self.experience - 1}th season"
        print(f"{self.name}, {self.age}-yr old {self.position} in {experience_phrase}")

    def _add_season(self):
        self.career_stats.append(Player_Season())
        self.experience += 1

    def _fetch_season(self, season: int) -> Player_Season:
        if not (season == -1 or 1 <= season <= len(self.career_stats)):
            raise KeyError("Season invalid. \n")
        return self.career_stats[-1] if season == -1 else self.career_stats[season - 1]

    def _fetch_game(self, season, week) -> Player_Game:
            # Pass in either an integer specifying the season number, or the entire season
            # Week is either an integer (regular season) or a string specifying playoff round
            if type(season) == int:
                season = self._fetch_season(season)

            if type(week) == int:
                if season.reg_season_games[week - 1] is None:
                    raise KeyError("Game not logged.")
                else:
                    return season.reg_season_games[week - 1]
            else:
                if season.ps_games[week] is None:
                    raise KeyError("Game not logged.")
                else:
                    return season.ps_games[week]

    def delete_game(self, season, week):
        if type(season) == int:
            season = self._fetch_season(season)

        if type(week) == int:
            if season.reg_season_games[week - 1] is None:
                raise KeyError("Game not logged.")
            else:
                season.reg_season_games[week - 1] = None
        else:
            if season.ps_games[week] is None:
                raise KeyError("Game not logged.")
            else:
                season.ps_games[week] = None

    def fetch_fantasy_season(self, season) -> tuple[list[float], float]:
        if type(season) == int:
            season = self._fetch_season(season)
        fseason = [game.fpts for game in season.reg_season_games if game is not None]
        season_fppg = sum(fseason) / len(fseason)
        return fseason, season_fppg

class Quarterback(Player):
    def __init__(self, name: str, position: str, age: int, accuracy: int, strength: int, 
                            speed: int, stamina: int, career: list[Player_Season] = None):
                   
                super().__init__(name, position, age, speed, stamina, career)
                           
                self.accuracy = accuracy
                self.strength = strength

    def to_dict(self):
        return {
            "__type__": "Quarterback",
            "name": self.name,
            "position": self.position,
            "age": self.age,
            "accuracy": self.accuracy,
            "strength": self.strength,
            "speed": self.speed,
            "stamina": self.stamina,
            "career": self.career_stats
            }

    @classmethod
    def from_dict(cls, d: dict):
        return Quarterback(d["name"], d["position"], d["age"], 
                           d["accuracy"], d["strength"], d["speed"], d["stamina"], d["career"])

    def add_game(self, week, opponent, att, cmp, pass_yds, pass_tds, pass_lng, ints, sacks,
                 carries, rush_yds, rush_tds, rush_lng, fum, season: int = -1) -> None:
        # Handle season gaps
        if season != -1:
            while len(self.career_stats) < season:
                self._add_season()
        else: # Season == -1
            if (type(week) == int):
                if self.career_stats[-1].num_ps_games > 0:
                    self._add_season()
                elif self.career_stats[-1].reg_season_games != [None] * 18:
                    for game in self.career_stats[-1].reg_season_games[::-1]:
                        if game is not None:
                            last_logged_game = game
                            break
                    if week < last_logged_game.week:
                        self.add_season

        season = self._fetch_season(season)

        game = Quarterback_Game(week, opponent, att, cmp, pass_yds, pass_tds, pass_lng, ints, sacks, 
                                carries, rush_yds, rush_tds, rush_lng, fum)
        
        if type(week) == int: # Regular season game
            if (season.reg_season_games[week - 1] is not None):
                raise KeyError("Game is already present. Use edit_game() to overwrite.")
            season.reg_season_games[week - 1] = game
            season.num_reg_season_games += 1
        
        elif type(week) == str: # Post-season game
            season.ps_games[week] = game
            season.num_ps_games += 1

    def display_game_stats(self, season, week):
        game = self._fetch_game(season, week)
        
        if type(game.week) == int:
            week_line = f"Week {game.week} vs {game.opponent}"
        else:
            week_line = f"{game.week} round vs {game.opponent}"


        if game.pass_tds == 1:
            pass_tds_line = "1 touchdown"
        else:
            pass_tds_line = f"{game.pass_tds} touchdowns"

        if game.rush_tds == 1:
            rush_tds_line = "1 touchdown"
        else:
            rush_tds_line = f"{game.rush_tds} touchdowns"

        out_lines = [
            week_line,
            f"{game.cmp} completions on {game.att} attempts for {game.pass_yds} yards and {pass_tds_line}",
            f"{game.pass_avg} yards per attempt",
            f"Longest passing play: {game.pass_lng} yards",
            f"{game.rush_yds} yards and {rush_tds_line} on {game.carries} carries",
            f"{game.rush_avg} yards per carry with a longest rush of {game.rush_lng} yards",
            f"Fumbles: {game.fum}",
            f"Fantasy points: {game.fpts}",
        ]
        output = "\n".join(out_lines)

        print(output)

class Runningback(Player):
    def __init__(self, name: str, position: str, age: int, catching: int, strength: int, 
                 speed: int, stamina: int, career: list[Player_Season] = None):
        
        super().__init__(name, position, age, speed, stamina, career)
                
        self.catching = catching
        self.strength = strength

    def to_dict(self):
            return {
                "__type__": "Runningback",
                "name": self.name,
                "position": self.position,
                "age": self.age,
                "catching": self.catching,
                "strength": self.strength,
                "speed": self.speed,
                "stamina": self.stamina,
                "career": self.career_stats
                }

    @classmethod
    def from_dict(cls, d: dict):
        return Runningback(d["name"], d["position"], d["age"], 
                           d["catching"], d["strength"], d["speed"], d["stamina"], d["career"])

    def add_game(self, week, opponent, carries, rush_yds, rush_tds, rush_lng,
                 rec, rec_yds, rec_tds, rec_lng, fum, season: int = -1) -> None:
    
        # Handle season gaps
        if season != -1:
            while len(self.career_stats) < season:
                self._add_season()
        else: # Season == -1
            if (type(week) == int):
                if self.career_stats[-1].num_ps_games > 0:
                    self._add_season()
                elif self.career_stats[-1].reg_season_games != [None] * 18:
                    for game in self.career_stats[-1].reg_season_games[::-1]:
                        if game is not None:
                            last_logged_game = game
                            break
                    if week < last_logged_game.week:
                        self.add_season

        season = self._fetch_season(season)

        game = Runningback_Game(week, opponent, carries, rush_yds, rush_tds, rush_lng, 
                                rec, rec_yds, rec_tds, rec_lng, fum)
        
        if type(week) == int: # Regular season game
            if (season.reg_season_games[week - 1] is not None):
                raise KeyError("Game is already present. Use edit_game() to overwrite.")
            season.reg_season_games[week - 1] = game
            season.num_reg_season_games += 1
        
        elif type(week) == str: # Post-season game
            season.ps_games[week] = game
            season.num_ps_games += 1

    def display_game_stats(self, season, week):
        game = self._fetch_game(season, week)
        
        if type(game.week) == int:
            week_line = f"Week {game.week} vs {game.opponent}"
        else:
            week_line = f"{game.week} round vs {game.opponent}"


        if game.rush_tds == 1:
            rush_tds_line = "1 rushing touchdown"
        else:
            rush_tds_line = f"{game.rush_tds} rushing touchdowns"

        if game.rec_tds == 1:
            
            rec_tds_line = "1 receiving touchdown"
        else:
            rec_tds_line = f"{game.rec_tds} receiving touchdowns"

        out_lines = [
            week_line,
            f"{game.carries} carries",
            f"{game.rush_yds} rushing yards",
            rush_tds_line,
            f"{game.rush_avg} yards per carry",
            f"Longest rush: {game.rush_lng} yards",
            f"{game.rec} receptions",
            f"{game.rec_yds} receiving yards",
            rec_tds_line,
            f"{game.rec_avg} yards per reception",
            f"Longest reception: {game.rec_lng} yards",
            f"Fumbles: {game.fum}",
            f"Fantasy points: {game.fpts}",
        ]
        output = "\n".join(out_lines)

        print(output)

# Receiver class applies to both WRs and TEs
class Receiver(Player):
    def __init__(self, name: str, position: str, age: int, catching: int, strength: int, 
                 speed: int, stamina: int, career: list[Player_Season] = None):
        
        super().__init__(name, position, age, speed, stamina, career)
        
        self.catching = catching
        self.strength = strength

    def to_dict(self):
        return {
            "__type__": "Receiver",
            "name": self.name,
            "position": self.position,
            "age": self.age,
            "catching": self.catching,
            "strength": self.strength,
            "speed": self.speed,
            "stamina": self.stamina,
            "career": self.career_stats
            }

    @classmethod
    def from_dict(cls, d):
        return Receiver(d["name"], d["position"], d["age"], 
                        d["catching"], d["strength"], d["speed"], d["stamina"], d["career"])

    def add_game(self, week, opponent: str, rec: int, rec_yds: int, rec_tds: int ,
                  rec_lng: int, fum: int, season: int = -1) -> None:

        # Handle season gaps
        if season != -1:
            while len(self.career_stats) < season:
                self._add_season()
        else: # Season == -1
            if (type(week) == int):
                if self.career_stats[-1].num_ps_games > 0:
                    self._add_season()
                elif self.career_stats[-1].reg_season_games != [None] * 18:
                    for game in self.career_stats[-1].reg_season_games[::-1]:
                        if game is not None:
                            last_logged_game = game
                            break
                    if week < last_logged_game.week:
                        self.add_season

        season = self._fetch_season(season)

        game = Receiver_Game(week, opponent, rec, rec_yds, rec_tds, rec_lng, fum)
        
        if type(week) == int: # Regular season game
            if (season.reg_season_games[week - 1] is not None):
                raise KeyError("Game is already present. Use edit_game() to overwrite.")
            season.reg_season_games[week - 1] = game
            season.num_reg_season_games += 1
        
        elif type(week) == str: # Post-season game
            season.ps_games[week] = game
            season.num_ps_games += 1

    def display_game_stats(self, season, week):
        game = self._fetch_game(season, week)
        
        if type(game.week) == int:
            week_line = f"Week {game.week} vs {game.opponent}"
        else:
            week_line = f"{game.week} round vs {game.opponent}"

        if game.rec_tds == 1:
            tds_line = "1 receiving touchdown"
        else:
            tds_line = f"{game.rec_tds} receiving touchdowns"

        out_lines = [
            week_line,
            f"{game.rec} receptions",
            f"{game.rec_yds} receiving yards",
            f"{game.rec_avg} yards per reception",
            tds_line,
            f"Longest reception: {game.rec_lng} yards",
            f"Fantasy points: {game.fpts}",
        ]
        output = "\n".join(out_lines)

        print(output)

################################ Data saving, loading, I/O ###############################
def encode(obj):
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def decode(data_dict):
    if data_dict.get("__type__") == "Receiver":
        return Receiver.from_dict(data_dict)
    elif data_dict.get("__type__") == "Runningback":
        return Runningback.from_dict(data_dict)
    elif data_dict.get("__type__") == "Quarterback":
            return Quarterback.from_dict(data_dict)
    elif data_dict.get("__type__") == "Player_Season":
        return Player_Season.from_dict(data_dict)
    elif data_dict.get("__type__") == "Receiver_Game":
        return Receiver_Game.from_dict(data_dict)
    elif data_dict.get("__type__") == "Runningback_Game":
        return Runningback_Game.from_dict(data_dict)
    elif data_dict.get("__type__") == "Quarterback_Game":
            return Quarterback_Game.from_dict(data_dict)
    else:
        return data_dict

def load_data() -> dict[str: Player]:
    if os.path.exists(DATA_STORAGE_FILE):
        with open(DATA_STORAGE_FILE, "r") as f:
            return json.load(f, object_hook=decode)
    else:
        # TODO: Make default return for whatever data is being stored/loaded
        return dict()

def save_data(player_dict):
    with open(DATA_STORAGE_FILE, "w") as f:
        json.dump(player_dict, f, default=encode)

################################ Terminal-interaction / Interface level functions ###############################
def create_player(players: dict[Player], player_name: str) -> None:
    # Adds a Receiver with the inputted data to the player dictionary
    position = input("Create new player. Position? \n")
    age = input("Age? \n")
    skill = input("Skill? \n")
    strength = input("Strength? \n")
    speed = input("Speed? \n")
    stamina = input("Stamina? \n")

    args = (player_name, position, age, skill, strength, speed, stamina)

    if position == "WR" or position == "TE":
        players[player_name] = Receiver(*args)
    elif position == "RB":
        players[player_name] = Runningback(*args)
    elif position == "QB":
        players[player_name] = Quarterback(*args)
    
    print(f"Player {player_name} added to registry.")

def delete_player(players: dict[Player], player_name: str) -> None:
    if players.get(player_name) is not None:
        players.pop(player_name)
        print(players)
        print(f"Player {player_name}'s data erased.")
    else:
        print("Player not in registry.")

def log_game(player: Player):
    ps_game_keys = {"wild card", "divisional", "conference", "super bowl"}
    valid_week_inputs = set([str(v) for v in list(range(1, 19))]).union(ps_game_keys)

    season = int(input("Enter season number or -1 to add to current season. \n"))
    while not (-1 <= season <= 20):
        season = int(input("Enter a season number (1-20), or enter [-1] to add to current season. \n"))

    week = input("Week? \n")
    while week not in valid_week_inputs:
        week = input("Enter a number 1-18 for regular season game or one of 'wild card', 'divisional', 'conference', or 'super bowl' for postseason game. \n")

    if week not in ps_game_keys:
        week = int(week)

    opponent = input("Opponent? \n")

    # Get input for appropriate game stats

    if player.position == "QB":
       cmp = int(input("Passes completed? \n"))
       att = int(input("Passes attempted? \n"))
       pass_yds = int(input("Passing yards? \n"))
       pass_tds = int(input("Passing touchdowns? \n"))
       pass_lng = int(input("Longest passing play? \n"))
       ints = int(input("Interceptions? \n"))
       sacks = int(input("Sacks? \n"))
       

    if player.position == "QB" or player.position == "RB":
        # Input rushing stats
        carries = int(input("Carries? \n"))
        rush_yds = int(input("Rushing yards? \n"))
        rush_tds = int(input("Rushing touchdowns? \n"))
        rush_lng = int(input("Longest rush? \n"))

    if player.position == "RB" or player.position == "WR" or player.position == "TE":
        # Input passing stats
        rec = int(input("Receptions? \n"))
        rec_yds = int(input("Receiving yards? \n"))
        rec_tds = int(input("Receiving touchdowns? \n"))
        rec_lng = int(input("Longest reception? \n"))

    fum = int(input("Fumbles? \n"))

    # Pack all relevant game stats into a tuple and pass that argument tuple into player.add_game()
    if player.position == "QB":
        game_stats = (cmp, att, pass_yds, pass_tds, pass_lng, ints, sacks, carries, rush_yds, rush_tds, rush_lng, fum)
    elif player.position == "RB":
        game_stats = (carries, rush_yds, rush_tds, rush_lng, rec, rec_yds, rec_tds, rec_lng, fum)
    else:
        game_stats = (rec, rec_yds, rec_tds, rec_lng, fum)
    
    try:
        player.add_game(week, opponent, *game_stats, season)
        print("Game added. \n")
    except:
        print("Add game failed. \n")

def display_game(player: Player):
    season = int(input("Season? \n"))
    week = input("Week? \n")

    ps_game_keys = {"wild card", "divisional", "conference", "super bowl"}
    if week not in ps_game_keys:
        week = int(week)

    try:
        player.display_game_stats(season, week)
    except:
        print("Error: Season/game invalid. \n")

def delete_game(player: Player):
    ps_game_keys = {"wild card", "divisional", "conference", "super bowl"}
    valid_week_inputs = set([str(v) for v in list(range(1, 19))]).union(ps_game_keys)

    season = int(input("Enter season number or -1 to add to current season. \n"))
    while not (-1 <= season <= 20):
        season = int(input("Enter a season number (1-20), or enter [-1] for current season. \n"))

    week = input("Week? \n")
    while week not in valid_week_inputs:
        week = input("Enter a number 1-18 for regular season game or one of 'wild card', 'divisional', 'conference', or 'super bowl' for postseason game. \n")

    if week not in ps_game_keys:
        week = int(week)

    try:
        player.delete_game(season, week)
        print("Game deleted. \n")
    except:
        print("Delete game failed. \n")

def delete_player(players: dict[Player], player: Player):
    players.pop(player.name)
