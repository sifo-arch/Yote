import pygame
import sys
from experiments import Yote, AI, GameState, History

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
BOARD_SIZE = 600
CELL_SIZE = BOARD_SIZE // 6
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
GREEN = (100, 200, 100)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
WOOD_LIGHT = (210, 180, 140)
WOOD_DARK = (139, 90, 43)
BOARD_BORDER = (101, 67, 33)
LINE_COLOR = (70, 50, 30)

class YoteGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Yote - AI vs Human")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        self.game = Yote()
        self.history = History()
        self.history.push(GameState(self.game))
        self.ai = AI(2)  # Black player (AI)
        self.AI_DEPTH = 4
        
        # Game state variables
        self.selected_piece = None
        self.selected_move = None
        self.possible_moves = []
        self.waiting_for_capture_choice = False
        self.pending_capture_moves = []
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        
    def get_board_pos(self, mouse_pos):
        """Convert mouse position to board coordinates"""
        x, y = mouse_pos
        col = (x - BOARD_OFFSET_X) // CELL_SIZE
        row = (y - BOARD_OFFSET_Y) // CELL_SIZE
        if 0 <= row < 5 and 0 <= col < 6:
            return (row, col)
        return None
    
    def draw_board(self):
        """Draw the game board"""
        # Draw background
        self.screen.fill((245, 235, 220))
        
        # Draw board border (thick wooden frame)
        border_thickness = 15
        board_rect = pygame.Rect(BOARD_OFFSET_X - border_thickness, 
                                 BOARD_OFFSET_Y - border_thickness,
                                 BOARD_SIZE + 2 * border_thickness,
                                 BOARD_SIZE + 2 * border_thickness)
        pygame.draw.rect(self.screen, BOARD_BORDER, board_rect)
        pygame.draw.rect(self.screen, (80, 50, 20), board_rect, 3)
        
        # Draw wooden board background
        board_bg = pygame.Rect(BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE, BOARD_SIZE)
        pygame.draw.rect(self.screen, WOOD_LIGHT, board_bg)
        
        # Draw alternating wood pattern for cells
        for row in range(5):
            for col in range(6):
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + row * CELL_SIZE
                
                # Alternate wood colors for a checkered pattern
                if (row + col) % 2 == 0:
                    cell_color = WOOD_LIGHT
                else:
                    cell_color = WOOD_DARK
                
                pygame.draw.rect(self.screen, cell_color, (x, y, CELL_SIZE, CELL_SIZE))
                
                # Draw cell border lines
                pygame.draw.rect(self.screen, LINE_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 2)
        
        # Draw highlights BEFORE stones
        # Highlight selected piece
        if self.selected_piece:
            row, col = self.selected_piece
            x = BOARD_OFFSET_X + col * CELL_SIZE
            y = BOARD_OFFSET_Y + row * CELL_SIZE
            # Draw a glowing yellow circle behind the stone
            center_x = x + CELL_SIZE // 2
            center_y = y + CELL_SIZE // 2
            pygame.draw.circle(self.screen, (255, 255, 150, 128), (center_x, center_y), CELL_SIZE // 2 - 5)
            pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), CELL_SIZE // 2 - 5, 4)
        
        # Highlight possible moves
        if not self.waiting_for_capture_choice:
            for move in self.possible_moves:
                if 'h' in move:
                    pos = move[0]
                elif 'b' in move or 'c' in move:
                    pos = move[1]
                else:
                    continue
                    
                x = BOARD_OFFSET_X + pos[1] * CELL_SIZE
                y = BOARD_OFFSET_Y + pos[0] * CELL_SIZE
                center_x = x + CELL_SIZE // 2
                center_y = y + CELL_SIZE // 2
        
        # Highlight capturable pieces when waiting for choice
        if self.waiting_for_capture_choice:
            for move in self.pending_capture_moves:
                if len(move) == 5:
                    pos = move[4]  # The piece to throw
                    x = BOARD_OFFSET_X + pos[1] * CELL_SIZE
                    y = BOARD_OFFSET_Y + pos[0] * CELL_SIZE
                    center_x = x + CELL_SIZE // 2
                    center_y = y + CELL_SIZE // 2
                    # Draw pulsing red circle
                    pygame.draw.circle(self.screen, (255, 150, 150, 128), (center_x, center_y), CELL_SIZE // 2 - 5)
                    pygame.draw.circle(self.screen, RED, (center_x, center_y), CELL_SIZE // 2 - 5, 4)
        
        # Draw stones ON TOP of highlights
        for row in range(5):
            for col in range(6):
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + row * CELL_SIZE
                
                cell_value = self.game.board[row, col]
                if cell_value != 0:
                    center_x = x + CELL_SIZE // 2
                    center_y = y + CELL_SIZE // 2
                    radius = CELL_SIZE // 3
                    
                    # Draw stone with realistic shading
                    if cell_value == 1:  # White stone
                        # Shadow
                        pygame.draw.circle(self.screen, (200, 200, 200), (center_x + 2, center_y + 2), radius)
                        # Main stone
                        pygame.draw.circle(self.screen, WHITE, (center_x, center_y), radius)
                        # Highlight for 3D effect
                        pygame.draw.circle(self.screen, (255, 255, 255), (center_x - 5, center_y - 5), radius // 4)
                        # Border
                        pygame.draw.circle(self.screen, (180, 180, 180), (center_x, center_y), radius, 2)
                    else:  # Black stone
                        # Shadow
                        pygame.draw.circle(self.screen, (50, 50, 50), (center_x + 2, center_y + 2), radius)
                        # Main stone
                        pygame.draw.circle(self.screen, BLACK, (center_x, center_y), radius)
                        # Highlight for 3D effect
                        pygame.draw.circle(self.screen, (80, 80, 80), (center_x - 5, center_y - 5), radius // 4)
                        # Border
                        pygame.draw.circle(self.screen, (60, 60, 60), (center_x, center_y), radius, 2)
    
    def draw_info(self):
        """Draw game information"""
        info_x = BOARD_OFFSET_X + BOARD_SIZE + 30
        info_y = 50
        
        # Current player
        current_player = "White (You)" if self.game.nplayer == 1 else "Black (AI)"
        if self.ai_thinking:
            current_player = "AI is thinking..."
        player_text = self.font.render(f"Turn: {current_player}", True, BLACK)
        self.screen.blit(player_text, (info_x, info_y))
        
        # Stones in hand
        white_stones_text = self.small_font.render(f"White stones: {self.game.in_hand_white_stones}", True, BLACK)
        self.screen.blit(white_stones_text, (info_x, info_y + 60))
        
        black_stones_text = self.small_font.render(f"Black stones: {self.game.in_hand_black_stones}", True, BLACK)
        self.screen.blit(black_stones_text, (info_x, info_y + 90))
        
        # Captures
        white_captures_text = self.small_font.render(f"White captures: {self.game.white_captures}", True, BLACK)
        self.screen.blit(white_captures_text, (info_x, info_y + 130))
        
        black_captures_text = self.small_font.render(f"Black captures: {self.game.black_captures}", True, BLACK)
        self.screen.blit(black_captures_text, (info_x, info_y + 160))
        
        # Instructions
        if self.waiting_for_capture_choice:
            instruction = "Click opponent piece to remove"
        elif self.selected_piece:
            instruction = "Click destination"
        else:
            instruction = "Click to place/move"
        
        instruction_text = self.small_font.render(instruction, True, BLUE)
        self.screen.blit(instruction_text, (info_x, info_y + 220))
        
        # Restart button
        button_rect = pygame.Rect(info_x, info_y + 280, 180, 50)
        pygame.draw.rect(self.screen, GREEN, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        restart_text = self.font.render("Restart", True, BLACK)
        text_rect = restart_text.get_rect(center=button_rect.center)
        self.screen.blit(restart_text, text_rect)
        
        # Game over message
        if self.game_over:
            winner_name = "White (You)" if self.winner == 1 else "Black (AI)"
            game_over_text = self.font.render(f"{winner_name} wins!", True, RED)
            self.screen.blit(game_over_text, (info_x, info_y + 360))
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        # Check restart button
        info_x = BOARD_OFFSET_X + BOARD_SIZE + 30
        info_y = 50
        button_rect = pygame.Rect(info_x, info_y + 280, 180, 50)
        if button_rect.collidepoint(pos):
            self.reset_game()
            return
        
        if self.game_over or self.game.nplayer == 2:
            return
        
        board_pos = self.get_board_pos(pos)
        if board_pos is None:
            return
        
        # Handle capture choice
        if self.waiting_for_capture_choice:
            for move in self.pending_capture_moves:
                if len(move) == 5 and move[4] == board_pos:
                    self.execute_move(move)
                    self.waiting_for_capture_choice = False
                    self.pending_capture_moves = []
                    return
            return
        
        row, col = board_pos
        
        # Check if clicking on own piece to select it
        if self.game.board[row, col] == self.game.nplayer:
            self.selected_piece = board_pos
            self.update_possible_moves()
            return
        
        # Try to execute a move
        for move in self.possible_moves:
            move_executed = False
            
            # Place from hand
            if 'h' in move and move[0] == board_pos:
                self.execute_move(move)
                move_executed = True
                break
            
            # Move on board
            if 'b' in move and self.selected_piece == move[0] and move[1] == board_pos:
                self.execute_move(move)
                move_executed = True
                break
            
            # Capture move
            if 'c' in move and self.selected_piece == move[0] and move[1] == board_pos:
                # Check if this capture requires choosing a piece to throw
                capture_moves_to_this_dest = [m for m in self.possible_moves 
                                             if 'c' in m and m[0] == move[0] and m[1] == move[1]]
                
                if any(len(m) == 5 for m in capture_moves_to_this_dest):
                    # Need to choose which piece to throw
                    self.pending_capture_moves = [m for m in capture_moves_to_this_dest if len(m) == 5]
                    self.waiting_for_capture_choice = True
                else:
                    # No choice needed, execute the move
                    self.execute_move(move)
                    move_executed = True
                break
        
        if not self.waiting_for_capture_choice:
            self.selected_piece = None
            self.update_possible_moves()
    
    def execute_move(self, move):
        """Execute a move and handle turn change"""
        self.game.play_move(move)
        self.history.push(GameState(self.game))
        self.selected_piece = None
        self.possible_moves = []
        
        # Check if game is over
        is_over, winner = self.game.is_over()
        if is_over:
            self.game_over = True
            self.winner = winner
    
    def update_possible_moves(self):
        """Update the list of possible moves"""
        self.possible_moves = self.game.possible_moves()
        
        # Filter moves based on selected piece
        if self.selected_piece:
            self.possible_moves = [m for m in self.possible_moves 
                                  if ('b' in m or 'c' in m) and m[0] == self.selected_piece]
    
    def ai_move(self):
        """Execute AI move"""
        if self.game.nplayer == 2 and not self.game_over:
            self.ai_thinking = True
            self.draw()
            pygame.display.flip()
            
            move, value = self.ai.choose_best_move(self.game, self.AI_DEPTH, False)
            self.execute_move(move)
            
            self.ai_thinking = False
    
    def draw(self):
        """Draw everything"""
        self.draw_board()
        self.draw_info()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            # AI turn
            if self.game.nplayer == 2 and not self.game_over and not self.waiting_for_capture_choice:
                self.ai_move()
            
            # Update possible moves for human player
            if self.game.nplayer == 1 and not self.waiting_for_capture_choice:
                if not self.selected_piece:
                    self.possible_moves = self.game.possible_moves()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game_gui = YoteGUI()
    game_gui.run()