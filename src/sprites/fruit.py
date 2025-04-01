import random
import pygame
from pygame.math import Vector2
from src.constants import CELL_NUMBER
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Fruit:
    def __init__(self):
        self.randomize()
        folder_path = os.path.join(BASE_DIR, "..", "assets" ,"graphics")
        self.apple = pygame.image.load(os.path.join(folder_path, "apple.png")).convert_alpha()
        
    def draw_fruit(self, screen, cell_size):
        fruit_rect = pygame.Rect(self.pos.x * cell_size, self.pos.y * cell_size, cell_size, cell_size)
        screen.blit(self.apple, fruit_rect)
        
    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER - 1)
        self.y = random.randint(0, CELL_NUMBER - 1)
        self.pos = Vector2(self.x, self.y)