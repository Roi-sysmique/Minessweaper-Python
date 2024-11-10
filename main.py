import pygame
import random

# Initialize Pygame
pygame.init()

# Define screen dimensions and cell size for the grid
SCREEN_HEIGHT = 450
SCREEN_WIDTH = 450
CELL_SIZE = 30
# Load font for displaying text on the screen
FONT = pygame.font.Font('FONT/score_board_font.ttf', 60)
# Create a background surface for the game
BACKGROUND = pygame.surface.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize the game grid; each cell is represented by '.'
game_grid = [['.' for _ in range(int(SCREEN_WIDTH / CELL_SIZE))] for _ in
             range(int((SCREEN_HEIGHT - 60) / CELL_SIZE))]

# Get the number of rows and columns in the grid
num_rows = len(game_grid)
num_cols = len(game_grid[0])

# Set up the display
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
pygame.display.set_caption('Minesweeper')

# Set up clock and game parameters
CLOCK = pygame.time.Clock()
FPS = 120
mouse_click = None
num_mine = 20
num_flag = num_mine
# Load restart button image and set its position
restart = pygame.transform.scale(pygame.image.load('Assets/button.png'), (60, 60))
restart_rect = restart.get_rect(midtop=(SCREEN_WIDTH/2, 0))
# Initialize timer variables
start_time = pygame.time.get_ticks()
time = ""
minutes = 0
second = 0
elapsed_seconds = 0

# Mapping numbers to their corresponding image paths
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
# Game status flags
game_over = False
game_win = False


