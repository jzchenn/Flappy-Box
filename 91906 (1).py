"""Flappy bird program made using Tkinter."""
from tkinter import *
import random


class Gui:
    """Handle the graphical interface and game logic for Flappy bird.

    Attributes:
        CANVAS_LENGTH (int): Height of the game canvas.
        CANVAS_WIDTH (int): Width of the game canvas.
        OBSTACLES_GAP (int): The gap between the obstacles.
        UP_KEYBIND (list): The list of keys.
        NORMAL_TEXT_SIZE (int): The text size for instructions and score.
        GAME_OVER_TEXT_SIZE (int): The text size for game over.
        AFTER_CALL_RATE (int): The rate of after call.
        INSTRUCTION_POSITION_RATIO (float): The position of instruction's text.
        BACKGROUND_COLOR (str): The hex code of the background color.
        SCORE_Y_POSITION (int): The y position of the instruction text.
        SCORE_X_POSITION (int): The x position of the instruction text.
    """

    CANVAS_LENGTH = 480  # Default length is 480.
    CANVAS_WIDTH = 640   # Default width is 640
    # Resolution should be defaulted to 640x512
    # The aspect ratio 4:3 is the most common ratios for standard monitor.
    OBSTACLES_GAP = 500
    NORMAL_TEXT_SIZE = 10
    GAME_OVER_TEXT_SIZE = 50
    AFTER_CALL_RATE = 16
    # After testing, 16 feels the smoothest for the computer I use.
    # This could be adjusted according to the refresh rate of monitors.
    INSTRUCTION_POSITION_RATIO = 4/5

    BACKGROUND_COLOR = "#93fffe"
    # Sky blue color hex code.
    UP_KEYBIND = [
        "KeyPress-space",
        "KeyPress-Up",
        "KeyPress-w",
        "Button-1"
    ]
    SCORE_Y_POSITION = 100
    SCORE_X_POSITION = 50

    def __init__(self):
        """Initialize the GUI for the Flappy Bird game.

        Instance Attribute:
            _window (Tk): The Tkinter window.
            _game_on (bool): Game condition.
            _score (int): The score of the player, initially set to 0.
            _game_canvas (Canvas): Canvas where player and obstacle are drawn.
            _floor (Floor): The floor of the game.
            _obstacle (list): List of the obstacles.
            _player (Player): The player.
        """
        self._window = Tk()
        self._after_call = None
        self._game_on = False
        self._score = 0
        self._game_canvas = Canvas(self._window,
                                   width=self.CANVAS_WIDTH,
                                   height=self.CANVAS_LENGTH,
                                   background=self.BACKGROUND_COLOR)
        self._floor = Floor(self._game_canvas,
                            self.CANVAS_WIDTH,
                            self.CANVAS_LENGTH)

        self._obstacles = [self.create_obstacle()]
        self._player = Player(self._game_canvas,
                              self,
                              self._floor,
                              self._obstacles,
                              self.CANVAS_WIDTH / 2,
                              # Middle of the canvas.
                              self.CANVAS_LENGTH / 2)
        # Keybindings
        self._key_list = set()
        for key_binds in self.UP_KEYBIND:
            self._window.bind(f"<{key_binds}>", self.up_keypress)
        self._window.bind("<KeyPress-r>", self.restart_game)

        self._game_canvas.create_text(
            # Scales the position of text according to canvas width.
            # Divide by 2 so text would be in the center of the canvas width.
            self.CANVAS_WIDTH/2,
            self.CANVAS_LENGTH*self.INSTRUCTION_POSITION_RATIO,
            text="Press SPACE to start game\n"
                 "Keep tapping SPACE to flap and "
                 "avoid hitting the ground or the incoming obstacle!",
            fill="black",
            font=(
                f'Helvetica '
                f'{self.NORMAL_TEXT_SIZE} '
                f'bold'
            ),
            tags=('instructions',)
        )
        self._score_text = self._game_canvas.create_text(
            self.SCORE_Y_POSITION,
            self.SCORE_X_POSITION,
            text=f"Amount of obstacle passed: {self._score}",
            font=(
                f'Helvetica '
                f'{self.NORMAL_TEXT_SIZE} '
                f'bold'),
        )
        self._game_canvas.pack()
        self._window.resizable(False, False)

        self._window.mainloop()

    def create_obstacle(self):
        """Create and return a new obstacle."""
        return Obstacle(self._game_canvas,
                        self,
                        self.CANVAS_WIDTH,
                        self._floor.return_coord()[1])

    def change_game_condition(self, condition):
        """Change the condition of game.

        Parameter:
            condition (bool): The condition of game.
        """
        self._game_on = condition

    def return_game_condition(self):
        """Return the game condition."""
        return self._game_on

    def game_over_text(self):
        """Create texts when game is over."""
        self._game_canvas.create_text(
            # Draw at the center of screen.
            self.CANVAS_WIDTH / 2,
            self.CANVAS_LENGTH / 2,
            text="You Crashed!\n"
                 "Press R to Restart",
            fill="red",
            font=(
                f'Helvetica '
                f'{self.GAME_OVER_TEXT_SIZE} '
                f'bold'
            ),
            tags=('game over',)
        )

    def restart_game(self, reset_pressed):
        """Restart the game.

        Parameter:
            reset_pressed (str): Key pressed.
        """
        if not self._game_on:
            self._score = 0
            self._player.return_starting_position()
            self._game_canvas.delete('game over')
            for obstacles in self._obstacles[:]:
                obstacles.delete_obstacle()
            self._obstacles.clear()
            self._obstacles.append(self.create_obstacle())
            self._after_call = None

    def up_keypress(self, up_pressed):
        """Start the game and make the player go up.

        Parameter:
            up_pressed (str): Key pressed.
        """
        if not self._game_on:
            self.change_game_condition(True)
            self._game_canvas.delete('instructions')
            self._player.up()
            if self._after_call is None:
                self.moving()
        else:
            self._player.up()

    def add_score(self):
        """Increase score by one."""
        self._score += 1

    def moving(self):
        """Update the game state.

        When game is active,
        update player and obstacle position.
        """
        Player.move(self._player)
        self._game_canvas.tag_raise(self._score_text)
        last_obstacle = self._obstacles[-1]
        if ((last_obstacle.return_top_obstacle_coords()[2])
                <= self.OBSTACLES_GAP):
            self._obstacles.append(self.create_obstacle())
        for obstacles in self._obstacles:
            Obstacle.move(obstacles)
            if (self._player.return_player_coords()[0] >=
                    obstacles.return_top_obstacle_coords()[2] and
                    not obstacles.return_scored()):
                self.add_score()
                obstacles.has_scored()
            if obstacles.return_top_obstacle_coords()[2] <= 0:
                self._obstacles.remove(obstacles)
                obstacles.delete_obstacle()

        self._game_canvas.itemconfig(
            self._score_text,
            text=f"Amount of obstacle passed: {self._score}"
        )
        if self._game_on:
            self._after_call = self._window.after(
                self.AFTER_CALL_RATE,
                self.moving
            )
        else:
            self._after_call = None


