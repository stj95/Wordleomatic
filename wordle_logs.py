from wordle_users import WordleUser
from datetime import datetime

class WordleLog:
    def __init__(self, startdate, enddate):
        self.users = {}
        self.wordle_squares = ['🟩', '🟨', '⬛', '⬜']
        self.start_date = startdate
        self.end_date = enddate
        self.n_days = (self.end_date.value - self.start_date.value).days + 1


    def get_or_create_user(self, name):
        if name not in self.users:
            self.users[name] = WordleUser(name, self.n_days)
        return self.users[name]

    def parse_lines(self, lines):
        i = 0
        while i < len(lines):
          line = lines[i]
          if ': Wordle' in line and line[-2]=='/':
                try:
                    
                    # Extract timestamp
                    prefix = line.split(', ', 1)
                    
                    if len(prefix) < 2:
                      i += 1
                      continue

                    date_part = prefix[0].strip()
                    time_and_rest = prefix[1].split(' - ', 1)
                    if len(time_and_rest) < 2:
                      i += 1
                      continue


                    time_part = time_and_rest[0].replace('\u202f', ' ').strip()
                    timestamp_str = f"{date_part} {time_part}"

                    try:
                        timestamp = datetime.strptime(timestamp_str, "%m/%d/%y %I:%M %p")
                    except ValueError:
                        timestamp = datetime.strptime(timestamp_str, "%m/%d/%y %H:%M")

                    # ✅ Filter by date range
                    if self.start_date.value and timestamp.date() < self.start_date.value:
                      i += 1
                      continue

                    if self.end_date.value and timestamp.date() > self.end_date.value:
                      i += 1
                      continue

                    meta = line.split(' - ', 1)[1]
                    sender, rest = meta.split(':', 1)
                    user = self.get_or_create_user(sender.strip())

                    wordle_info = rest.strip().split()
                    puzzle_number = int(wordle_info[1].replace(',', ''))
                    score_raw = wordle_info[2].split('/')[0]
                    success = score_raw.upper() != 'X'
                    attempts = int(score_raw) if success else None

                    # Look ahead for emoji grid
                    grid_lines = []
                    j = i + 2
                    
                    while j < len(lines) and any(c in lines[j] for c in self.wordle_squares):
                        
                        grid_lines.append(lines[j].strip())
                        j += 1
                    
                    game = WordleGame(timestamp, puzzle_number, attempts, success, grid_lines)
                    user.add_game(game)
                    i = j   # advance the main index to skip grid lines
                except Exception as e:
                    print(f"Failed to parse Wordle message: {line}\nError: {e}")
          else:
              try:
                    meta = line.split(' - ', 1)[1]
                    sender, rest = meta.split(':', 1)
                    user = self.get_or_create_user(sender.strip())
                    user.add_chat()

              except Exception as e:
                    pass
                    # print(f"Failed to parse Wordle message: {line}\nError: {e}")
              
              i += 1



class WordleGame:

    def __init__(self, date, puzzle_number, attempts, success, grid_lines):
        self.date = date
        self.puzzle_number = puzzle_number
        self.attempts = attempts  # int or None
        self.success = success  # True/False
        self.grid = grid_lines  # list of strings like '⬛⬛⬛⬛🟨'
        self.tile_score_system = {
          'green': 1,
          'yellow': 2,
          'grey': 0
        }
        self.attempts_score_system = {
          1: -10,
          2: -5,
          3: -2,
          4: 1,
          5: 3,
          6: 5,
          None: 10,
          "missed": 12 
        }
        self.score = self.calculate_score()
    
    def count_boxes(self):
        from collections import Counter
        flat = ''.join(self.grid)
        # print(self.grid)
        # print(flat)
        counter = Counter(flat)
        return {
            'green': counter.get('🟩', 0),
            'yellow': counter.get('🟨', 0),
            'grey': counter.get('⬛', 0)
        }

    def calculate_score(self):
      
      attempts_score = self.attempts_score_system[self.attempts]

      box_dict = self.count_boxes()
      n_green = box_dict['green']
      n_yellow = box_dict['yellow']
      n_grey = box_dict['grey']

      green_score = n_green * self.tile_score_system["green"]
      yellow_score = n_yellow * self.tile_score_system["yellow"]
      grey_score = n_grey * self.tile_score_system["grey"]
      
      total_score = attempts_score + green_score + yellow_score + grey_score
      
      return total_score
