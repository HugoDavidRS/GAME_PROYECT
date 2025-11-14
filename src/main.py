import sys
import os
import argparse
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
from src.game import Game
from src.game_multiplayer import MultiplayerGame
from src.constants import GRASS_COLOR_ALT, MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT

def run_game(game_mode="two_player", p1_name="Player 1", p2_name="Player 2", 
             sound="on", music="on", host=None, port=5555, is_host=True):
    """Run a single game session and return when complete"""
    # Initialize pygame
    pygame.mixer.pre_init(44100, 16, 2, 512)
    pygame.init()
    pygame.display.init()
    
    # Create appropriate game instance
    if game_mode in [MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT]:
        print(f"🎮 Iniciando juego multijugador: {'HOST' if is_host else 'CLIENTE'}")
        print(f"🔗 Conectando a: {host}:{port}")
        game = MultiplayerGame(game_mode, p1_name, p2_name, sound, music, host, port, is_host)
    else:
        print(f"🎮 Iniciando juego local: {game_mode}")
        game = Game(game_mode, p1_name, p2_name, sound, music)
    
    # Game loop
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Clean up before returning
                if hasattr(game, 'cleanup'):
                    game.cleanup()
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                pygame.quit()
                return "QUIT"
                
            if event.type == game.SCREEN_UPDATE:
                if game.game_state == 'playing':
                    game.update()
                    
            # Handle other inputs
            game.handle_input(event)
            
        # Handle network messages for multiplayer (outside event loop for better performance)
        if hasattr(game, 'handle_network_messages'):
            game.handle_network_messages()
                
        # Update during countdown and connecting states
        if game.game_state in ['countdown', 'connecting']:
            game.update()
            
        # Drawing
        game.screen.fill(GRASS_COLOR_ALT)
        
        if game.game_state == 'countdown':
            game.draw_grass()
            if hasattr(game, 'draw_countdown'):
                game.draw_countdown()
        else:
            game.draw_elements()
            
        pygame.display.update()
        game.clock.tick(60)  # Limit to 60 frames per second
        
        # Check for menu return
        if getattr(game, 'game_state', None) == "MENU":
            # Clean up before returning
            if hasattr(game, 'cleanup'):
                game.cleanup()
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            pygame.quit()
            return "MENU"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Snake Game')
    parser.add_argument('game_mode', nargs='?', default="single_player")
    parser.add_argument('p1_name', nargs='?', default="Player 1")
    parser.add_argument('p2_name', nargs='?', default="Player 2")
    parser.add_argument('sound', nargs='?', default="on")
    parser.add_argument('music', nargs='?', default="on")
    
    # Multiplayer arguments
    parser.add_argument('--host', help='Server host address')
    parser.add_argument('--port', type=int, default=5555, help='Server port')
    parser.add_argument('--is-host', type=int, default=1, help='Is host (1) or client (0)')
    
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # If parameters were provided when launching the script
    if len(sys.argv) >= 2:
        # Extract multiplayer parameters
        host = args.host
        port = args.port
        is_host = bool(args.is_host)
        
        # Run game with provided parameters
        result = run_game(
            game_mode=args.game_mode,
            p1_name=args.p1_name,
            p2_name=args.p2_name,
            sound=args.sound,
            music=args.music,
            host=host,
            port=port,
            is_host=is_host
        )
        
        # After game ends, check result
        if result == "MENU":
            # Import and run menu
            from src.ui.menu import run_menu
            menu_result = run_menu()
            
            if menu_result == "QUIT":
                sys.exit(0)
    else:
        # No parameters provided, start with menu
        from src.ui.menu import run_menu
        run_menu()

if __name__ == "__main__":
    main()