class Floor:
    """Construct a floor object for the game.

    Attributes:
        FLOOR_POSITION_RATIO (int): The position of floor.
    """

    FLOOR_POSITION_RATIO = 15/16

    def __init__(self, canvas, x, y):
        """Initialize floor with canvas, width and height.

        Parameters:
            canvas (Canvas): The game canvas.
            x (int): The canvas's width size.
            y (int): The canvas's height size.

        Instance Attributes:
            _canvas (Canvas): The canvas where floor is drawn.
            _floor_id (Floor): Floor object.

        """
        self._canvas = canvas
        self._floor_id = self._canvas.create_rectangle(
            0,
            y * self.FLOOR_POSITION_RATIO,
            x,
            y,
            fill="green"
        )

    def return_coord(self):
        """Return the coord of the floor object."""
        return self._canvas.coords(self._floor_id)


class Obstacle:
    """Construct obstacle object for the game.

    Attributes:
        PLAYER_PASS_GAP (int): The size of the gap between top & bot obstacle.
        WIDTH (int): The width of the obstacle.
        MINIMUM_HEIGHT (int): The minimum height of the obstacles.
        OBSTACLE_MOVEMENT_SPEED (int): The movement speed of obstacle.
        OBSTACLE_OFFSET (int): The offset of the obstacle.
    """

    PLAYER_PASS_GAP = 150
    WIDTH = 70
    MINIMUM_HEIGHT = 50
    OBSTACLE_MOVEMENT_SPEED = 2
    OBSTACLE_OFFSET = 5

    def __init__(self, canvas, gui, x, y):
        """Initialize the obstacle object.

        Parameters:
            canvas (Canvas): The game canvas where obstacle is drawn.
            gui (Gui): The Gui object.
            x (int): The size of the canvas width.
            y (float): The size of the canvas height with floor.
        Instance Attribute:
            _canvas (Canvas): The game canvas.
            _gui (Gui): The Gui object.
            _scored (bool): Indicate if player has scored from this obstacle.
            _top_height (int): The height of the top obstacle.
        """
        self._canvas = canvas
        self._gui = gui
        self._scored = False
        self._top_height = random.randint(
            self.MINIMUM_HEIGHT,
            int(y) - self.PLAYER_PASS_GAP - self.MINIMUM_HEIGHT
        )
        self._top_obstacle = self._canvas.create_rectangle(
            # Spawns with offset so player can't see the edge of obstacle.
            x + self.OBSTACLE_OFFSET,
            0,
            x + self.WIDTH,
            self._top_height,
            fill="orange",
        )
        self._bot_obstacle = self._canvas.create_rectangle(
            # Spawns with offset so player can't see the edge of obstacle.
            x + self.OBSTACLE_OFFSET,
            y,
            x + self.WIDTH,
            self._top_height + self.PLAYER_PASS_GAP,
            fill="orange"
        )

    def move(self):
        """Handle the movement of top and bottom obstacle."""
        if self._gui.return_game_condition():
            # The y velocity is 0 because don't need it to move vertically.
            self._canvas.move(self._top_obstacle,
                              -self.OBSTACLE_MOVEMENT_SPEED,
                              0)
            self._canvas.move(self._bot_obstacle,
                              -self.OBSTACLE_MOVEMENT_SPEED,
                              0)

    def return_top_obstacle_coords(self):
        """Return the top obstacle's coordinates."""
        return self._canvas.coords(self._top_obstacle)

    def return_bot_obstacle_coords(self):
        """Return the bot obstacle's coordinates."""
        return self._canvas.coords(self._bot_obstacle)

    def return_scored(self):
        """Return _scored."""
        return self._scored

    def has_scored(self):
        """Set _scored to True.

        The player has scored through this obstacle.
        """
        self._scored = True

    def delete_obstacle(self):
        """Delete the obstacles from canvas."""
        self._canvas.delete(self._top_obstacle)
        self._canvas.delete(self._bot_obstacle)


