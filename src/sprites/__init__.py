# This file makes the sprites directory a Python package
# This allows for importing from src.sprites

from src.sprites.snake import Snake
from src.sprites.fruit import Fruit
from src.sprites.button import Button

__all__ = ['Snake', 'Fruit', 'Button']