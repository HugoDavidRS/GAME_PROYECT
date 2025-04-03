import customtkinter as ctk
import subprocess
import sys
import os
from PIL import Image, ImageTk

class MainMenu:
    def __init__(self):
        # Set theme and appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create root window
        self.root = ctk.CTk()
        self.root.title("Slither.io Clone")
        self.root.geometry("600x920")
        self.root.resizable(False, False)
        
        # Initialize variables
        self.game_mode = ctk.StringVar(value="single_player")
        self.player1_name = ctk.StringVar(value="Player_1")
        self.player2_name = ctk.StringVar(value="Player_2")
        self.sound_effects = ctk.BooleanVar(value=True)
        self.music = ctk.BooleanVar(value=True)
        
        # Create UI elements
        self.create_welcome_header()
        self.create_game_mode_section()
        self.create_player_name_section()
        self.create_sound_controls()
        self.create_leaderboard()
        self.create_buttons()
        
        # Update player name fields based on initial game mode
        self.update_player_fields()
        
    def create_welcome_header(self):
        # Logo/Welcome section (you can replace with your own logo image)
        self.header_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Try to load a logo image (you would need to create this file)
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_logo.png")
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((80, 80))
            self.logo = ImageTk.PhotoImage(logo_img)
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo, text="")
            self.logo_label.pack(side="left", padx=15, pady=15)
        except:
            # If logo can't be loaded, use text instead
            pass
        
        # Welcome message
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=10, pady=15, fill="both", expand=True)
        
        welcome_label = ctk.CTkLabel(
            title_frame, 
            text="Welcome to Slither.io Clone!", 
            font=ctk.CTkFont(family="Arial", size=24, weight="bold")
        )
        welcome_label.pack(anchor="w", pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Slither your way to the top of the leaderboard!",
            font=ctk.CTkFont(family="Arial", size=14)
        )
        subtitle_label.pack(anchor="w")
    
    def create_game_mode_section(self):
        # Game mode selection
        mode_frame = ctk.CTkFrame(self.root, corner_radius=10)
        mode_frame.pack(fill="x", padx=20, pady=10)
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Select Game Mode",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        mode_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Radio buttons for game mode
        single_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Single Player",
            variable=self.game_mode,
            value="single_player",
            command=self.update_player_fields,
            font=ctk.CTkFont(size=14)
        )
        single_radio.pack(anchor="w", padx=25, pady=5)
        
        multi_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Two Player",
            variable=self.game_mode,
            value="two_player",
            command=self.update_player_fields,
            font=ctk.CTkFont(size=14)
        )
        multi_radio.pack(anchor="w", padx=25, pady=(5, 15))
    
    def create_player_name_section(self):
        # Player name input section
        self.player_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.player_frame.pack(fill="x", padx=20, pady=10)
        
        name_label = ctk.CTkLabel(
            self.player_frame,
            text="Player Names",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Player 1 name input
        self.p1_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.p1_frame.pack(fill="x", padx=15, pady=5)
        
        p1_label = ctk.CTkLabel(self.p1_frame, text="Player 1:", font=ctk.CTkFont(size=14))
        p1_label.pack(side="left", padx=(10, 5))
        
        p1_entry = ctk.CTkEntry(self.p1_frame, textvariable=self.player1_name, width=200)
        p1_entry.pack(side="left", padx=5)
        
        # Player 2 name input (will be shown/hidden based on game mode)
        self.p2_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.p2_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        p2_label = ctk.CTkLabel(self.p2_frame, text="Player_2:", font=ctk.CTkFont(size=14))
        p2_label.pack(side="left", padx=(10, 5))
        
        p2_entry = ctk.CTkEntry(self.p2_frame, textvariable=self.player2_name, width=200)
        p2_entry.pack(side="left", padx=5)
    
    def create_sound_controls(self):
        # Sound controls section
        sound_frame = ctk.CTkFrame(self.root, corner_radius=10)
        sound_frame.pack(fill="x", padx=20, pady=10)
        
        sound_label = ctk.CTkLabel(
            sound_frame,
            text="Sound Settings",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        sound_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Sound effects switch
        effects_switch = ctk.CTkSwitch(
            sound_frame,
            text="Sound Effects",
            variable=self.sound_effects,
            font=ctk.CTkFont(size=14)
        )
        effects_switch.pack(anchor="w", padx=25, pady=5)
        
        # Music switch
        music_switch = ctk.CTkSwitch(
            sound_frame,
            text="Background Music",
            variable=self.music,
            font=ctk.CTkFont(size=14)
        )
        music_switch.pack(anchor="w", padx=25, pady=(5, 15))
    
    def create_leaderboard(self):
        # Leaderboard section
        lb_frame = ctk.CTkFrame(self.root, corner_radius=10)
        lb_frame.pack(fill="x", padx=20, pady=10)
        
        lb_label = ctk.CTkLabel(
            lb_frame,
            text="Leaderboard",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        lb_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Mock leaderboard data (you'll replace with actual data later)
        leaderboard_data = [
            ("SnakeMaster", 1450),
            ("Viper", 1320),
            ("SlitherPro", 1290),
            ("SerpentKing", 1180),
            ("CobraQueen", 1050)
        ]
        
        # Header row
        header_frame = ctk.CTkFrame(lb_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(0, 5))
        
        rank_header = ctk.CTkLabel(header_frame, text="Rank", width=50, font=ctk.CTkFont(weight="bold"))
        rank_header.pack(side="left", padx=5)
        
        name_header = ctk.CTkLabel(header_frame, text="Name", width=150, font=ctk.CTkFont(weight="bold"))
        name_header.pack(side="left", padx=5)
        
        score_header = ctk.CTkLabel(header_frame, text="Score", width=80, font=ctk.CTkFont(weight="bold"))
        score_header.pack(side="left", padx=5)
        
        # Leaderboard entries
        for i, (name, score) in enumerate(leaderboard_data, 1):
            entry_frame = ctk.CTkFrame(lb_frame, fg_color="transparent")
            entry_frame.pack(fill="x", padx=15, pady=2)
            
            rank_label = ctk.CTkLabel(entry_frame, text=f"{i}", width=50)
            rank_label.pack(side="left", padx=5)
            
            name_label = ctk.CTkLabel(entry_frame, text=name, width=150, anchor="w")
            name_label.pack(side="left", padx=5)
            
            score_label = ctk.CTkLabel(entry_frame, text=str(score), width=80)
            score_label.pack(side="left", padx=5)
            
        lb_frame.pack(pady=(10, 15))
    
    def create_buttons(self):
        # Action buttons
        button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Exit button
        exit_button = ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.exit_program,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=100
        )
        exit_button.pack(side="left", padx=20)
        
        # Play button
        play_button = ctk.CTkButton(
            button_frame,
            text="Play Game",
            command=self.start_game,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            font=ctk.CTkFont(weight="bold"),
            width=150
        )
        play_button.pack(side="right", padx=20)
    
    def update_player_fields(self):
        # Show/hide player 2 input based on game mode
        if self.game_mode.get() == "single_player":
            self.p2_frame.pack_forget()
        else:
            self.p2_frame.pack(fill="x", padx=15, pady=(5, 15))
    
    def exit_program(self):
        self.root.destroy()
        os._exit(0)
    
    def start_game(self):
        # Get player names
        p1_name = self.player1_name.get()
        p2_name = self.player2_name.get()
        
        # Check if names are provided
        if not p1_name:
            self.show_error("Please enter a name for Player 1")
            return
            
        if self.game_mode.get() == "two_player" and not p2_name:
            self.show_error("Please enter a name for Player 2")
            return
        
        # Validation checks
        if not p1_name or " " in p1_name:
            self.show_error("Player 1 name cannot be empty or contain spaces.")
            return
            
        if self.game_mode.get() == "two_player":
            if not p2_name or " " in p2_name:
                self.show_error("Player 2 name cannot be empty or contain spaces.")
                return
        
        # Get game parameters
        mode = self.game_mode.get()
        sound = "on" if self.sound_effects.get() else "off"
        music = "on" if self.music.get() else "off"
        
        # Print the parameters for now (you'll replace with game launch later)
        print(f"Starting game with: Mode={mode}, P1={p1_name}, P2={p2_name}, Sound={sound}, Music={music}")
        
        # Close the menu before launching the game
        self.root.destroy()
        
        # Use Python executable to start the game (modify path as needed)
        main_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'main.py')
        python_executable = sys.executable
        
        # Pass all parameters to the game
        subprocess.Popen([
            python_executable, 
            main_py_path, 
            mode, 
            p1_name, 
            p2_name if mode == "two_player" else "", 
            sound, 
            music
        ])
    
    def show_error(self, message):
        error_window = ctk.CTkToplevel(self.root)
        error_window.title("Error")
        error_window.geometry("350x150")
        error_window.resizable(False, False)
        
        error_label = ctk.CTkLabel(
            error_window,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        error_label.pack(pady=(30, 20))
        
        ok_button = ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy,
            width=100
        )
        ok_button.pack(pady=10)
        
        # Make the error window modal
        error_window.transient(self.root)
        error_window.grab_set()
        self.root.wait_window(error_window)

def run_menu():
    app = MainMenu()
    app.root.mainloop()

if __name__ == "__main__":
    run_menu()