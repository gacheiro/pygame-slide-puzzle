from random import choice

import pygame


class Game:
    """The game class."""

    def __init__(self, width, height, puzzle_image,
                 game_rect=(0, 0, 328, 328)):
        # Init the display
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Pygame Sliding Puzzle')
        # Creates the game board
        self.puzzle = make_puzzle(puzzle_image, game_rect)
        self.running = False

    def start(self):
        """Starts the game and shuffles the game board."""
        self.puzzle.shuffle(moves=150)
        self.running = True

    def update(self):
        """Processes input events and updates the board."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.puzzle.move('up')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.puzzle.move('right')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.puzzle.move('down')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.puzzle.move('left')

    def draw(self):
        """Draws the game puzzle."""
        surface = self.screen
        self.puzzle.draw(surface)
        # Draws a white border around the image puzzle
        brect = self.puzzle.rect
        inflated_brect = brect.inflate(int(brect.width * 0.05),
                                       int(brect.height * 0.05))
        pygame.draw.rect(surface, (255, 255, 255), inflated_brect, 3)


    def quit(self):
        """Makes the game exit in the next loop."""
        self.running = False

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


class Puzzle(object):
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
        # Makes sure the empty space is at the botton-right corner
        self.move('left'), self.move('left'), self.move('left')
        self.move('up'), self.move('up'), self.move('up')

    def is_solved(self):
        """Returns True if the game is solved."""
        return all(s.start_pos == (s.x, s.y) for s in self)

    def draw(self, surface):
        """Draw the image pieces on the surface."""
        for subsurf in self.image_pieces:
            surface.blit(subsurf.image, (subsurf.x, subsurf.y))


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
        puzzle_image='pygame-badge.png',
        game_rect=(36, 50, 328, 328)
    )
    game.start()
    game.game_loop()
