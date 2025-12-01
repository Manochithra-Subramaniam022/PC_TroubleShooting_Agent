import numpy as np
import pygame
import sys
import math
import random

# --- Constants ---
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROWS = 6
COLS = 7

PLAYER_PIECE = 1
AI_PIECE = 2

SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)

# --- Functions ---

def create_board():
    """Create a new empty Connect 4 board."""
    return np.zeros((ROWS, COLS), dtype=int)

def drop_piece(board, row, col, piece):
    """Place a piece on the board at the specified location."""
    board[row][col] = piece

def is_valid_location(board, col):
    """Check if a column has an empty slot."""
    return board[ROWS-1][col] == 0

def get_next_open_row(board, col):
    """Find the next open row in a given column."""
    for r in range(ROWS):
        if board[r][col] == 0:
            return r
    return None

def winning_move(board, piece):
    """Check if the last move resulted in a win."""
    # Check horizontal locations
    for c in range(COLS - 3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

def evaluate_window(window, piece):
    """Helper function to score a 4-slot window."""
    score = 0
    opponent_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    
    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4
    
    return score

def score_position(board, piece):
    """Scores the entire board for a given piece."""
    score = 0
    center_array = [int(i) for i in list(board[:, COLS // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # Score vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # Score positive sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Score negative sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
            
    return score

def get_valid_locations(board):
    """Get a list of all valid columns."""
    return [col for col in range(COLS) if is_valid_location(board, col)]

def is_terminal_node(board):
    """Check if the game has ended."""
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    """Minimax algorithm with Alpha-Beta Pruning."""
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE): return (None, 10000000)
            elif winning_move(board, PLAYER_PIECE): return (None, -10000000)
            else: return (None, 0)
        else: return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta: break
        return column, value
    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta: break
        return column, value

def draw_board(board, screen, height):
    """Draw the game board using Pygame."""
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

# --- Main Execution ---
if __name__ == '__main__':
    board = create_board()
    game_over = False
    turn = random.randint(0, 1)

    pygame.init()
    width = COLS * SQUARESIZE
    height = (ROWS + 1) * SQUARESIZE
    size = (width, height)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Connect 4 AI")
    draw_board(board, screen, height)
    myfont = pygame.font.SysFont("monospace", 75)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                if turn == 0:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)

                        if winning_move(board, PLAYER_PIECE):
                            label = myfont.render("You win!!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True
                        
                        turn = 1
                        draw_board(board, screen, height)

        if turn == 1 and not game_over:
            # AI THINKING 
            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
            
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = myfont.render("AI wins!!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True

                draw_board(board, screen, height)
                turn = 0

        if game_over:
            pygame.time.wait(3000)