import pygame
from pygame.math import Vector2
from src.constants import CELL_SIZE
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Snake:
    def __init__(self, start_position, player_number):
        self._initialize(start_position, player_number)
        self.new_block = False
        
        # Load snake graphics based on player number

        self._load_graphics(player_number)
        folder_path = os.path.join(BASE_DIR, "..", "assets" ,"Sound")
        # print("________________\n")
        # print(folder_path)
        # print("________________")
        self.crunch_sound = pygame.mixer.Sound(os.path.join(folder_path, "crunch.wav"))


    def _initialize(self, start_position, player_number):
        if player_number == 1:
            self.body = [Vector2(start_position[0], start_position[1]),
                         Vector2(start_position[0] - 1, start_position[1]),
                         Vector2(start_position[0] - 2, start_position[1])]
            self.direction = Vector2(1, 0)  
        elif player_number == 2:
            self.body = [Vector2(start_position[0], start_position[1]),
                         Vector2(start_position[0] + 1, start_position[1]),
                         Vector2(start_position[0] + 2, start_position[1])]
            self.direction = Vector2(-1, 0)
    
    def _load_graphics(self, player_number):
        folder_path = os.path.join(BASE_DIR, "..", "assets", "graphics", f"player{player_number}")

        self.head_up = pygame.image.load(os.path.join(folder_path, "head_up.png")).convert_alpha()
        self.head_down = pygame.image.load(os.path.join(folder_path, "head_down.png")).convert_alpha()
        self.head_right = pygame.image.load(os.path.join(folder_path, "head_right.png")).convert_alpha()
        self.head_left = pygame.image.load(os.path.join(folder_path, "head_left.png")).convert_alpha()

        self.tail_up = pygame.image.load(os.path.join(folder_path, "tail_up.png")).convert_alpha()
        self.tail_down = pygame.image.load(os.path.join(folder_path, "tail_down.png")).convert_alpha()
        self.tail_right = pygame.image.load(os.path.join(folder_path, "tail_right.png")).convert_alpha()
        self.tail_left = pygame.image.load(os.path.join(folder_path, "tail_left.png")).convert_alpha()

        self.body_vertical = pygame.image.load(os.path.join(folder_path, "body_vertical.png")).convert_alpha()
        self.body_horizontal = pygame.image.load(os.path.join(folder_path, "body_horizontal.png")).convert_alpha()

        self.body_tr = pygame.image.load(os.path.join(folder_path, "body_tr.png")).convert_alpha()
        self.body_tl = pygame.image.load(os.path.join(folder_path, "body_tl.png")).convert_alpha()
        self.body_br = pygame.image.load(os.path.join(folder_path, "body_br.png")).convert_alpha()
        self.body_bl = pygame.image.load(os.path.join(folder_path, "body_bl.png")).convert_alpha()


    def draw_snake(self, screen, cell_size):
        self.update_head_graphics()
        self.update_tail_graphics()

        for index, block in enumerate(self.body):
            x_pos = block.x * cell_size
            y_pos = block.y * cell_size
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)

            if index == 0:
                screen.blit(self.head, block_rect)
            elif index == len(self.body) - 1:
                screen.blit(self.tail, block_rect)
            else:
                previous_block = self.body[index+1] - block
                next_block = self.body[index-1] - block
                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical, block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal, block_rect)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x ==-1:    
                        screen.blit(self.body_tl, block_rect)
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x ==-1:    
                        screen.blit(self.body_bl, block_rect)
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x ==1:    
                        screen.blit(self.body_tr, block_rect)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x ==1:    
                        screen.blit(self.body_br, block_rect)

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1, 0): self.head = self.head_left
        elif head_relation == Vector2(-1, 0): self.head = self.head_right
        elif head_relation == Vector2(0, 1): self.head = self.head_up
        elif head_relation == Vector2(0, -1): self.head = self.head_down
    
    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1, 0): self.tail = self.tail_left
        elif tail_relation == Vector2(-1, 0): self.tail = self.tail_right
        elif tail_relation == Vector2(0, 1): self.tail = self.tail_up
        elif tail_relation == Vector2(0, -1): self.tail = self.tail_down

    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            
    def add_block(self):
        self.new_block = True
        
    def play_crunch_sound(self):
        self.crunch_sound.play()
        
    def reset(self, start_position, player_number):
        self._initialize(start_position, player_number)