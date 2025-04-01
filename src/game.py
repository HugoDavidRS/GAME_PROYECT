import pygame
import os
from pygame.math import Vector2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from src.constants import CELL_SIZE, CELL_NUMBER, GRASS_COLOR, GRASS_COLOR_ALT
from src.sprites.snake import Snake
from src.sprites.fruit import Fruit
from src.sprites.button import Button

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((CELL_NUMBER * CELL_SIZE, CELL_NUMBER * CELL_SIZE))
        self.clock = pygame.time.Clock()
        font_path = os.path.join(BASE_DIR, "..", "assets", "Font", "PoetsenOne-Regular.ttf")
        # print(font_path)
        self.game_font = pygame.font.Font(font_path, 50)
        
        # Game objects
        self.snake = Snake(start_position=(3, 10), player_number=1)
        self.snake2 = Snake(start_position=(22, 10), player_number=2) 
        self.fruit = Fruit()
        
        # Game state
        self.game_state = 'start'
        
        # Buttons
        button_width, button_height = 200, 50
        button_x = (CELL_NUMBER * CELL_SIZE - button_width) // 2
        button_y = (CELL_NUMBER * CELL_SIZE - button_height) // 2
        
        self.start_button = Button(button_x, button_y, button_width, button_height, 
                                   'Start Game', (0, 255, 0), (0, 0, 0))
        
        self.reset_button = Button(button_x, button_y, button_width, button_height, 
                                   'Start Again', (255, 0, 0), (255, 255, 255))
        
        # Countdown
        self.countdown = 4
        self.last_countdown_tick = None
        
        # Set up timer event
        self.SCREEN_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(self.SCREEN_UPDATE, 150)

    def update(self):
        if self.game_state == 'countdown':
            # Handle countdown timer
            current_time = pygame.time.get_ticks()
            if self.last_countdown_tick is None or current_time - self.last_countdown_tick >= 1000:
                self.countdown -= 1
                self.last_countdown_tick = current_time
                if self.countdown <= 0:
                    self.game_state = 'playing'
        elif self.game_state == 'playing':
            self.snake.move_snake() 
            self.snake2.move_snake()
            self.check_collision()
            self.check_fail()
            
    def draw_elements(self):
        self.draw_grass()
        
        if self.game_state == 'start':
            self.start_button.draw(self.screen)
        elif self.game_state == 'countdown':
            self.draw_countdown()
        elif self.game_state == 'playing':
            self.fruit.draw_fruit(self.screen, CELL_SIZE)
            self.snake.draw_snake(self.screen, CELL_SIZE)
            self.snake2.draw_snake(self.screen, CELL_SIZE)
        elif self.game_state == 'game_over':
            self.reset_button.draw(self.screen)

    def draw_countdown(self):
        countdown_text = self.game_font.render(str(self.countdown), True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(CELL_NUMBER * CELL_SIZE // 2, CELL_NUMBER * CELL_SIZE // 2))
        self.screen.blit(countdown_text, countdown_rect)

    def check_collision(self):
        # Check if snakes eat fruit
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()
            
        if self.fruit.pos == self.snake2.body[0]:
            self.fruit.randomize()
            self.snake2.add_block()
            self.snake2.play_crunch_sound()
            
        # Make sure fruit doesn't spawn on snake bodies
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()
                
        for block in self.snake2.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()

    def check_fail(self):
        # Check if either snake hits wall
        if not 0 <= self.snake.body[0].x < CELL_NUMBER or not 0 <= self.snake.body[0].y < CELL_NUMBER:
            self.game_over()
            
        if not 0 <= self.snake2.body[0].x < CELL_NUMBER or not 0 <= self.snake2.body[0].y < CELL_NUMBER:
            self.game_over()
            
        # Check if snakes hit themselves
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()
                
        for block in self.snake2.body[1:]:
            if block == self.snake2.body[0]:
                self.game_over()
                
        # Check if snakes hit each other
        for block in self.snake2.body:
            if block == self.snake.body[0]:
                self.game_over()
                
        for block in self.snake.body:
            if block == self.snake2.body[0]:
                self.game_over()

    def game_over(self):
        self.game_state = 'game_over'

    def reset_game(self):
        self.snake.reset(start_position=(3, 10), player_number=1)
        self.snake2.reset(start_position=(22, 10), player_number=2)
        self.fruit.randomize()
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
                    
        if self.game_state == 'playing' and event.type == pygame.KEYDOWN:
            # Player 1 controls (Arrow keys)
            if event.key == pygame.K_UP:
                if self.snake.direction.y != 1:
                    self.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN:
                if self.snake.direction.y != -1:
                    self.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_RIGHT:
                if self.snake.direction.x != -1:
                    self.snake.direction = Vector2(1, 0)
            if event.key == pygame.K_LEFT:
                if self.snake.direction.x != 1:
                    self.snake.direction = Vector2(-1, 0)
                    
            # Player 2 controls (WASD)
            if event.key == pygame.K_w:
                if self.snake2.direction.y != 1:
                    self.snake2.direction = Vector2(0, -1)
            if event.key == pygame.K_s:
                if self.snake2.direction.y != -1:
                    self.snake2.direction = Vector2(0, 1)
            if event.key == pygame.K_d:
                if self.snake2.direction.x != -1:
                    self.snake2.direction = Vector2(1, 0)
            if event.key == pygame.K_a:
                if self.snake2.direction.x != 1:
                    self.snake2.direction = Vector2(-1, 0)  