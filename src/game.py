import pygame
import os, sys
from pygame.math import Vector2
from src.ui.menu import run_menu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from src.constants import CELL_SIZE, CELL_NUMBER, GRASS_COLOR, GRASS_COLOR_ALT
from src.sprites.snake import Snake
from src.sprites.fruit import Fruit
from src.sprites.button import Button
from src.sprites.mines import Mines
from src.services.dbhelper import DatabaseService

class Game:
    def __init__(self, game_mode="two_player", p1_name="Player 1", p2_name="Player 2", sound="on", music="on"):
        self.screen = pygame.display.set_mode((CELL_NUMBER * CELL_SIZE, CELL_NUMBER * CELL_SIZE))
        self.clock = pygame.time.Clock()
        font_path = os.path.join(BASE_DIR, "..", "assets", "Font", "PoetsenOne-Regular.ttf")
        
        self.game_font = pygame.font.Font(font_path, 50)
        self.db_service = DatabaseService()

        
        # Game settings
        self.game_mode = game_mode
        self.p1_name = p1_name
        self.p2_name = p2_name
        self.sound_enabled = True if sound == "on" else False
        self.music_enabled = True if music == "on" else False

        
        # Game objects
        self.snake = Snake(start_position=(3, 10), player_number=1)
        
        # Create second snake only for multiplayer mode
        self.snake2 = None
        if self.game_mode == "two_player":
            self.snake2 = Snake(start_position=(22, 10), player_number=2)
        
        self.fruit = Fruit()
        
        # Add mine object
        self.mine = Mines()
        # Make sure the mine doesn't spawn in restricted areas initially
        self.validate_mine_position()
        
        # Game state
        self.game_state = 'start'
        
        # Buttons
        button_width, button_height = 200, 50
        button_x = (CELL_NUMBER * CELL_SIZE - button_width) // 2
        button_y = (CELL_NUMBER * CELL_SIZE - button_height) // 2
        
        self.start_button = Button(button_x, button_y, button_width, button_height, 
                           'Start Game', (0, 200, 0), (255, 255, 255))

        self.reset_button = Button(button_x, button_y, button_width, button_height, 
                           'Replay!', (255, 165, 0), (0, 0, 0))

        spacing = 10
        adjusted_height = button_height - 5

        self.quit_button = Button(button_x, button_y + adjusted_height + spacing, 
                                    button_width, adjusted_height, 
                                    'Quit Game', (200, 0, 0), (255, 255, 255))

        self.menu_button = Button(button_x, button_y + 2 * (adjusted_height + spacing), 
                                    button_width, adjusted_height, 
                                    'Menu', (0, 150, 255), (0, 0, 0))
        
        text_x = button_x + button_width // 2
        text_y = button_y - 30
        self.game_over_txt_pos = (text_x, text_y)
        
        # Countdown
        self.countdown = 4
        self.last_countdown_tick = None
        
        # Set up timer event
        self.SCREEN_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(self.SCREEN_UPDATE, 150)

    def validate_mine_position(self):
        # Regenerate mine position until it's valid
        valid_position = False
        while not valid_position:
            # Check if mine is in restricted area (top rows, leftmost and rightmost)
            in_restricted_area = False
            
            # Checking top 2 rows, leftmost and rightmost 3 columns
            if self.mine.pos.y < 2:  # First two rows
                if self.mine.pos.x < 3 or self.mine.pos.x >= CELL_NUMBER - 3:
                    in_restricted_area = True
            
            # Check if mine is on the same position as fruit
            on_fruit = self.mine.pos == self.fruit.pos
            
            # Check if mine is on snake bodies
            on_snake = False
            for block in self.snake.body:
                if self.mine.pos == block:
                    on_snake = True
                    break
                    
            if self.game_mode == "two_player" and self.snake2:
                for block in self.snake2.body:
                    if self.mine.pos == block:
                        on_snake = True
                        break
            
            if not in_restricted_area and not on_fruit and not on_snake:
                valid_position = True
            else:
                self.mine.randomize()  # Try a new position

    def update(self):

        if self.game_state == 'countdown':
            # Handle countdown timer
            current_time = pygame.time.get_ticks()
            if self.last_countdown_tick is None or current_time - self.last_countdown_tick >= 1000:
                self.countdown -= 1
                self.last_countdown_tick = current_time
                if self.countdown <= 0:
                    self.game_state = 'playing'
                    if self.music_enabled:
                        game_music = os.path.join(BASE_DIR, "..", "assets", "Sound", "game_music.wav")
                        pygame.mixer.init()
                        pygame.mixer.music.load(game_music)
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
        elif self.game_state == 'playing':
            self.snake.move_snake()
            if self.game_mode == "two_player" and self.snake2:
                self.snake2.move_snake()
            self.check_collision()
            self.check_fail()

    def draw_elements(self):
        # print(f"Mine position: {self.mine.pos}")
        self.draw_grass()
        if self.game_state == 'start':
            self.start_button.draw(self.screen)
        elif self.game_state == 'countdown':
            self.draw_countdown()
        elif self.game_state == 'playing':
            self.fruit.draw_fruit(self.screen, CELL_SIZE)
            # Draw the mine
            self.mine.draw_mine(self.screen, CELL_SIZE)
            self.snake.draw_snake(self.screen, CELL_SIZE)
            if self.game_mode == "two_player" and self.snake2:
                self.snake2.draw_snake(self.screen, CELL_SIZE)
        elif self.game_state == 'game_over':
            pygame.mixer.music.stop()
            font_path = os.path.join(BASE_DIR, "..", "assets", "Font", "PoetsenOne-Regular.ttf")
            font = pygame.font.Font(font_path, 50) 

            # Determine message based on winner
            if self.winner == 1:
                game_over_text = f"{self.p1_name} Wins!"
                text_color = (0, 0, 200)  
            elif self.winner == 2:
                game_over_text = f"{self.p2_name} Wins!"
                text_color = (0, 0, 200)  
            elif self.winner == 0:
                game_over_text = "It's a Tie!"
                text_color = (255, 0, 0) 
            else:
                game_over_text = "Game Over"
                text_color = (255, 0, 0)

            game_over_surface = font.render(game_over_text, True, text_color)  
            text_rect = game_over_surface.get_rect(center=self.game_over_txt_pos)  
            self.screen.blit(game_over_surface, text_rect)

            self.reset_button.draw(self.screen)
            self.quit_button.draw(self.screen)
            self.menu_button.draw(self.screen)
        self.draw_score()

    def draw_score(self):
        margin = 20  
        snake_size = 40  
        padding = 10  
        bottom_padding = 2  

        # Player 1 (Left)
        score_text_p1 = str(len(self.snake.body) - 3)  
        score_surface_p1 = self.game_font.render(score_text_p1, True, (56, 74, 12))

        snake_image_p1 = pygame.transform.scale(self.fruit.p1, (snake_size, snake_size))
        snake_rect_p1 = snake_image_p1.get_rect(midleft=(margin, margin + 12))
        score_rect_p1 = score_surface_p1.get_rect(midleft=(snake_rect_p1.right + 10, snake_rect_p1.centery))

        bg_rect_p1 = pygame.Rect(
            snake_rect_p1.left - padding, snake_rect_p1.top - padding,
            snake_rect_p1.width + score_rect_p1.width + padding * 2 + 10, 
            max(snake_rect_p1.height, score_rect_p1.height) + padding + bottom_padding
        )

        # Draw Player 1's score (Left)
        pygame.draw.rect(self.screen, (167, 209, 61), bg_rect_p1, border_radius=8)
        pygame.draw.rect(self.screen, (56, 74, 12), bg_rect_p1, 2, border_radius=8)
        self.screen.blit(snake_image_p1, snake_rect_p1)
        self.screen.blit(score_surface_p1, score_rect_p1)

        # Only draw Player 2's score in two-player mode
        if self.game_mode == "two_player" and self.snake2:
            # Player 2 (Right)
            score_text_p2 = str(len(self.snake2.body) - 3)  
            score_surface_p2 = self.game_font.render(score_text_p2, True, (56, 74, 12))
        
            snake_image_p2 = pygame.transform.scale(self.fruit.p2, (snake_size, snake_size))
            score_rect_p2 = score_surface_p2.get_rect(midright=(CELL_SIZE * CELL_NUMBER - margin, margin + 12))
            snake_rect_p2 = snake_image_p2.get_rect(midright=(score_rect_p2.left - 10, score_rect_p2.centery))

            bg_rect_p2 = pygame.Rect(
                snake_rect_p2.left - padding, snake_rect_p2.top - padding,
                snake_rect_p2.width + score_rect_p2.width + padding * 2 + 10, 
                max(snake_rect_p2.height, score_rect_p2.height) + padding + bottom_padding
            )

            # Draw Player 2's score (Right)
            pygame.draw.rect(self.screen, (167, 209, 61), bg_rect_p2, border_radius=8)
            pygame.draw.rect(self.screen, (56, 74, 12), bg_rect_p2, 2, border_radius=8)
            self.screen.blit(snake_image_p2, snake_rect_p2)
            self.screen.blit(score_surface_p2, score_rect_p2)

    def draw_countdown(self):
        countdown_text = self.game_font.render(str(self.countdown), True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(CELL_NUMBER * CELL_SIZE // 2, CELL_NUMBER * CELL_SIZE // 2))
        self.screen.blit(countdown_text, countdown_rect)


    def check_collision(self):
        # Check if snakes eat fruit
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            if self.sound_enabled:
                self.snake.play_crunch_sound()
            
        if self.game_mode == "two_player" and self.snake2 and self.fruit.pos == self.snake2.body[0]:
            self.fruit.randomize()
            self.snake2.add_block()
            if self.sound_enabled:
                self.snake2.play_crunch_sound()
        
        # Check if snakes hit mines
        if self.mine.pos == self.snake.body[0]:
            if self.sound_enabled:
                self.snake.play_boom_sound()
            if len(self.snake.body) >= 5:
                self.snake.body.pop()
                self.snake.body.pop()
            elif len(self.snake.body) == 4:
                self.snake.body.pop()
            elif len(self.snake.body) == 3:
                if self.game_mode == "two_player":
                    self.game_over(2)
                else:
                    self.game_over(3)
            # Reposition the mine
            self.mine.randomize()
            self.validate_mine_position()
            
        if self.game_mode == "two_player" and self.snake2 and self.mine.pos == self.snake2.body[0]:
            if self.sound_enabled:
                self.snake.play_boom_sound()
            if len(self.snake2.body) >= 5:  # Ensure the snake keeps at least 3 blocks (minimum length)
                self.snake2.body.pop()
                self.snake2.body.pop()
            elif len(self.snake2.body) == 4:
                self.snake2.body.pop()
            elif len(self.snake2.body) == 3:
                self.game_over(1)
            # Reposition the mine
            self.mine.randomize()
            self.validate_mine_position()
            
        # Make sure fruit doesn't spawn on snake bodies or the mine
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()
                
        if self.game_mode == "two_player" and self.snake2:
            for block in self.snake2.body[1:]:
                if block == self.fruit.pos:
                    self.fruit.randomize()
        
        # Check if fruit spawned on mine
        if self.fruit.pos == self.mine.pos:
            self.fruit.randomize()
        
        # Apple spawning behind score fix
        for y in range(2):
            for x in range(3):
                if self.fruit.pos == (x, y):
                    self.fruit.randomize()

            for x in range(CELL_NUMBER - 3, CELL_NUMBER):
                if self.fruit.pos == (x, y):
                    self.fruit.randomize()
                    
        # Mine spawning behind score fix and in restricted areas
        for y in range(2):
            for x in range(3):
                if self.mine.pos == (x, y):
                    self.mine.randomize()
                    self.validate_mine_position()

            for x in range(CELL_NUMBER - 3, CELL_NUMBER):
                if self.mine.pos == (x, y):
                    self.mine.randomize()
                    self.validate_mine_position()


    def check_fail(self):
        snake1_dead = False
        snake2_dead = False

        # Snake 1 hits walls
        if not 0 <= self.snake.body[0].x < CELL_NUMBER or not 0 <= self.snake.body[0].y < CELL_NUMBER:
            print("Snake 1 hit the wall")
            snake1_dead = True
                
        # Snake 1 hits its own body
        for block in self.snake.body[1:]:
            if block.x == self.snake.body[0].x and block.y == self.snake.body[0].y:
                print("Snake 1 hit itself")
                snake1_dead = True

        if self.game_mode == "two_player" and self.snake2:
            # Snake 2 hits walls
            if not 0 <= self.snake2.body[0].x < CELL_NUMBER or not 0 <= self.snake2.body[0].y < CELL_NUMBER:
                print("Snake 2 hit the wall")
                snake2_dead = True

            # Snake 2 hits its own body
            for block in self.snake2.body[1:]:
                if block.x == self.snake2.body[0].x and block.y == self.snake2.body[0].y:
                    print("Snake 2 hit itself")
                    snake2_dead = True

            # Snake 1 hits Snake 2
            for block in self.snake2.body:
                if block.x == self.snake.body[0].x and block.y == self.snake.body[0].y:
                    self.snake.play_hiss_sound()
                    print("Snake 1 hit Snake 2's body")
                    snake1_dead = True

            # Snake 2 hits Snake 1
            for block in self.snake.body:
                if block.x == self.snake2.body[0].x and block.y == self.snake2.body[0].y:
                    self.snake2.play_hiss_sound()
                    print("Snake 2 hit Snake 1's body")
                    snake2_dead = True

        # Handle game over conditions
        if self.game_mode == "single_player":
            if snake1_dead:
                self.game_over(3)  # Game over in single player
        else:
            # Two-player mode logic
            if snake1_dead and snake2_dead:
                snake1_score = len(self.snake.body) - 3
                snake2_score = len(self.snake2.body) - 3

                print(f"Scores -> Snake 1: {snake1_score}, Snake 2: {snake2_score}")
                
                if snake1_score > snake2_score:
                    self.game_over(1)  # Snake 1 wins
                elif snake1_score < snake2_score:
                    self.game_over(2)  # Snake 2 wins
                else:
                    self.game_over(0)  # It's a tie
            elif snake1_dead:
                self.game_over(2)  # Snake 2 wins
            elif snake2_dead:
                self.game_over(1)  # Snake 1 wins



    def game_over(self, winner):
        self.game_state = 'game_over'
        self.winner = winner
        self.game_state = 'game_over'
        self.winner = winner
    
        # Update scores in database
        if self.game_mode == "single_player":
        # In single player, update score when game ends
            score = len(self.snake.body) - 3
            self.db_service.update_score_singleplayer(self.p1_name, score)
        else:
        # In multiplayer, update both players' scores
            score1 = len(self.snake.body) - 3
            score2 = len(self.snake2.body) - 3
        
            self.db_service.update_score_multiplayer(self.p1_name, score1)
            self.db_service.update_score_multiplayer(self.p2_name, score2)
            if winner == 1:
                self.db_service.update_multiplayer_win(self.p1_name)
            elif winner == 2:
                self.db_service.update_multiplayer_win(self.p2_name)

    def reset_game(self):
        self.snake.reset(start_position=(3, 10), player_number=1)
        if self.game_mode == "two_player" and self.snake2:
            self.snake2.reset(start_position=(22, 10), player_number=2)
        self.fruit.randomize()
        self.mine.randomize()
        self.validate_mine_position()
        self.start_countdown()

    def start_countdown(self):
        self.game_state = 'countdown'
        self.countdown = 4
        self.last_countdown_tick = None

    def draw_grass(self):
        for row in range(CELL_NUMBER):
            if row % 2 == 0:   
                for col in range(CELL_NUMBER):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, GRASS_COLOR, grass_rect)
            else:
                for col in range(CELL_NUMBER):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, GRASS_COLOR, grass_rect)
                        
    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.game_state == 'start':
                if self.start_button.is_clicked(event.pos):
                    self.start_countdown()
            elif self.game_state == 'game_over':
                if self.reset_button.is_clicked(event.pos):
                    self.reset_game()
                if self.quit_button.is_clicked(event.pos):
                    pygame.quit()
                    os._exit(0)
                if self.menu_button.is_clicked(event.pos):
                    self.game_state="MENU"
                    return
                    
        if self.game_state == 'playing' and event.type == pygame.KEYDOWN:
            # Player 1 controls (WASD)
            if event.key == pygame.K_w:
                if self.snake.direction.y != 1:
                    self.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_s:
                if self.snake.direction.y != -1:
                    self.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_d:
                if self.snake.direction.x != -1:
                    self.snake.direction = Vector2(1, 0)
            if event.key == pygame.K_a:
                if self.snake.direction.x != 1:
                    self.snake.direction = Vector2(-1, 0)
                    
            # Player 2 controls (Arrow keys) - only in two-player mode
            if self.game_mode == "two_player" and self.snake2:
                if event.key == pygame.K_UP:
                    if self.snake2.direction.y != 1:
                        self.snake2.direction = Vector2(0, -1)
                if event.key == pygame.K_DOWN:
                    if self.snake2.direction.y != -1:
                        self.snake2.direction = Vector2(0, 1)
                if event.key == pygame.K_RIGHT:
                    if self.snake2.direction.x != -1:
                        self.snake2.direction = Vector2(1, 0)
                if event.key == pygame.K_LEFT:
                    if self.snake2.direction.x != 1:
                        self.snake2.direction = Vector2(-1, 0)