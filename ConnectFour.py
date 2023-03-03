import numpy as np
from button import Button
import random
import math
import pygame
import sys

class Game:
    def __init__(self,row=6,col=7,player=0,AI=1,empt=0,player_piece=1,AI_piece=2,wind_leng=4):
        self.ROW_COUNT=row
        self.COLUMN_COUNT=col
        self.PLAYER=player
        self.AI=AI
        self.EMPTY=empt
        self.PLAYER_PIECE=player_piece
        self.AI_PIECE=AI_piece
        self.WINDOW_LENGTH= wind_leng

    def create_board(self):
        board = np.zeros((self.ROW_COUNT,self.COLUMN_COUNT))
        return board

    def drop_piece(self,board,row, col, piece):
        board[row][col] = piece

    def is_valid_location(self,board, col):
        return board[self.ROW_COUNT-1][col] == 0

    def get_next_open_row(self,board, col):
        for r in range(self.ROW_COUNT):
            if board[r][col] == 0:
                return r
            
    def print_board(self,board):
        print(np.flip(board, 0))
    
    def winning_move(self,board, piece):
        	# Check horizontal locations for win
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True
                
                # Check vertical locations for win
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT-3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True
                
                # Check positively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT-3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True

            	# Check negatively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(3, self.ROW_COUNT):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True
                    
    def evaluate_window(self,window, piece):
        score=0
        opp_piece = self.PLAYER_PIECE
        if piece == self.PLAYER_PIECE:
            opp_piece = self.AI_PIECE
            
        if window.count(piece) == 4:
            score += 100
        
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2
            
        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4
        
        return score
        
    def score_position(self,board, piece):
        score = 0
        
        ## Score center column
        center_array = [int(i) for i in list(board[:, self.COLUMN_COUNT//2])]
        center_count = center_array.count(piece)
        score += center_count * 3
        ## Score Horizontal
        for r in range(self.ROW_COUNT):
            row_array = [int(i) for i in list(board[r,:])]
            for c in range(self.COLUMN_COUNT-3):
                window = row_array[c:c+self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)
        ## Score Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = [int(i) for i in list(board[:,c])]
            for r in range(self.ROW_COUNT-3):
                window = col_array[r:r+self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)
        ## Score posiive sloped diagonal
        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board[r+i][c+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)
        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board[r+3-i][c+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)
        return score
        
    def is_terminal_node(self,board):
        return self.winning_move(board, self.PLAYER_PIECE) or self.winning_move(board, self.AI_PIECE) or len(self.get_valid_locations(board)) == 0
        
    def minimax(self,board, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, self.AI_PIECE):
                    return (None, 100000000000000)
                elif self.winning_move(board, self.PLAYER_PIECE):
                    return (None, -10000000000000)
                else: # Game is over, no more valid moves
                    return (None, 0)
            else: # Depth is zero
                return (None, self.score_position(board, self.AI_PIECE))
        
        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, self.AI_PIECE)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
            
        else: # Minimizing player
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, self.PLAYER_PIECE)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
            
    def get_valid_locations(self,board):
        valid_locations = []
        for col in range(self.COLUMN_COUNT):
            if self.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations
        
    def pick_best_move(self,board, piece):
        valid_locations = self.get_valid_locations(board)
        best_score = -10000
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = self.get_next_open_row(board, col)
            temp_board = board.copy()
            self.drop_piece(temp_board, row, col, piece)
            score = self.score_position(temp_board, piece)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col


#Blue board
def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, DARK_BLUE, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

#Global font
def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)

#Play game window
def play(algo_depth):
    game=Game()
    board=game.create_board()
    game.print_board(board)
    LEADERBOARD=''
    AI_SCORE=0
    PLAYER_SCORE=0
    game_over=False
    draw_board(board)
    pygame.display.set_caption("Connect 4")
    pygame.display.update()
    myfont = get_font(45)
    turn = random.randint(PLAYER, AI)
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			
			# Ask for Player 1 Input
                if turn == PLAYER:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))
                    
                    if game.is_valid_location(board, col):
                        row = game.get_next_open_row(board, col)
                        game.drop_piece(board, row, col, PLAYER_PIECE)
                        PLAYER_SCORE+=1
                        score=str(PLAYER_SCORE)
                        points = myfont.render(score, 1, RED)
                        screen.blit(points, (530,10))
                        if game.winning_move(board, PLAYER_PIECE):
                            label = myfont.render("USER WINS", 1, RED)
                            screen.blit(label, (140,10))
                            LEADERBOARD += 'PLAYER' + ' scores '  + score+'\n'
                            game_over = True
                            
                        turn += 1
                        turn = turn % 2
                        
                        game.print_board(board)
                        draw_board(board)
        
        
        # # Ask for Player 2 Input
        if turn == AI and not game_over:
		#col = random.randint(0, COLUMN_COUNT-1)
		#col = pick_best_move(board, AI_PIECE)
            col, minimax_score = game.minimax(board, algo_depth, -math.inf, math.inf, True)
            if game.is_valid_location(board, col):
                row = game.get_next_open_row(board, col)
                game.drop_piece(board, row, col, AI_PIECE)
                AI_SCORE+=1
                score=str(AI_SCORE)
                points = myfont.render(score, 1, YELLOW)
                screen.blit(points, (30,10))
                if game.winning_move(board, AI_PIECE):
                    label = myfont.render("AI WINS", 1, YELLOW)
                    screen.blit(label, (190,10))
                    LEADERBOARD += 'AI' + ' scores ' + score + '\n'
                    game_over = True
                
                game.print_board(board)
                draw_board(board)
                
                turn += 1
                
                turn = turn % 2
        if game_over:
            print(LEADERBOARD)
            pygame.time.wait(1800)
            screen.blit(BG, (0,0))
            pygame.display.update()
            replay_window(algo_depth)

