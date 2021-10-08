from local import game_log_loc
import os, json
from enum import IntEnum

class game_winner(IntEnum):
    BLUE = 0
    RED = 1

class game_parser():
    def __init__(self, log_team_gold_adv = False, log_team_XP_adv = False):
        self.game_loc = game_log_loc
        self.log_team_gold_adv = log_team_gold_adv
        self.log_team_XP_adv = log_team_XP_adv
        self.gold_adv = []
        self.XP_adv = []
        self.blue_keys = ["1", "2", "3", "4", "5"]
        self.red_keys = ["6", "7", "8", "9", "10"]
        self.dump_file = "data_dump.json"
    
    def get_game_winner(self, game_obj):
        winner = game_obj["info"]["frames"][-1]["events"][-1]["winningTeam"]
   
        if winner == 100:
            return game_winner.BLUE
        elif winner == 200:
            return game_winner.RED
        else:
            print("Error: Could't match winner ({})".format(winner))
            raise ValueError


    def _get_red_xp(self, frame):
        XP = 0
        for key in self.red_keys:
            partFrame = frame["participantFrames"][key]
            XP += partFrame["xp"]
        return XP  
      
    def _get_blue_xp(self, frame):
        XP = 0
        for key in self.blue_keys:
            partFrame = frame["participantFrames"][key]
            XP += partFrame["xp"]
        return XP  
    
    def parse_team_XP_adv(self, game_obj):
        game_XP_chart = []
        for frame in game_obj["info"]["frames"]:
            game_XP_chart.append((frame["timestamp"], self._get_blue_xp(frame), self._get_red_xp(frame)))
        self.XP_adv.append((self.get_game_winner(game_obj), game_XP_chart))
                
    def _get_red_gold(self, frame):
        gold = 0
        for key in self.red_keys:
            partFrame = frame["participantFrames"][key]
            gold += partFrame["totalGold"]
        return gold
    
    def _get_blue_gold(self, frame):
        gold = 0
        for key in self.blue_keys:
            partFrame = frame["participantFrames"][key]
            gold += partFrame["totalGold"]
        return gold
        
    def parse_team_gold_adv(self, game_obj):
        game_gold_chart = []
        for frame in game_obj["info"]["frames"]:
            game_gold_chart.append((frame["timestamp"], self._get_blue_gold(frame), self._get_red_gold(frame)))
        self.gold_adv.append((self.get_game_winner(game_obj), game_gold_chart))
        
    def game_process(self, game_file_name):
        with open(game_file_name) as file:
            game_obj = json.load(file)
            
        if self.log_team_gold_adv:
            self.parse_team_gold_adv(game_obj)
        if self.log_team_XP_adv:
            self.parse_team_XP_adv(game_obj)
        
    def parse_files(self):
        failed = []
        for file_name in os.scandir(self.game_log_directory):
            if file_name.path.endswith(".json") and file_name.is_file():
                try:
                    self.game_process(file_name)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    failed.append((str(file_name), e))
                    
        print("Failed to handle fails:", failed)
    
    def dump_data(self):
        json_obj = {"version" : "1.0.0"}
        if self.log_team_gold_adv:
            json_obj["gold adv"] = self.gold_adv
        if self.log_team_XP_adv:
            json_obj["XP adv"] = self.XP_adv
        
        with open(self.dump_file, "w") as file:
            json.dump(json_obj, file)
        
if __name__ == "__main__":
    gp = game_parser(log_team_gold_adv = True, log_team_XP_adv = True)
    gp.game_process(game_log_loc + "NA1_4061560429.json")
    gp.dump_data()
    print(gp.gold_adv)
    print(gp.XP_adv)
        
        