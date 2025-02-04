class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.nome = None
        self.eliminated = False
        self.wins = 0

    def add_win(self):
        self.wins += 1

    def eliminate_player(self):
        self.eliminated = True

    def reset_player(self):
        self.eliminated = False
    

    