class Player:
    """Construct a player object.

    Attributes:
        PLAYER_SIZE (int): Size of the player.
        PLAYER_JUMP_STRENGTH (int): The jump strength of player.
        GRAVITY_ACCELERATION (int): The gravity simulation fall speed.
    """

    PLAYER_SIZE = 20
    PLAYER_JUMP_STRENGTH = 10
    GRAVITY_ACCELERATION = 1

    def __init__(self, canvas, gui, floor, obstacle, x, y):
        """Initialize the player object.

        Parameter:
            canvas (Canvas): The game canvas where player is drawn.
            gui (Gui): The gui object.
            floor (Floor): The floor of the game.
            obstacle (list): The list of obstacle objects.
            x (float): The width of the game canvas.
            y (float): The height of the game with floor.
        Instances Attribute:
            _original_position (list): The player's starting coordinates.
            _y_vel (int): The vertical velocity of player.
            _jump (bool): Check if the player has jumped already.
        """
        self._canvas = canvas
        self._gui = gui
        self._floor = floor
        self._obstacles = obstacle
        self._player_id = canvas.create_rectangle(
            # Makes the centroid of the player to be on the centroid of canvas.
            x - self.PLAYER_SIZE,
            y - self.PLAYER_SIZE,
            x + self.PLAYER_SIZE,
            y + self.PLAYER_SIZE,
            fill="white"
        )
        self._original_position = self._canvas.coords(self._player_id)
        self._y_vel = 0
        self._jump = False

    def return_starting_position(self):
        """Return the player to the starting position."""
        self._canvas.coords(
            self._player_id,
            self._original_position
        )

    def return_player_coords(self):
        """Return the player's coordinates."""
        return self._canvas.coords(self._player_id)

    def up(self):
        """Set the _jump to True.

        The player has jumped.
        """
        self._jump = True

    def move(self):
        """Handle the movements of player."""
        # The x vel is 0 because don't need it to move horizontally.
        self._canvas.move(
            self._player_id,
            0,
            self._y_vel
        )
        self.collision()

        if self._gui.return_game_condition():
            if self._jump:
                self._y_vel = -self.PLAYER_JUMP_STRENGTH
                self._jump = False
            else:
                self._y_vel += self.GRAVITY_ACCELERATION

    def collision(self):
        """Handle the collision of player."""
        player_coords = self.return_player_coords()
        player_height = player_coords[3] - player_coords[1]
        # Boundary Collision
        floor_y1_coord = (self._floor.return_coord())[1]
        if player_coords[3] >= floor_y1_coord:
            # If player's bottom face hits bottom boundary.
            self._y_vel = 0
            self._gui.change_game_condition(False)
            self._gui.game_over_text()
            self._canvas.coords(self._player_id,
                                player_coords[0],
                                floor_y1_coord -
                                player_height,
                                player_coords[2],
                                floor_y1_coord)

        if player_coords[1] < 0:
            # If player's top face hits top boundary.
            self._canvas.coords(
                self._player_id,
                player_coords[0],
                0,
                player_coords[2],
                player_height
            )
        # Obstacle Collision
        for obstacles in self._obstacles:
            top_coord = obstacles.return_top_obstacle_coords()
            bot_coord = obstacles.return_bot_obstacle_coords()
            if (
                    (
                        # If player is inside top pipe.
                        player_coords[2] > top_coord[0] and
                        player_coords[0] < top_coord[2] and
                        player_coords[1] <= top_coord[3]
                    )
                    or
                    (
                        # If player is inside bottom pipe.
                        player_coords[2] > bot_coord[0] and
                        player_coords[0] < bot_coord[2] and
                        player_coords[3] >= bot_coord[1]
                    )
            ):
                self._y_vel = 0
                self._gui.change_game_condition(False)
                self._gui.game_over_text()
                # If the player is fully within the obstacle pass gap.
                if (player_coords[0] > top_coord[0] and
                        player_coords[2] < top_coord[2]):
                    if player_coords[1] <= top_coord[3] <= player_coords[3]:
                        self._canvas.coords(
                            self._player_id,
                            player_coords[0],
                            top_coord[3],
                            player_coords[2],
                            top_coord[3] + player_height
                        )
                    if player_coords[1] <= bot_coord[1] <= player_coords[3]:
                        self._canvas.coords(
                            self._player_id,
                            player_coords[0],
                            bot_coord[1] - player_height,
                            player_coords[2],
                            bot_coord[1]
                        )


Gui()
