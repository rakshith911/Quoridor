import pygame # type: ignore
import sys
from queue import Queue, Empty
import time

# Constants
BOARD_SIZE = 9
CELL_SIZE = 60
GAP_SIZE = 10
MARGIN = 50
WINDOW_SIZE = BOARD_SIZE * (CELL_SIZE + GAP_SIZE) + GAP_SIZE + 2 * MARGIN
PLAYER_RADIUS = 20
WALL_WIDTH = 10
WALL_DISPLAY_HEIGHT = 50

# Colors
LAVENDER = (230, 230, 250)
DARK_PURPLE = (24, 2, 48)
PURPLE = (128, 0, 128)
LIGHT_BROWN = (210, 180, 140)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255,255,255)

class QuoridorGame:
    def __init__(self):
        self.board_size = BOARD_SIZE
        self.players = {'A': (0, 4), 'B': (8, 4)}
        self.walls = set()
        self.turn = 'A'
        self.wall_count = {'A': 6, 'B': 6}
        self.placed_walls = {'A': 0, 'B': 0}
        self.selected_player = None
        self.selected_wall = None
        self.message = ""
        self.frame_queue = Queue()

        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 100))
        pygame.display.set_caption("Quoridor Game")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()

    def draw_board(self):
        self.screen.fill(DARK_PURPLE)
        # Draw the grid with gaps and stroked boxes
        for i in range(self.board_size):
            for j in range(self.board_size):
                x = MARGIN + j * (CELL_SIZE + GAP_SIZE)
                y = MARGIN + i * (CELL_SIZE + GAP_SIZE)
                pygame.draw.rect(self.screen, LAVENDER, (x, y, CELL_SIZE, CELL_SIZE), 2)

        # Draw the players
        for player, (i, j) in self.players.items():
            x = MARGIN + j * (CELL_SIZE + GAP_SIZE) + CELL_SIZE // 2
            y = MARGIN + i * (CELL_SIZE + GAP_SIZE) + CELL_SIZE // 2
            color = LIGHT_BROWN if player == 'A' else ORANGE
            pygame.draw.circle(self.screen, color, (x, y), PLAYER_RADIUS)
            if self.selected_player == player:
                pygame.draw.circle(self.screen, YELLOW, (x, y), PLAYER_RADIUS, 3)

        # Draw the walls
        for y, x, orientation, owner in self.walls:
            wx = MARGIN + x * (CELL_SIZE + GAP_SIZE)
            wy = MARGIN + y * (CELL_SIZE + GAP_SIZE)
            color = YELLOW if owner == 'A' else BLUE
            if orientation == 'H':
                pygame.draw.rect(self.screen, color, (wx, wy + CELL_SIZE, CELL_SIZE + GAP_SIZE, WALL_WIDTH))
            else:
                pygame.draw.rect(self.screen, color, (wx + CELL_SIZE, wy, WALL_WIDTH, CELL_SIZE + GAP_SIZE))

        # Draw the grid labels
        for i in range(self.board_size):
            num_label = self.small_font.render(str(i + 1), True, WHITE)
            self.screen.blit(num_label, (MARGIN - 20, MARGIN + i * (CELL_SIZE + GAP_SIZE) + CELL_SIZE // 2 - 10))
            alpha_label = self.small_font.render(chr(65 + i), True, WHITE)
            self.screen.blit(alpha_label, (MARGIN + i * (CELL_SIZE + GAP_SIZE) + CELL_SIZE // 2 - 10, MARGIN - 30))

    def draw_turn_indicator(self):
        # Clear the turn indicator area
        turn_indicator_area = pygame.Rect(MARGIN, WINDOW_SIZE - 40, WINDOW_SIZE - 2 * MARGIN, 40)
        pygame.draw.rect(self.screen, DARK_PURPLE, turn_indicator_area)  # Clear the turn indicator area

        # Draw the turn indicator
        turn_text = f"Player {self.turn}'s turn"
        color = LIGHT_BROWN if self.turn == 'A' else ORANGE
        text_surface = self.font.render(turn_text, True, color)
        self.screen.blit(text_surface, (MARGIN, WINDOW_SIZE - 30))

        # Draw the move not possible message on the right
        if self.message:
            text_surface = self.font.render(self.message, True, CYAN)
            text_rect = text_surface.get_rect(right=WINDOW_SIZE - MARGIN, top=WINDOW_SIZE - 30)
            self.screen.blit(text_surface, text_rect)

    def draw_wall_count(self):
        y_position = WINDOW_SIZE + 20
        for i in range(self.wall_count['A']):
            x_position = MARGIN + i * (WALL_WIDTH + 5)
            pygame.draw.rect(self.screen, LIGHT_BROWN, (x_position, y_position, WALL_WIDTH, WALL_DISPLAY_HEIGHT))

        for i in range(self.wall_count['B']):
            x_position = WINDOW_SIZE - MARGIN - (self.wall_count['B'] - 1 - i) * (WALL_WIDTH + 5) - WALL_WIDTH
            pygame.draw.rect(self.screen, ORANGE, (x_position, y_position, WALL_WIDTH, WALL_DISPLAY_HEIGHT))

    def move_player(self, player, new_position):
        if self.is_valid_move(player, new_position):
            self.players[player] = new_position
            self.turn = 'B' if self.turn == 'A' else 'A'
            self.message = ""
        else:
            self.message = "Move not possible"

    def is_valid_move(self, player, new_position):
        current_position = self.players[player]
        y, x = new_position
        cy, cx = current_position

        if 0 <= y < self.board_size and 0 <= x < self.board_size:
            # Check if the move is to an adjacent cell (up, down, left, right)
            if (abs(cy - y) == 1 and cx == x) or (abs(cx - x) == 1 and cy == y):
                # Check if there is a wall blocking the move
                if cy == y:
                    # Horizontal move
                    if cx < x:
                        return (cy, cx, 'V') not in self.walls
                    else:
                        return (cy, x, 'V') not in self.walls
                else:
                    # Vertical move
                    if cy < y:
                        return (cy, cx, 'H') not in self.walls
                    else:
                        return (y, cx, 'H') not in self.walls
        return False

    def place_wall(self, player, wall_position):
        if self.wall_count[player] > 0 and self.is_valid_wall(wall_position):
            self.walls.add((*wall_position, player))
            self.wall_count[player] -= 1
            self.placed_walls[player] += 1
            self.turn = 'B' if self.turn == 'A' else 'A'
            self.message = ""
        else:
            self.message = "Wall placement not possible"

    def is_valid_wall(self, wall_position):
        for wall in self.walls:
            if wall[:3] == wall_position:
                return False
        return True

    def check_win(self):
        for player, position in self.players.items():
            if (player == 'A' and position[0] == self.board_size - 1) or (player == 'B' and position[0] == 0):
                return player
        return None

    def handle_click(self, pos):
        print(pos)
        x, y = pos
        board_x = (x - MARGIN) // (CELL_SIZE + GAP_SIZE)
        board_y = (y - MARGIN) // (CELL_SIZE + GAP_SIZE)
        isMoved = False

        print(board_x, board_y)
        print(self.players[self.turn])
        

        if 0 <= board_x < self.board_size and 0 <= board_y < self.board_size:
            if self.selected_wall:
                print("c1")
                new_wall_position = (board_y, board_x, 'H' if (y - MARGIN) % (CELL_SIZE + GAP_SIZE) > CELL_SIZE else 'V')
                self.move_wall(new_wall_position)
                self.selected_wall = None
                isMoved = True
            elif self.players[self.turn] == (board_y, board_x):
                print("c2")
                self.selected_player = self.turn
            elif self.selected_player:
                print("c3")
                self.move_player(self.selected_player, (board_y, board_x))
                self.selected_player = None
                isMoved = True
            else:
                print("c4")
                # Select or place wall logic
                if self.placed_walls[self.turn] < 6:
                    # Wall placement phase
                    if self.is_valid_wall((board_x, board_y, 'H')) and self.is_valid_wall((board_x, board_y, 'V')):
                        orientation = 'H' if (y - MARGIN) % (CELL_SIZE + GAP_SIZE) > CELL_SIZE else 'V'
                        self.place_wall(self.turn, (board_y, board_x, orientation))
                        isMoved = True
                else:
                    # Wall movement phase
                    for wall in self.walls:
                        wy, wx, orientation, owner = wall
                        wx_pos = MARGIN + wx * (CELL_SIZE + GAP_SIZE)
                        wy_pos = MARGIN + wy * (CELL_SIZE + GAP_SIZE)
                        if orientation == 'H' and wy_pos + CELL_SIZE <= y <= wy_pos + CELL_SIZE + WALL_WIDTH and wx_pos <= x <= wx_pos + CELL_SIZE + GAP_SIZE:
                            self.selected_wall = wall
                            self.walls.remove(wall)
                            return
                        elif orientation == 'V' and wx_pos + CELL_SIZE <= x <= wx_pos + CELL_SIZE + WALL_WIDTH and wy_pos <= y <= wy_pos + CELL_SIZE + GAP_SIZE:
                            self.selected_wall = wall
                            self.walls.remove(wall)
                            return
                    # Place a new wall in the movement phase
                    if self.is_valid_wall((board_x, board_y, 'H')) and self.is_valid_wall((board_x, board_y, 'V')):
                        orientation = 'H' if (y - MARGIN) % (CELL_SIZE + GAP_SIZE) > CELL_SIZE else 'V'
                        self.place_wall(self.turn, (board_y, board_x, orientation))
                        isMoved = True
        
        print("\n\n")
        return isMoved

    def move_wall(self, new_position):
        if self.is_valid_wall(new_position):
            self.walls.add((*new_position, self.turn))
            self.message = ""
            self.turn = 'B' if self.turn == 'A' else 'A'
        else:
            self.message = "Move not possible"
            # Re-add the previously removed wall
            self.walls.add(self.selected_wall)
        self.selected_wall = None

    def get_new_pos(self, poses):
        # Map poses to player movements (This is just an example)
        # Assuming poses is a list [thumb, index, middle, ring, pinky]
        current_position = self.players[self.turn]
        new_position = current_position

        if poses == [1, 0, 0, 0, 0]:  # select player
            return 1
        if poses == [0, 1, 0, 0, 0]:  # Example pose for moving up
            new_position = (current_position[0] - 1, current_position[1])
        elif poses == [0, 1, 1, 0, 0]:  # Example pose for moving down
            new_position = (current_position[0] + 1, current_position[1])
        elif poses == [0, 1, 1, 1, 0]:  # Example pose for moving left
            new_position = (current_position[0], current_position[1] - 1)
        elif poses == [0, 1, 1, 1, 1]:  # Example pose for moving right
            new_position = (current_position[0], current_position[1] + 1)
        else:
            return None
        
        return new_position

    def run(self):
        while True:
            poses = [0, 0, 0, 0, 0]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
            
            try:
                if not self.frame_queue.empty():
                    poses = self.frame_queue.get_nowait()  # Non-blocking get
                    next_pos = self.get_new_pos(poses)
                    isMoved = False

                    if next_pos != None:
                        # this section selects the player before moving
                        if next_pos == 1:
                            curr_pos = self.players[self.turn]
                            curr_coord = ((curr_pos[1] * (CELL_SIZE + GAP_SIZE)) + MARGIN , (curr_pos[0] * (CELL_SIZE + GAP_SIZE)) + MARGIN)
                            self.handle_click(curr_coord)
                        # this section actually moves the player
                        elif self.selected_player != None:
                            next_coord = ((next_pos[1] * (CELL_SIZE + GAP_SIZE)) + MARGIN , (next_pos[0] * (CELL_SIZE + GAP_SIZE)) + MARGIN)
                            isMoved = self.handle_click(next_coord)
                            
                        # check if current player made his move, if true clear queue and wait for opponent to send his moves
                        if isMoved:
                            self.selected_player = None
                            pygame.display.flip()
                            time.sleep(2)
                            with self.frame_queue.mutex:
                                self.frame_queue.queue.clear()

                            print("Is queue emptied ?", self.frame_queue.empty())
                                
            except Empty:
                pass  # If the queue is empty, just pass

            self.draw_board()
            self.draw_turn_indicator()
            self.draw_wall_count()
            winner = self.check_win()
            if winner:
                win_text = self.font.render(f"Player {winner} wins!", True, GREEN)
                self.screen.blit(win_text, (WINDOW_SIZE // 2 - win_text.get_width() // 2, WINDOW_SIZE // 2 - win_text.get_height() // 2))

            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    game = QuoridorGame()
    game.run()
