__version__ = "0.3"

from random import choice

import pygame


class Game:
    """The game class."""

    def __init__(self, width, height, game_rect=(0, 0, 328, 328)):
        # Init the display
        self.width, self.height = width, height
        self.game_rect = game_rect
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Pygame Slide Puzzle')
        # Creates the level selector
        self.level_selector = LevelSelector(on_select=self.start)
        # Marks the game as running, but level was not selected yet
        self.running = True
        self.started = False

    def start(self, image_path):
        """Starts the game, loads and shuffles the image."""
        self.puzzle = make_puzzle(image_path, self.game_rect)
        self.puzzle.shuffle(moves=150)
        self.started = True

    def update(self):
        """Processes input events and updates the game."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type != pygame.KEYDOWN:
                continue
            # Pass the control to the level selector if game is not started
            if not self.started:
                self.level_selector.update(event)
            else:
                self.puzzle.update(event)

    def draw(self):
        """Draws either the level selector or the game puzzle."""
        surface = self.screen
        if not self.started:
            self.level_selector.draw(surface)
        else:
            self.puzzle.draw(surface)

    def game_loop(self):
        """Performs the game loop: process input, update screen etc."""
        clock = pygame.time.Clock()
        while self.running:
            elapsed = clock.tick(30)
            self.screen.fill((0, 0, 0))
            self.update()
            self.draw()
            pygame.display.update()
        pygame.quit()


class LevelSelector:
    """The level selector scene."""

    IMAGES = [
        "puzzles/deepelf.png",
        "puzzles/demilich.png",
        "puzzles/dragonwhelp.png",
        "puzzles/fireelemental.png",
        "puzzles/goblinrunts.png",
        "puzzles/goblin.png",
    ]

    def __init__(self, on_select):
        self.on_select = on_select # Callback to start the game
        self._level = 0
        self._images = []
        for image in self.IMAGES:
            self._images.append(load_puzzle_image(image, image_size=(220, 220)))
        self._select = pygame.image.load("select.png").convert_alpha()

    def prev(self):
        """Slide to the previous image."""
        if self._level > 0:
            self._level -= 1

    def next(self):
        """Slide to the next image."""
        if self._level < len(self._images) - 1:
            self._level += 1

    def _current_puzzle(self):
        """Returns the image for the current level."""
        return self._images[self._level]

    def _prev_puzzle(self):
        """Returns the image for the previous level (if exists)."""
        if self._level > 0:
            return self._images[self._level - 1]

    def _next_puzzle(self):
        """Returns the image for the next level (if exists)."""
        if self._level < len(self._images) - 1:
            return self._images[self._level + 1]

    def update(self, event):
        """Processes user's input."""
        if event.type != pygame.KEYDOWN:
            return
        elif event.key == pygame.K_LEFT:
            self.prev()
        elif event.key == pygame.K_RIGHT:
            self.next()
        elif event.key == pygame.K_RETURN:
            self.on_select(self.IMAGES[self._level])

    def draw(self, surface):
        """Draws current state."""
        pos = ((-180, 90), (90, 104), (360, 90))
        levels = (self._prev_puzzle(),
                  self._current_puzzle(),
                  self._next_puzzle())
        # Draws the images at the predefined positions
        for level, p in zip(levels, pos):
            if level is not None:
                surface.blit(level, p)
        # Draws a white border around the current image and the `select puzzle` image
        pygame.draw.rect(surface, (255, 255, 255), (80, 94, 240, 240), 3)
        surface.blit(self._select, (127, 40))


