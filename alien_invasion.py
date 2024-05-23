import sys
from time import sleep

import pygame

from settings import Settings
from game_states import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from sound_effects import SoundEffects


class AlienInvasion:
    """ Overall class to manage game assets and behavior """

    def __init__(self):
        """ Initialize the game, and create game resources """
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        pygame.display.set_caption('Alien Invasion')

        # Create instance to store game statistics,
        # and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.sound = SoundEffects()

        self._create_fleet()

        # Make the play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """ Start the main loop for the game """
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()

                self._bullets_update()

                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        """ Respond to key presses and mouse events. """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                high_score_string = str(self.stats.high_score)
                with open('High_score.txt', 'w') as high_score:
                    high_score.write(high_score_string)
                sys.exit()
            elif self.stats.game_active:
                if event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """ Start a new game when the player clicks play. """
        if (self.play_button.rect.collidepoint(mouse_pos)
                and not self.stats.game_active):
            self._start_game()

    def _start_game(self):
        """ Start a new game. """
        # Reset the game settings
        self.settings.initialize_dynamic_settings()
        # Reset the game statistics
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_images()

        # Get rid of any remaining aliens and bullets.
        self.aliens.empty()
        self.bullets.empty()

        # Create a new fleet and center the ship
        self._create_fleet()
        self.ship.center_ship()

        # Hide the mouse cursor
        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """ Respond to key presses """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullets()
            self.sound.play_sound(self.sound.shot)

    def _check_keyup_events(self, event):
        """ Respond to key release """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _create_fleet(self):
        """ Create the fleet of aliens. """
        # Make an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height)
                             - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        # Create an alien and place it in the row.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """ Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """ Drop the entire fleet and change the fleet's direction. """
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _fire_bullets(self):
        """ Create a new bullet and add it to the bullets group. """
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _ship_hit(self):
        """ Respond to the ship being hit by an alien. """
        if self.stats.ship_left > 0:
            # Decrement ship_left.
            self.stats.ship_left -= 1
            self.sb.prep_ships()
            pygame.mixer.Sound.stop(self.sound.shot)
            self.sound.play_sound(self.sound.ship_lose)

            # Get tid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)

        else:
            self.sound.play_sound(self.sound.game_over)
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """ Check if any aliens have reached the bottom of the screen. """
        screen_rect = self.screen.get_rect()
        for alien in self.aliens:
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _bullets_update(self):
        """ Update position of bullets and git ride of old ones """
        # Update bullet positions.
        self.bullets.update()
        # Get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """ Respond to bullet-alien collision. """
        # Check for any bullets that have hit aliens.
        # if so get rid of the bullet and the alien.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sound.play_sound(self.sound.points)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            self._start_new_level()

    def _start_new_level(self):
        """ Start new level after pass one. """
        # Destroy existing bullets and create new fleet.
        self.bullets.empty()
        self._create_fleet()
        self.settings.increase_speed()

        # Increase level
        self.stats.level += 1
        self.sb.prep_level()
        self.sound.play_sound(self.sound.new_level)

    def _update_aliens(self):
        """
        Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _update_screen(self):
        """ Update images on the screen and flip to new screen. """
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screen visible.
        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
