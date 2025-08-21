"""
    Minesweeper Clone
    @Author: Patricio Labin (@f1r3f0x)
    2025
"""

import time
import random
from dataclasses import dataclass

from pprint import pprint

import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BOARD_POSITION = (20, 20)  # Pixels (x, y)
BOARD_HEIGHT = 10
BOARD_WIDTH = 10

CELL_SIZE = 50  # Pixels

MINES_EASY = 10
MINES_MEDIUM = 30
MINES_HARD = 60


@dataclass
class Cell:
    mine: bool = False         # is there a mine here?
    adj: int = 0               # number of adjacent mines
    revealed: bool = False     # has player revealed this cell?
    flagged: bool = False      # has player flagged this cell?

@dataclass
class Position:
    x: int = 0
    y: int = 0

def setup():
    """
    Initializes Pygame and sets up the display with the specified
    dimensions and title.

    Returns:
        tuple: screen, clock
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minesweeper Clone - F1r3f0x")
    clock = pygame.time.Clock()
    font = pygame.font.Font("assets/PublicPixel.ttf", 18)

    return screen, clock, font


def initialize_board():
    board_array = []

    random.seed(time.time())
    #random.seed(1.2)

    mines_count = 0

    for y in range(BOARD_HEIGHT * BOARD_WIDTH):
        if mines_count < 10:
            board_array.append(Cell(mine=True))
            mines_count += 1
        else:
            board_array.append(Cell())

    random.shuffle(board_array)

    board = []
    for y in range(BOARD_HEIGHT):
        row = []
        for x in range(BOARD_WIDTH):
            row.append(board_array[y * BOARD_WIDTH + x])
        board.append(row)

    
    # Precompute mine counters
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            cell = board[y][x]
            if cell.mine:
                for local_y in range(-1, 2):
                    for local_x in range(-1, 2):
                        if (x + local_x >= 0 and x + local_x < BOARD_WIDTH and y + local_y >= 0 
                            and y + local_y < BOARD_HEIGHT):
                            local_cell = board[y + local_y][x + local_x]
                            local_cell.adj += 1

    return board


def draw_cell(screen, color, cell_x, cell_y, cell_size):
    """
    Draws a cell on the screen.

    :param screen: The pygame screen to draw on.
    :param cell_x: The x position of the cell.
    :param cell_y: The y position of the cell.
    :param cell_size: The size of the cell.
    :param color: The color of the cell.
    """
    pygame.draw.rect(
        screen,
        color,
        (
            cell_x + 1,     # Top: Current x value * cell_size + offset from the screen + offset from other cells + 1 to offset from the border
            cell_y + 1,     # Left: Current y value * cell_size + offset from the screen + offset from other cells + 1 to offset from the border
            cell_size - 2,  # Width: Current cell size - 2 to fill the inside of the cell
            cell_size - 2   # Height: Current cell size - 2 to fill the inside of the cell
        )
    )


def draw_board(screen, font, board):
    """
    Draws a Minesweeper board on the screen.

    The board is drawn with a cell size of CELL_SIZE and offset by 20 pixels from the
    top and left of the screen. The board is drawn with a 1 pixel border.

    :param screen: The pygame screen to draw on.
    """
    cell_offset_x = 0
    cell_offset_y = 0

    for y in range(BOARD_HEIGHT):
        # Offsets 1 pixel to the top (so we just draw one continous line)
        if y > 0:
            cell_offset_y -= 1
        else: # resets offset
            cell_offset_y = 0

        for x in range(BOARD_WIDTH):
            # Offsets 1 pixel to the left ((so we just draw one continous line))
            if x > 0:
                cell_offset_x -= 1
            else: # resets offset
                cell_offset_x = 0

            cell_x_pos = (x * CELL_SIZE) + BOARD_POSITION[0] + cell_offset_x  # Current x value * cell_size + offset from the screen + offset from other cells
            cell_y_pos = (y * CELL_SIZE) + BOARD_POSITION[1] + cell_offset_y

            # Draw cell borders
            pygame.draw.rect(
                screen,
                "black",
                (
                    cell_x_pos,  # Top
                    cell_y_pos,  # Left
                    CELL_SIZE,   # Width
                    CELL_SIZE    # Height
                ),
                1
            )
            
            cell = board[y][x]

            if cell.flagged:
                draw_cell(screen, "yellow", cell_x_pos, cell_y_pos, CELL_SIZE)
            elif cell.mine and not cell.revealed:
                draw_cell(screen, "red", cell_x_pos, cell_y_pos, CELL_SIZE)
            elif cell.revealed == False:
                draw_cell(screen, "gray", cell_x_pos, cell_y_pos, CELL_SIZE)
            elif cell.revealed:
                draw_cell(screen, "white", cell_x_pos, cell_y_pos, CELL_SIZE)
                if cell.adj > 0:
                    text = font.render(str(cell.adj), True, "black")
                    text_rect = text.get_rect(center=(cell_x_pos + (CELL_SIZE / 2), cell_y_pos + (CELL_SIZE / 2)))
                    screen.blit(text, text_rect)

def draw_text(screen, font):
    text = font.render("Minesweeper", True, "black")
    text_rect = text.get_rect(top=20, left=540)
    screen.blit(text, text_rect)


def get_cell_pos_from_click(mouse_pos) -> Position | None:
    x = (mouse_pos[0] - BOARD_POSITION[0]) // CELL_SIZE
    y = (mouse_pos[1] - BOARD_POSITION[1]) // CELL_SIZE
    
    if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
        return None

    return Position(x,y)


def process_game(board, clicked_pos: Position, mouse_left, mouse_right):
    
    clicked_cell = board[clicked_pos.y][clicked_pos.x]
    
    if mouse_left:
        if clicked_cell.mine:
            print("You lost!")
            return
        
        # Process empty cells
        if not clicked_cell.mine and not clicked_cell.revealed:
            process_empty_cell(board, clicked_pos)
    
    if mouse_right and not clicked_cell.revealed:
        clicked_cell.flagged = not clicked_cell.flagged
        
def process_empty_cell(board, cell_pos: Position):
    
    cell = board[cell_pos.y][cell_pos.x]
    
    cell.revealed = True
    cell.flagged = False
    
    # If we clicked a mine or a flagged cell, we don't care.
    if cell.mine or cell.flagged or cell.adj != 0:
        return
    
    # Check neighbors
    for x in range(cell_pos.x - 1, cell_pos.x + 2):
        for y in range(cell_pos.y - 1, cell_pos.y + 2):
            
            # Check if neighbor is out of bounds.
            if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
                continue
            
            neighbor = board[y][x]
            
            # Ignore cells we don't need to process.
            if neighbor.revealed or neighbor.flagged or neighbor.mine:
                continue
            
            neighbor.revealed = True

            # Process only the empty cells
            if neighbor.adj == 0:
                process_empty_cell(board, Position(x,y))

def main():
    """
    Main function for the game.

    Contains the main game loop and handles updating the game state
    and rendering the game frame.
    """
    screen, clock, font = setup()
    running = True
    dt = 0
    refresh_rate = pygame.display.get_current_refresh_rate()

    board = initialize_board()

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_buttons = pygame.mouse.get_just_released()
        mouse_left = mouse_buttons[0]
        mouse_right = mouse_buttons[2]
        mouse_pos = pygame.mouse.get_pos()

        if mouse_left or mouse_right:
            mouse_pos = pygame.mouse.get_pos()
            cell_pos = get_cell_pos_from_click(mouse_pos)
            if cell_pos:
                cell = board[cell_pos.y][cell_pos.x]
                print(cell)
                process_game(board, cell_pos, mouse_left, mouse_right)

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        draw_board(screen, font, board)
        draw_text(screen, font)

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to refresh rate
        dt = clock.tick(refresh_rate) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()