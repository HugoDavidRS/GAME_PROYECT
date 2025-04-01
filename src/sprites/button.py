import pygame
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        folder_path = os.path.join(BASE_DIR, "..", "assets" ,"Font")
        self.font = pygame.font.Font(os.path.join(folder_path, "PoetsenOne-Regular.ttf"), 25)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)