#Help window            
def help():
    while True:
        screen.blit(BcG, (0, 20))
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        OPTIONS_BACK = Button(image=None, pos=(40, 30), 
                            text_input="<", font=get_font(40), base_color=YELLOW, hovering_color=RED)
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(screen)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu() 
        pygame.display.update() 

#Main menu window
def main_menu():
    while True:
        screen.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(40).render("MAIN MENU", True, "#ffffff")
        MENU_RECT = MENU_TEXT.get_rect(center=(330, 150))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(330, 240), 
                            text_input="PLAY", font=get_font(20), base_color="#808080", hovering_color="White")
                            
        HELP_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(260, 355), 
                            text_input="HELP!", font=get_font(20), base_color="#808080", hovering_color="White")

        PLAYMODE_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(400, 355), 
                            text_input="MODES", font=get_font(20), base_color="#808080", hovering_color="White")
        
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(330, 470), 
                            text_input="QUIT", font=get_font(20), base_color="#808080", hovering_color="White")

        screen.blit(MENU_TEXT, MENU_RECT)
        for button in [PLAY_BUTTON, HELP_BUTTON,PLAYMODE_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(4)
                if PLAYMODE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mode_window()
                if HELP_BUTTON.checkForInput(MENU_MOUSE_POS):
                    help()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

#game mode window
def mode_window():
    while True:
        screen.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(40).render("SELECT GAME MODE", True, "#ffffff")
        MENU_RECT = MENU_TEXT.get_rect(center=(330, 110))

        EASY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(330, 210), 
                            text_input="EASY", font=get_font(20), base_color="#808080", hovering_color="White")
        
        INTERMEDIATE_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(330, 340), 
                            text_input="INTERMEDIATE", font=get_font(20), base_color="#808080", hovering_color="White")
        
        HARD_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(330, 470), 
                            text_input="HARD", font=get_font(20), base_color="#808080", hovering_color="White")

        screen.blit(MENU_TEXT, MENU_RECT)
        for button in [EASY_BUTTON, INTERMEDIATE_BUTTON, HARD_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if EASY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(1)
                if INTERMEDIATE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(2)
                if HARD_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(4)
        pygame.display.update()

#Replay window
def replay_window(algo_depth):
    while True:
        screen.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(40).render("REPLAY...", True, "#ffffff")
        MENU_RECT = MENU_TEXT.get_rect(center=(330, 150))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(330, 250), 
                            text_input="REPLAY", font=get_font(20), base_color="#808080", hovering_color="White")
        
        PLAYMODE_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(330, 360), 
                            text_input="GAME MODE", font=get_font(20), base_color="#808080", hovering_color="White")
                            
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(330, 470), 
                            text_input="QUIT", font=get_font(20), base_color="#808080", hovering_color="White")

        screen.blit(MENU_TEXT, MENU_RECT)
        for button in [PLAY_BUTTON, PLAYMODE_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(algo_depth)
                if PLAYMODE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mode_window()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

#Initial window
def initial_window():
    screen.blit(ConnectFourImg, (0,0))
    pygame.display.update()
    pygame.time.wait(1800)

#variables' assignment
#colors
WHITE=(255,255,255)
BLUE = (20,80,147)
DARK_BLUE = (7,39,75)
BLACK=(0,0,0)
RED = (255,30,30)
YELLOW = (255,255,0)
#row and column
ROW_COUNT = 6
COLUMN_COUNT = 7
#values of players
PLAYER = 0
AI = 1
#terminal board values
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
#gui window variables
WINDOW_LENGTH = 4
SQUARESIZE = 90
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)
#game initialization variables
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4")
ConnectFourImg = pygame.image.load("assets/Splash.png")
initial_window()
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Main Menu")
BG = pygame.image.load("assets/Background.png")
BcG = pygame.image.load("assets/help.png")
main_menu()