class Cell(pygame.sprite.Sprite):
    def __init__(self, row, col):
        pygame.sprite.Sprite.__init__(self)
        self.size = CELL_SIZE
        self.col = col
        self.row = row

        # Create a surface for the cell and define its position
        self.image = pygame.transform.scale(pygame.image.load('Assets/block.png'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.col * CELL_SIZE, (self.row * CELL_SIZE) + 60)
        self.mark_flag = False
        self.last_click_id = None
        self.revealed = False
        self.mine = False

        # Set mine status based on game_grid
        if game_grid[self.row][self.col] == '*':
            self.mine = True

        # Neighboring cell offsets for mine counting
        self.neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1),
                                 (-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Initialize list for neighboring cells and count of mines
        self.neighbors = []
        self.num = None

        # Remove invalid neighboring offsets
        self.remove_invalid_neighbors()

        # Calculate the number of neighboring mines if cell is not a mine
        self.count_mines()

    def remove_invalid_neighbors(self):
        # Filter out offsets that would go out of grid bounds
        self.neighbor_offsets = [(dr, dc) for dr, dc in self.neighbor_offsets
                                 if 0 <= self.row + dr < num_rows and 0 <= self.col + dc < num_cols]

    def count_mines(self):
        # Count how many neighbors contain mines
        for dr, dc in self.neighbor_offsets:
            row_pos = self.row + dr
            col_pos = self.col + dc
            self.neighbors.append(game_grid[row_pos][col_pos])
        # Calculate number of neighboring mines if not a mine
        if not self.mine:
            self.num = self.neighbors.count('*')
            game_grid[self.row][self.col] = self.num

    def update(self, click):
        global game_over, num_flag
        # Update cell appearance based on its state (revealed, flagged, etc.)
        if self.revealed and self.num == 0:
            self.image = pygame.surface.Surface((CELL_SIZE, CELL_SIZE))
            self.image.fill('grey')
        elif self.revealed and self.mine:
            self.image = pygame.transform.scale(pygame.image.load('Assets/clicked_mine.png'),
                                                (CELL_SIZE, CELL_SIZE))
        elif self.revealed and not self.mine:
            self.image = pygame.transform.scale(pygame.image.load(num_to_image[self.neighbors.count('*')]),
                                                (CELL_SIZE, CELL_SIZE))
        # Handle right-click for flagging/unflagging cells
        if click is not None and self.rect.collidepoint(click[0]) and click[1] == 2 and click[2] != self.last_click_id and not self.revealed:
            if not self.mark_flag:
                num_flag -= 1
                self.image = pygame.transform.scale(pygame.image.load("Assets/flag.png"),
                                                    (CELL_SIZE, CELL_SIZE))
                self.mark_flag = True
                self.last_click_id = click[2]
            if self.mark_flag and click[2] != self.last_click_id:
                num_flag += 1
                self.image = pygame.transform.scale(pygame.image.load('Assets/block.png'),
                                                    (CELL_SIZE, CELL_SIZE))
                self.mark_flag = False
                self.last_click_id = click[2]
        # Handle left-click for revealing cells
        elif click is not None and self.rect.collidepoint(click[0]) and click[1] == 0:
            if self.mark_flag:
                pass
            elif self.num == 0:
                self.revealed = True
            elif not self.mine:
                self.revealed = True
            else:
                self.revealed = True
                game_over = True


def draw_grid():
    # Draw vertical and horizontal lines to create a grid on the screen
    for x in range(0, int(SCREEN_WIDTH + 1), CELL_SIZE):
        pygame.draw.line(SCREEN, 'grey', (x, 60), (x, SCREEN_HEIGHT))
    for y in range(60, int(SCREEN_HEIGHT + 1), CELL_SIZE):
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


def flood_fill():
    # Reveal empty neighboring cells if cell is not adjacent to a mine
    revealed_cells = []
    for cell in cells:
        if cell.num == 0 and cell.revealed:
            for dr, dc in cell.neighbor_offsets:
                row_pos = cell.row + dr
                col_pos = cell.col + dc
                revealed_cells.append((row_pos, col_pos))
    for cell in cells:
        if (cell.row, cell.col) in revealed_cells:
            if not cell.mark_flag:
                cell.revealed = True


def reveal_all_mines():
    # Reveal all mines if the player loses the game
    global game_win
    for cell in cells:
        if cell.mine and not cell.revealed:
            cell.image = pygame.transform.scale(pygame.image.load('Assets/mine.png'),
                                                (CELL_SIZE, CELL_SIZE))
        if not cell.mine:
            cell.revealed = True
        game_win = False


def check_win():
    # Check if all non-mine cells have been revealed to determine win condition
    global game_win
    for _ in cells:
        if not _.mine and _.revealed:
            pass
        elif not _.mine and not _.revealed:
            return None
    game_win = True


# Place mines and initialize cells
place_mines(num_mine)
cells = pygame.sprite.Group()
for row in range(0, len(game_grid)):
    for col in range(0, len(game_grid[row])):
        cell = Cell(row=row, col=col)
        cells.add(cell)


def time_sys():
    global start_time, time, minutes, second, elapsed_seconds
    # Calculate elapsed time in seconds since the game started
    elapsed_seconds = (pygame.time.get_ticks() - start_time) // 1000

    # Calculate minutes and seconds for the timer display
    minutes = elapsed_seconds // 60
    second = elapsed_seconds % 60

    # Format time for display
    time = f"{minutes}:{str(second).zfill(2)}"  # Display 00:00 format


# Main game loop
while True:
    num_flag_txt = FONT.render(str(num_flag), True, 'red')
    num_flag_txt_rect = num_flag_txt.get_rect(midtop=(SCREEN_WIDTH/4, 10))
    time_text = FONT.render(str(time), True, 'red')
    time_text_rect = time_text.get_rect(midtop=(SCREEN_WIDTH * 3 / 4, 10))
    mouse_key = pygame.mouse.get_pressed(3)
    last_mouse_click = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        # Check for mouse button inputs and update mouse click status
        if mouse_key[2]:  # Right click
            mouse_click = (pygame.mouse.get_pos(), 2, random.randrange(0, 1000))
        elif mouse_key[0]:  # Left click
            mouse_click = (pygame.mouse.get_pos(), 0, random.randrange(0, 1000))
        # Reset game if the restart button is clicked
        if mouse_click != None and restart_rect.collidepoint(pygame.mouse.get_pos()) and last_mouse_click != mouse_click[2] and mouse_key[0]:
            last_mouse_click = mouse_click[2]
            game_grid = [['.' for _ in range(int(SCREEN_WIDTH / CELL_SIZE))] for _ in
                         range(int((SCREEN_HEIGHT - 60) / CELL_SIZE))]
            place_mines(num_mine)
            num_flag = num_mine
            cells.empty()
            for row in range(0, len(game_grid)):
                for col in range(0, len(game_grid[row])):
                    cell = Cell(row=row, col=col)
                    cells.add(cell)
            game_over = False
            game_win = False
            # Reset timer
            start_time = pygame.time.get_ticks()
            minutes = 0
            second = 0
            time = "0:00"  # Update initial display

    # Draw cells and grid
    if not game_over and not game_win:
        time_sys()
    SCREEN.blit(BACKGROUND, (0, 0))
    SCREEN.blit(restart, restart_rect)
    SCREEN.blit(time_text, time_text_rect)
    cells.draw(SCREEN)
    cells.update(mouse_click)
    SCREEN.blit(num_flag_txt, num_flag_txt_rect)
    flood_fill()
    draw_grid()
    check_win()
    # Display end game screen if player loses or wins
    if game_over:
        reveal_all_mines()
        restart = pygame.transform.scale(pygame.image.load('Assets/loose_button.png'), (60, 60))
        SCREEN.blit(restart, restart_rect)
    if game_win:
        restart = pygame.transform.scale(pygame.image.load('Assets/win_button.png'), (60, 60))
        SCREEN.blit(restart, restart_rect)
    else:
        restart = pygame.transform.scale(pygame.image.load('Assets/button.png'), (60, 60))
    pygame.display.update()
    CLOCK.tick(FPS)