class Puzzle:
    """The puzzle object."""

    def __init__(self, x, y, image_pieces):
        self.x, self.y, self.image_pieces = x, y, image_pieces

    @property
    def rect(self):
        """Returns a rect representing the board."""
        rect = pygame.Rect(self.x, self.y, 0, 0)
        for s in self.image_pieces:
            rect.union_ip(s.rect)
        return rect

    def update(self, event):
        """Processes user's input."""
        if event.type != pygame.KEYDOWN:
            return
        elif event.key == pygame.K_UP:
            self.move('up')
        elif event.key == pygame.K_RIGHT:
            self.move('right')
        elif event.key == pygame.K_DOWN:
            self.move('down')
        elif event.key == pygame.K_LEFT:
            self.move('left')

    def move(self, direction):
        """Move an image piece in the given direction. Possible directions
           are 'up', 'right', 'down' or 'left'."""
        board_rect = self.rect
        x_spacing, y_spacing = (board_rect.width//4,
                                board_rect.height//4)
        x, y = {
            'up':    (0, -y_spacing),
            'right': (x_spacing, 0),
            'down':  (0, y_spacing),
            'left':  (-x_spacing, 0)
        }[direction]

        # Helper function to check if a rect is valid (inside the puzzle)
        is_valid = board_rect.colliderect
        # The current state of the puzzle
        current_pos = set((s.x, s.y) for s in self.image_pieces)
        # Searchs sequentially for the only peice that can be moved
        # to the given direction
        for piece in self.image_pieces:
            new_x, new_y = piece.x + x, piece.y + y
            # Checks if the position is empty and is valid (inside the puzzle).
            if ((new_x, new_y) not in current_pos and is_valid(
                new_x, new_y, piece.width, piece.height)):
                # If everything is ok, then moves the image piece
                piece.x, piece.y = new_x, new_y

    def shuffle(self, moves=100):
        """Shuffles the board applying random moves."""
        for _ in range(moves):
            m = choice(('up', 'right', 'down', 'left'))
            self.move(m)
        # Makes sure the blank space is at the botton-right corner
        self.move('left'), self.move('left'), self.move('left')
        self.move('up'), self.move('up'), self.move('up')

    def draw(self, surface):
        """Draw the image pieces on the surface."""
        for subsurf in self.image_pieces:
            surface.blit(subsurf.image, (subsurf.x, subsurf.y))
        # Draws a white border around the image
        brect = self.rect
        inflated_brect = brect.inflate(int(brect.width * 0.05),
                                       int(brect.height * 0.05))
        pygame.draw.rect(surface, (255, 255, 255), inflated_brect, 3)


class ImagePiece(pygame.sprite.Sprite):
    """A piece (subsuface) of the puzzle image."""

    def __init__(self, x, y, subsurface):
        super(ImagePiece, self).__init__()
        # Saves the initial position of this piece. Used later
        # to check if the puzzle is solved or not.
        self.start_pos = (x, y)
        self.x, self.y = x, y
        self.image = subsurface

    @property
    def width(self):
        return self.image.get_width()

    @property
    def height(self):
        return self.image.get_height()

    @property
    def rect(self):
        return pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )


def make_puzzle(image_path, board_rect):
    """Creates the game puzzle"""
    x, y, width, height = board_rect
    puzzle_image = load_puzzle_image(image_path,
                                     image_size=(width, height))
    image_pieces = list(make_subsurfaces(puzzle_image,
                                         offset=(x, y)))
    # Create the puzzle, leaving out the last piece of the image.
    return Puzzle(x, y, image_pieces[:-1])


def load_puzzle_image(path, image_size):
    """Loads the puzzle image. The image is scaled to the `image_size` param."""
    surface = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(surface, image_size)


def make_subsurfaces(surface, offset=(0, 0)):
    """Cuts the image in small pieces of the same size."""
    width, height = surface.get_size()
    assert width % 4 + height % 4 == 0, (
        "image's dimention is not div by 4: {}".format(surface.get_size()))

    offx, offy = offset
    for y in range(0, height, height//4):
        for x in range(0, width, width//4):
            subsurface = surface.subsurface(x, y, width//4, height//4)
            yield ImagePiece(offx + x, offy + y, subsurface)


if __name__ == '__main__':
    game = Game(
        width=400,
        height=428,
        game_rect=(36, 50, 328, 328)
    )
    game.game_loop()
