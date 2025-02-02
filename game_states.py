class GameStats:
    """ Track statistics for Alien Invasion. """

    def __init__(self, ai_game):
        """ Initialize statistics. """
        self.settings = ai_game.settings
        self.reset_stats()
        # Start Alien Invasion in an inactive state.
        self.game_active = False

        with open("High_score.txt") as high_score:
            h_s = high_score.read()
        self.high_score = int(h_s)

    def reset_stats(self):
        """ Initialize statistics that can chang during the game."""
        self.ship_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        