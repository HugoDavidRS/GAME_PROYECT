import random
import pygame
from pygame.math import Vector2
from src.constants import CELL_NUMBER
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Mines:
    def __init__(self):
        self.randomize()
        folder_path = os.path.join(BASE_DIR, "..", "assets" ,"graphics")
        self.mine = pygame.image.load(os.path.join(folder_path, "mine.png")).convert_alpha()

    def draw_mine(self, screen, cell_size):
        mine_rect = pygame.Rect(self.pos.x * cell_size, self.pos.y * cell_size, cell_size, cell_size)
        screen.blit(self.mine, mine_rect)
        
    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER - 1)
        self.y = random.randint(0, CELL_NUMBER - 1)
        self.pos = Vector2(self.x, self.y)