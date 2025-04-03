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
    
    # Process command line arguments
    game_mode = "two_player"  # Default
    p1_name = "Player 1"
    p2_name = "Player 2"
    sound = "on"
    music = "on"
    
    # Get arguments if provided
    if len(sys.argv) >= 2:
        game_mode = sys.argv[1]
    if len(sys.argv) >= 3:
        p1_name = sys.argv[2]
    if len(sys.argv) >= 4:
        p2_name = sys.argv[3]
    if len(sys.argv) >= 5:
        sound = sys.argv[4]
    if len(sys.argv) >= 6:
        music = sys.argv[5]
    
    # Create game instance with settings
    game = Game(game_mode, p1_name, p2_name, sound, music)
    
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