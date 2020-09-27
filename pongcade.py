# This file is part of Pongcade.
#
# Pongcade is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pongcade is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pongcade.  If not, see <https://www.gnu.org/licenses/>.

import arcade
import random

# Constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Pongcade"

CHARACTER1_SCALING = 0.2
CHARACTER2_SCALING = 0.2
BALL1_SCALING = 0.1
PLAYER_MOVEMENT_SPEED = 7
BALL_MOVEMENT_SPEED_X = 10
BALL_MOVEMENT_SPEED_MIN_X = 5
BALL_MOVEMENT_SPEED_Y = 10
GAME_WIN_SCORE = 5

# Game state constants
GAME_STATE_WAIT = 0
GAME_STATE_ACTIVE = 1
GAME_STATE_END = 2


class Pongcade(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.wall_list = None
        self.player_list = None
        self.player1_sprite = None
        self.player2_sprite = None
        self.ball_list = None
        self.ball1_sprite = None
        self.score1 = 0
        self.score2 = 0
        self.sound_score = None
        self.sound_hit_player1 = None
        self.sound_hit_player2 = None
        self.sound_bounce = None
        self.game_state = None

    def setup(self):
        """Set up the game"""
        self.player_list = arcade.SpriteList()
        self.ball_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        # Set up the players
        player1_image_source = "resources/images/clown.png"
        player2_image_source = "resources/images/sheep.png"
        self.player1_sprite = arcade.Sprite(player1_image_source, CHARACTER1_SCALING)
        self.player2_sprite = arcade.Sprite(player2_image_source, CHARACTER2_SCALING)
        self.player1_sprite.center_x = 100
        self.player1_sprite.center_y = SCREEN_HEIGHT/2
        self.player2_sprite.center_x = SCREEN_WIDTH - 100
        self.player2_sprite.center_y = SCREEN_HEIGHT/2
        self.player_list.append(self.player1_sprite)
        self.player_list.append(self.player2_sprite)

        # Set up balls
        ball1_image_source = "resources/images/ball-sun.png"
        self.ball1_sprite = arcade.Sprite(ball1_image_source, BALL1_SCALING)
        self.set_default_ball_position()
        self.ball_list.append(self.ball1_sprite)

        # Start moving the ball
        self.set_game_state(GAME_STATE_WAIT)

        # Score
        self.score1 = 0
        self.score2 = 0

        # Sounds
        self.sound_score = arcade.load_sound("resources/sound/score.wav")
        self.sound_hit_player1 = arcade.load_sound("resources/sound/hit-player1.wav")
        self.sound_hit_player2 = arcade.load_sound("resources/sound/hit-player2.wav")
        self.sound_bounce = arcade.load_sound("resources/sound/bounce.wav")

    def on_draw(self):
        """Render the screen"""
        arcade.start_render()
        # Players and ball
        self.player_list.draw()
        self.ball_list.draw()
        # Score
        score = f"{self.score1} --- {self.score2}"
        arcade.draw_text(score, SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT - 40, arcade.color.WHITE, 30)
        # End of game
        if self.game_state == GAME_STATE_END:
            if self.score1 == GAME_WIN_SCORE:
                player = "player 1"
            else:
                player = "player 2"
            end_message = f"{player} wins!"
            arcade.draw_text(end_message, SCREEN_WIDTH/2 - 300, SCREEN_HEIGHT/2 - 40, arcade.color.WHITE, 80)

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.F:
            self.set_fullscreen(not self.fullscreen)
            self.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        elif key == arcade.key.SPACE and self.game_state == GAME_STATE_WAIT:
            self.set_game_state(GAME_STATE_ACTIVE)
        elif key == arcade.key.SPACE and self.game_state == GAME_STATE_END:
            # Game had ended, set up for next game
            self.score1 = 0
            self.score2 = 0
            self.set_game_state(GAME_STATE_WAIT)
        elif key == arcade.key.UP:
            self.player2_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player2_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.W:
            self.player1_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.S:
            self.player1_sprite.change_y = -PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key: int, modifiers: int):
        if key == arcade.key.UP:
            self.player2_sprite.change_y = 0
        elif key == arcade.key.DOWN:
            self.player2_sprite.change_y = 0
        elif key == arcade.key.W:
            self.player1_sprite.change_y = 0
        elif key == arcade.key.S:
            self.player1_sprite.change_y = 0

    def on_update(self, delta_time: float):
        self.player_list.update()
        self.ball_list.update()

        # Score
        if self.ball1_sprite.center_x < 0 or self.ball1_sprite.center_x > SCREEN_WIDTH:
            if self.ball1_sprite.center_x < 0:
                self.score2 += 1
            if self.ball1_sprite.center_x > SCREEN_WIDTH:
                self.score1 += 1
            self.set_default_ball_position()
            arcade.play_sound(self.sound_score)
            if self.score1 == GAME_WIN_SCORE or self.score2 == GAME_WIN_SCORE:
                self.set_game_state(GAME_STATE_END)
            else:
                self.set_game_state(GAME_STATE_WAIT)

        # If ball hits wall, bounce off
        if self.ball1_sprite.center_y < 0 or self.ball1_sprite.center_y > SCREEN_HEIGHT:
            self.ball1_sprite.change_y = -self.ball1_sprite.change_y
            arcade.play_sound(self.sound_bounce)

        # If ball hits a player kick it in opposite direction
        if arcade.check_for_collision(self.ball1_sprite, self.player1_sprite):
            rand_speed_x = random.randint(BALL_MOVEMENT_SPEED_MIN_X, BALL_MOVEMENT_SPEED_X)
            self.ball1_sprite.change_x = abs(rand_speed_x)
            arcade.play_sound(self.sound_hit_player1)
        if arcade.check_for_collision(self.ball1_sprite, self.player2_sprite):
            rand_speed_x = random.randint(BALL_MOVEMENT_SPEED_MIN_X, BALL_MOVEMENT_SPEED_X)
            self.ball1_sprite.change_x = -abs(rand_speed_x)
            arcade.play_sound(self.sound_hit_player2)

    def set_default_ball_position(self):
        self.ball1_sprite.center_x = SCREEN_WIDTH / 2
        self.ball1_sprite.center_y = SCREEN_HEIGHT / 2

    def set_game_state(self, state):
        if self.game_state != state:
            if state == GAME_STATE_ACTIVE:
                rand_dir_x = random_direction()
                rand_speed_x = random.randint(BALL_MOVEMENT_SPEED_MIN_X, BALL_MOVEMENT_SPEED_X)
                self.ball1_sprite.change_x = rand_dir_x * rand_speed_x
                rand_dir_y = random_direction()
                self.ball1_sprite.change_y = rand_dir_y * BALL_MOVEMENT_SPEED_Y
            elif state == GAME_STATE_WAIT:
                self.ball1_sprite.change_x = 0
                self.ball1_sprite.change_y = 0
            elif state == GAME_STATE_END:
                self.ball1_sprite.change_x = 0
                self.ball1_sprite.change_y = 0
            self.game_state = state


def random_direction():
    return 1 if random.random() < 0.5 else -1


def main():
    window = Pongcade()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
