import pygame
import random

pygame.init()

# Define screen dimensions and square size for grid cells
SCREEN_HEIGHT = 450
SCREEN_WIDTH = 450
square_length = 30

# Initialize the game environment with a grid, each cell represented by '.'
game_grid = [['.' for _ in range(int(SCREEN_WIDTH / square_length))] for _ in
             range(int((SCREEN_HEIGHT - 60) / square_length))]

# Get the number of rows and columns in the grid
num_rows = len(game_grid)
num_cols = len(game_grid[0])

# Set up the display
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
pygame.display.set_caption('minesweeper')

CLOCK = pygame.time.Clock()
FPS = 120
num_to_image = {
    1: "Assets/number-1.png",
    2: "Assets/number-2.png",
    3: "Assets/number-3.png",
    4: "Assets/number-4.png",
    5: "Assets/number-5.png",
    6: "Assets/number-6.png",
    7: "Assets/number-7.png",
    8: "Assets/number-8.png"
}


class Cell(pygame.sprite.Sprite):
    def __init__(self, row, col):
        pygame.sprite.Sprite.__init__(self)
        self.length = square_length
        self.col = col
        self.row = row

        # Create a surface for the cell and define its position
        self.image = pygame.transform.scale(pygame.image.load('Assets/block.png'), (square_length, square_length))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.col * square_length, (self.row * square_length) + 60)
        self.mark_flag = False

        # Set mine status and color based on game_grid
        if game_grid[self.row][self.col] == '*':
            self.mine = True
            self.image.fill('red')  # Red for mine
        else:
            self.mine = False

        # Define possible neighboring cell offsets if not a mine
        if not self.mine:
            self.neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1),
                                     (-1, -1), (-1, 1), (1, -1), (1, 1)]

            # Initialize list for neighboring cells and count of mines
            self.neighbors = []
            self.num = None

            # Remove invalid neighboring offsets
            self.remove_invalid_neighbors()

            # Calculate the number of neighboring mines
            self.count_mines()

    def remove_invalid_neighbors(self):
        # Filter out any offsets that would go out of grid bounds
        self.neighbor_offsets = [(dr, dc) for dr, dc in self.neighbor_offsets
                                 if 0 <= self.row + dr < num_rows and 0 <= self.col + dc < num_cols]

    def count_mines(self):
        # Count how many neighbors contain mines
        for dr, dc in self.neighbor_offsets:
            row_pos = self.row + dr
            col_pos = self.col + dc
            self.neighbors.append(game_grid[row_pos][col_pos])

        # Count mines among neighbors and update game_grid
        self.num = self.neighbors.count('*')
        game_grid[self.row][self.col] = self.num
        if self.num != 0:
            self.image = pygame.transform.scale(pygame.image.load(num_to_image[self.neighbors.count('*')]), (square_length, square_length))


def draw_grid():
    # Draw vertical and horizontal lines to create a grid on the screen
    for x in range(0, int(SCREEN_WIDTH + 1), square_length):
        pygame.draw.line(SCREEN, 'grey', (x, 60), (x, SCREEN_HEIGHT))
    for y in range(60, int(SCREEN_HEIGHT + 1), square_length):
        pygame.draw.line(SCREEN, 'grey', (0, y), (SCREEN_WIDTH, y))


def place_mines(mines_count):
    # Randomly place a specified number of mines within the grid
    mine_positions = []
    for _ in range(mines_count):
        mine_row = random.randint(0, num_rows - 1)
        mine_col = random.randint(0, num_cols - 1)
        if (mine_row, mine_col) in mine_positions:
            continue
        mine_positions.append((mine_row, mine_col))

    for row, col in mine_positions:
        game_grid[row][col] = '*'


# Place mines and initialize cells
place_mines(10)
cells = pygame.sprite.Group()
for row in range(0, len(game_grid)):
    for col in range(0, len(game_grid[row])):
        cell = Cell(row=row, col=col)
        cells.add(cell)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Draw cells and grid
    cells.draw(SCREEN)
    draw_grid()
    pygame.display.update()
    CLOCK.tick(FPS)
