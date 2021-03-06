from datetime import datetime

MIN_YEAR = -9999
MAX_GUESSES = 8

hints = {5: {'color': 'black', 'min': 201, 'max': float('inf'), 'text': 'over 200 years off', 'emoji': '⬛'},
         4: {'color': 'brown', 'min': 41, 'max': 200, 'text': '41-200 years off', 'emoji': '🟫'},
         3: {'color': 'red', 'min': 11, 'max': 40, 'text': '11-40 years off', 'emoji': '🟥'},
         2: {'color': 'orange', 'min': 3, 'max': 10, 'text': '3-10 years off', 'emoji': '🟧'},
         1: {'color': 'yellow', 'min': 1, 'max': 2, 'text': '1-2 years off', 'emoji': '🟨'},
         0: {'color': 'green', 'min': 0, 'max': 0, 'text': 'Nailed it!', 'emoji': '🟩'}
         }


def greg_to_astr(year):
    """Convert Gregorian year to astronomical year to account for missing year zero in calculations."""
    if year < 0:
        year += 1
    return year


def astr_to_greg(year):
    """Convert astronomical year back to Gregorian year."""
    if year < 1:
        year -= 1
    return year


class GuessRange:
    def __init__(self, min_yr=float('-inf'), max_yr=float('inf')):
        self.min_yr = min_yr
        self.max_yr = max_yr

    def __and__(self, other):
        if self.min_yr > other.max_yr or other.min_yr > self.max_yr:
            return GuessRange()
        else:
            new_min_yr = max(self.min_yr, other.min_yr)
            new_max_yr = min(self.max_yr, other.max_yr)
            return GuessRange(new_min_yr, new_max_yr)

    def __bool__(self):
        if self.min_yr == float('-inf'):
            return False
        else:
            return True

    def __str__(self):
        return f"{astr_to_greg(self.min_yr)} ... {astr_to_greg(self.max_yr)}"

    def bisect(self):
        return (self.min_yr + self.max_yr) // 2


class YeardleGame:
    def __init__(self):
        self.min_yr = greg_to_astr(MIN_YEAR)
        self.max_yr = greg_to_astr(datetime.now().year)
        self.guess_ranges = [GuessRange(self.min_yr, self.max_yr)]
        self.guess_count = 0
        self.guesses = []
        self.lastguess = float('-inf')

    def set_guess(self, guess_yr):
        self.guesses.append(guess_yr)
        self.lastguess = guess_yr
        self.guess_count += 1

    def calc_ranges(self, hint):
        up_and_down = []

        down_min = self.lastguess - hints[hint]['min']
        if down_min >= self.min_yr:
            down_max = max(self.min_yr, (self.lastguess - hints[hint]['max']))
            up_and_down.append(GuessRange(down_max, down_min))

        up_min = self.lastguess + hints[hint]['min']
        if up_min <= self.max_yr:
            up_max = min(self.max_yr, (self.lastguess + hints[hint]['max']))
            up_and_down.append(GuessRange(up_min, up_max))

        new_ranges = []
        for old_range in self.guess_ranges:
            for curr_range in up_and_down:
                new_range = old_range & curr_range
                if new_range:
                    new_ranges.append(new_range)

        self.guess_ranges = new_ranges


def print_game(game):
    strs = [''] * MAX_GUESSES
    for i, yr in enumerate(game.guesses):
        strs[i] = str(astr_to_greg(yr))
    strs[len(game.guesses)] = '_____'
    strs = [' '.join(list(string)).rjust(9) for string in strs]
    print(f'''\
\t╔═════════════╦═════════════╗
\t║  {strs[0]}  ║  {strs[4]}  ║
\t╠═════════════╬═════════════╣
\t║  {strs[1]}  ║  {strs[5]}  ║
\t╠═════════════╬═════════════╣
\t║  {strs[2]}  ║  {strs[6]}  ║
\t╠═════════════╬═════════════╣
\t║  {strs[3]}  ║  {strs[7]}  ║
\t╚═════════════╩═════════════╝''')


def print_ranges(game):
    if game.guess_count == 0:
        print(f"Allowed range of years: {game.guess_ranges[0]}")
    else:
        print("Possible guesses:\n")
        max_r_str_len = 0
        for r in game.guess_ranges:
            if len(str(r)) > max_r_str_len:
                max_r_str_len = len(str(r))
        if len(game.guess_ranges) == 0:
            print("\tNone")
        for r in game.guess_ranges:
            print(f"\t{str(r).rjust(max_r_str_len)} -> Suggested guess: {astr_to_greg(r.bisect())}")


def print_hint_menu():
    print("What was Yeardle's response to your guess?\n")
    for i, hint in hints.items():
        print(f"\t{i}: {hint['color'].title()}")


def input_year(min_yr, max_yr):
    while True:
        guess = input("Enter your guess: ")
        if guess == '0':
            print("Year zero does not exist!\n")
            continue
        if guess.isdecimal() or (guess.replace('-', '', 1).isdecimal() and guess[0] == '-'):
            guess_yr = greg_to_astr(int(guess))
        else:
            print("Not a valid number!\n")
            continue
        if guess_yr < min_yr or guess_yr > max_yr:
            print("Year out of range!\n")
            continue
        return guess_yr


def input_hint():
    while True:
        hint = input("Response? ")
        if hint.isdecimal():
            hint = int(hint)
        if hints.get(hint) is None:
            print("Not a valid answer.\n")
            continue
        return hint


def main():
    print("Welcome!\n")
    game = YeardleGame()
    
    while True:
        print("-" * 50)
        print(f"Guess # {game.guess_count+1}")
        # Print current state of the game
        print()
        print_game(game)
        print()
        print_ranges(game)
        print()
        # Ask user to input a year
        guess_yr = input_year(game.min_yr, game.max_yr)
        game.set_guess(guess_yr)
        # Print hint menu
        print()
        print_hint_menu()
        print()
        # Ask user to input Yeardle's hint
        hint = input_hint()
        print(f"-> {hints[hint]['text']}\n")
        # Check if game is done
        if hint == 0:
            print(f"Year: {astr_to_greg(game.lastguess)}\nGuesses: {game.guess_count}\n")
            break
        if game.guess_count == MAX_GUESSES:
            print("Your guesses are up. Better luck next time!\n")
            break
        # Calculate new possible ranges
        game.calc_ranges(hint)

    input("Enter to quit.")


if __name__ == "__main__":
    main()
