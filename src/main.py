import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
from src.game import Game
from src.constants import GRASS_COLOR_ALT

def run_game(game_mode="two_player", p1_name="Player 1", p2_name="Player 2", sound="on", music="on"):
    """Run a single game session and return when complete"""
    # Initialize pygame
    pygame.mixer.pre_init(44100, 16, 2, 512)
    pygame.init()
    pygame.display.init()
    
    # Create game instance with settings
    game = Game(game_mode, p1_name, p2_name, sound, music)
    
    # Game loop
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Clean up pygame before returning
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                pygame.quit()
                return "QUIT"  # Signal to exit the application
                
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
        
        # Check for menu return
        if game.game_state == "MENU":
            # Clean up pygame before returning
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            pygame.quit()
            return "MENU"  # Signal to go back to menu

def main():
    # If parameters were provided when launching the script
    if len(sys.argv) >= 2:
        game_mode = sys.argv[1]
        p1_name = sys.argv[2] if len(sys.argv) >= 3 else "Player 1"
        p2_name = sys.argv[3] if len(sys.argv) >= 4 else "Player 2"
        sound = sys.argv[4] if len(sys.argv) >= 5 else "on"
        music = sys.argv[5] if len(sys.argv) >= 6 else "on"
        
        # Run game directly with provided parameters
        result = run_game(game_mode, p1_name, p2_name, sound, music)
        
        # After game ends, check result
        if result == "MENU":
            # Import and run menu
            from src.ui.menu import run_menu
            menu_result = run_menu()
            
            if menu_result == "QUIT":
                sys.exit(0)
            # If not QUIT, the script will exit and menu.py will handle launching a new game
    else:
        # No parameters provided, start with menu
        from src.ui.menu import run_menu
        run_menu()

if __name__ == "__main__":
    main()