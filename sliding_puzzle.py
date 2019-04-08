from random import choice

import pygame


class Game:

    def __init__(self, 
        width, height, puzzle_image, caption='', board_rect=(0, 0, 328, 328)):
        
            self.width, self.height = width, height

            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(caption)
            
            self.board = make_board(puzzle_image, board_rect)
            self.running = False

    def start(self):
        self.board.randomize(n=150)
        self.running = True

    def update(self, elapsed):
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            elif (event.type == pygame.KEYDOWN
                and event.key == pygame.K_UP):
                    self.board.move('up')

            elif (event.type == pygame.KEYDOWN
                and event.key == pygame.K_RIGHT):
                    self.board.move('right')

            elif (event.type == pygame.KEYDOWN
                and event.key == pygame.K_DOWN):
                    self.board.move('down')

            elif (event.type == pygame.KEYDOWN
                and event.key == pygame.K_LEFT):
                    self.board.move('left')

    def draw(self, surface=None):
        if surface is None:
            surface = self.screen

        self.board.draw(surface)
        
        brect = self.board.rect
        inflated_brect = brect.inflate(brect.width * 0.05, brect.height * 0.05)
        
        pygame.draw.rect(surface, (255, 255, 255), inflated_brect, 3)

        
    def quit(self):
        self.running = False
        
    def game_loop(self):
        
        clock = pygame.time.Clock()

        while self.running:
            
            elapsed = clock.tick(60)
            self.update(elapsed)

            self.screen.fill((0, 0, 0))
            self.draw()

            pygame.display.update()

        pygame.quit()


class Board(object):

    def __init__(self, x, y, subsurfaces):
        self.x, self.y = x, y
        self.subsurfaces = subsurfaces

    @property
    def rect(self):
        '''Returns a rect representing the board.'''
        rect = pygame.Rect(self.x, self.y, 0, 0)
        for s in self:
            rect.union_ip(s.rect)
        return rect

    def move(self, direction):
        board_rect = self.rect
        x_spacing, y_spacing = board_rect.width//4, board_rect.height//4

        x, y = {
            'up':   (0, -y_spacing),
            'right': (x_spacing, 0),
            'down': (0, y_spacing),
            'left': (-x_spacing, 0)
        }[direction]

        # helper function to check if a rect is inside the board
        inside_board = board_rect.colliderect

        # the current state of the board
        current_pos = set((s.x, s.y) for s in self)

        for subsurf in self:
            new_x, new_y = subsurf.x + x, subsurf.y + y
            # checks if the position is not occupied and is inside
            # the board. If everything is ok, then update the subsurf's pos
            if ((new_x, new_y) not in current_pos
                and inside_board(new_x, new_y, subsurf.width, subsurf.height)):
                subsurf.x, subsurf.y = new_x, new_y

    def randomize(self, n=100):
        
        # make n random moves
        for direction in random_moves(n):
            self.move(direction)

        # move the blank space to the botton-right corner
        self.move('left'), self.move('left'), self.move('left')
        self.move('up'), self.move('up'), self.move('up')
        
    def is_solved(self):
        return all(s.start_pos == (s.x, s.y) for s in self)
        
    def draw(self, surface):
        for subsurf in self:
            surface.blit(subsurf.image, (subsurf.x, subsurf.y))
            
    def __iter__(self):
        return iter(self.subsurfaces)
            

class SubSurf(pygame.sprite.Sprite):

    def __init__(self, x, y, subsurface):
        super(SubSurf, self).__init__()

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


def make_board(image_path, board_rect):
    x, y, width, height = board_rect
    
    puzzle_image = load_puzzle_image(image_path, board_size=(width,height))
    subsurfs = list(make_subsurfaces(puzzle_image, offset=(x, y)))
    
    # create a board not including the last subsurfs (adding a blank space)
    return Board(x, y, subsurfs[:-1])
    

def load_puzzle_image(path, board_size):
    surface = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(surface, board_size)

    
def make_subsurfaces(surface, offset=(0, 0)):
    width, height = surface.get_size()
    
    assert width % 4 + height % 4 == 0, (
        "image's dimention is not div by 4: {}".format(surface.get_size()))

    offx, offy = offset
    for y in range(0, height, height//4):
        for x in range(0, width, width//4):
            subsurface = surface.subsurface(x, y, width//4, height//4)
            yield SubSurf(offx + x, offy + y, subsurface)


def random_moves(n):
    directions = ('up', 'right', 'down', 'left')
    for _ in range(n):
        yield choice(directions)


if __name__ == '__main__':
    game = Game(
        width=400, 
        height=428,
        caption='Pygame Sliding Puzzle',
        puzzle_image='pygame-badge.png', 
        board_rect=(36, 50, 328, 328)
    )
    game.start()
    game.game_loop()

