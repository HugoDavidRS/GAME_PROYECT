import tkinter as tk
import tkinter.ttk as ttk
import subprocess
import sys
import os

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Slither.io Clone")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(self.main_frame, text="Slither.io Clone", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # Game mode frame
        mode_frame = ttk.LabelFrame(self.main_frame, text="Game Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=10)
        
        # Game mode radio buttons
        self.game_mode = tk.StringVar(value="two_player")
        ttk.Radiobutton(mode_frame, text="Two Player Mode", variable=self.game_mode, value="two_player").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Single Player Mode", variable=self.game_mode, value="single_player").pack(anchor=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Start game button
        start_button = ttk.Button(buttons_frame, text="Start Game", command=self.start_game)
        start_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_button = ttk.Button(buttons_frame, text="Exit", command=self.root.destroy)
        exit_button.pack(side=tk.RIGHT, padx=5)
        
    def start_game(self):
        # Get the current working directory and format it correctly for subprocess
        # script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'main.py')

        
        # Add game mode as command line argument (can be used to modify game behavior)
        mode = self.game_mode.get()
        
        # Launch the Pygame window and close the tkinter window
        self.root.destroy()
        
        # Use Python executable that's currently running to launch the game
        python_executable = sys.executable
        subprocess.Popen([python_executable, main_py_path, mode])

def run_menu():
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()

if __name__ == "__main__":
    run_menu()