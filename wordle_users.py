
class WordleUser:
    def __init__(self, name, n_days):
        self.name = name
        self.games = []
        self.n_chats = 0
        self.n_days = n_days

    def add_game(self, game):
        self.games.append(game)

    def add_chat(self):
        self.n_chats += 1

    def total_box_counts(self):
        total = {'green': 0, 'yellow': 0, 'grey': 0}
        for game in self.games:
            counts = game.count_boxes()
            for color in total:
                total[color] += counts[color]
        return total

    def get_stats(self):

        # if len(self.games)>0:

        self.game_score = 0
        self.ones = 0
        self.sixs = 0
        self.losses = 0

        for game in self.games:
          self.game_score += game.score
          self.ones += 1 if game.attempts==1 else 0
          self.sixs += 1 if game.attempts==6 else 0
          self.losses += 1 if game.attempts==None else 0

          
        self.n_missed_games = self.n_days - len(self.games)

        box_dict = self.total_box_counts()
        

        if len(self.games) > 0:
          self.missed_score = self.n_missed_games * game.attempts_score_system["missed"]
          self.average_score = self.game_score/len(self.games)
          self.n_greens = box_dict['green']/len(self.games)
          self.n_yellows = box_dict['yellow']/len(self.games)
        else:
          print(f"{self.name} played zero games")
          self.missed_score = 0
          self.average_score = 0
          self.n_greens = 0
          self.n_yellows = 0

        self.total_score = self.missed_score + self.game_score
        

        return 0
