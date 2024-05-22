import pygame.mixer


class SoundEffects:
    def __init__(self):
        """ Initialize all sound in Alien Invasion"""
        self.shot = pygame.mixer.Sound("sounds/mixkit-game-whip-shot-1512.wav")
        self.new_level = pygame.mixer.Sound("sounds/mixkit-arcade-bonus-alert-767.wav")
        self.game_over = pygame.mixer.Sound("sounds/mixkit-arcade-retro-game-over-213.wav")
        self.ship_lose = pygame.mixer.Sound("sounds/mixkit-cartoon-blow-impact-2654.wav")
        self.points = pygame.mixer.Sound("sounds/mixkit-retro-game-notification-212.wav")

    def play_sound(self, sound):
        pygame.mixer.Sound.play(sound)
