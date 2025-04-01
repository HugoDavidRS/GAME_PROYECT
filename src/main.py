import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
from src.game import Game
from src.constants import GRASS_COLOR_ALT

def main():
    # Initialize pygame
    pygame.mixer.pre_init(44100, 16, 2, 512)
    pygame.init()
    
    # Create game instance
    game = Game()
    
    # Main game loop
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == game.SCREEN_UPDATE:
                if game.game_state == 'playing':
                    game.update()
                    
            # Handle other inputs
            game.handle_input(event)
                
        # Update during countdown
        if game.game_state in ['countdown']:
            game.update()
            
        # Drawing
        game.screen.fill(GRASS_COLOR_ALT)
        
        if game.game_state == 'countdown':
            game.draw_grass()
            game.draw_countdown()
        else:
            game.draw_elements()
            
        pygame.display.update()
        game.clock.tick(60)  # Limit to 60 frames per second

if __name__ == "__main__":
    main()