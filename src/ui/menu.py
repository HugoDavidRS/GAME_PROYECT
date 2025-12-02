import customtkinter as ctk
import subprocess
import sys
import os
from PIL import Image, ImageTk
from src.services.dbhelper import DatabaseService
import pygame
import socket
from src.constants import MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT

class MainMenu:
    def __init__(self):
        # Set theme and appearance - Dark theme like slither.io
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")  # Usar el tema blue por defecto

        self.exit_reason = "PLAY"
        
        # Initialize pygame for music
        pygame.init()
        pygame.mixer.init()
        self.music_playing = False
        self.menu_music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "Sound", "menu_bgm.mp3")
        
        # Create root window - Tamaño más manejable
        self.root = ctk.CTk()
        self.root.title("Slither.io Clone - 5 Jugadores")
        self.root.geometry("1000x700")  # Ventana más pequeña para forzar scroll
        self.root.resizable(True, True)  # Permitir redimensionamiento
        
        # Set window background color
        self.root.configure(fg_color="#1a1a1a")
        
        # Crear frame principal CON SCROLLBAR
        self.main_scrollable_frame = ctk.CTkScrollableFrame(
            self.root,
            fg_color="#1a1a1a",
            scrollbar_button_color="#4CAF50",
            scrollbar_button_hover_color="#45a049",
            border_width=0
        )
        self.main_scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize variables
        self.game_mode = ctk.StringVar(value="single_player")
        self.player1_name = ctk.StringVar(value="Player_1")
        self.player2_name = ctk.StringVar(value="Player_2")
        self.sound_effects = ctk.BooleanVar(value=True)
        self.music = ctk.BooleanVar(value=True)
        
        # Nuevas variables para multijugador
        self.multiplayer_mode = ctk.StringVar(value="host")
        self.server_ip = ctk.StringVar(value="localhost")
        self.server_port = ctk.StringVar(value="5555")
        
        # Initialize database service
        self.db_service = DatabaseService()
        
        # Create UI elements - Pasar al frame scrollable
        self.create_welcome_header()
        self.create_game_mode_section()
        self.create_multiplayer_section()
        self.create_player_name_section()
        self.create_sound_controls()
        self.create_leaderboard()
        self.create_buttons()
        
        # Update player name fields based on initial game mode
        self.update_player_fields()
        
        # Load leaderboard data from database
        self.load_leaderboard_data()
        
        # Start playing music when menu loads
        self.start_menu_music()
        
        # Set up a protocol for when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)
        
    def create_welcome_header(self):
        # Main header with solid colors
        self.header_frame = ctk.CTkFrame(
            self.main_scrollable_frame,  # Cambiado: usar frame scrollable
            corner_radius=15,
            fg_color="#2a2a2a",
            border_width=2,
            border_color="#4CAF50"
        )
        self.header_frame.pack(fill="x", padx=30, pady=(15, 10))
        
        # Title with slither.io style
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="#2a2a2a")
        title_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Main title
        welcome_label = ctk.CTkLabel(
            title_frame, 
            text="SLITHER.IO CLONE",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="#4CAF50"
        )
        welcome_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="¡Domina la arena con hasta 5 jugadores!",
            font=ctk.CTkFont(family="Arial", size=16),
            text_color="#81C784"
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Decorative snake animation placeholder
        snake_decoration = ctk.CTkLabel(
            title_frame,
            text="🐍" * 15,
            font=ctk.CTkFont(size=20),
            text_color="#4CAF50"
        )
        snake_decoration.pack(pady=5)
    
    def create_game_mode_section(self):
        # Game mode selection with modern cards
        mode_frame = ctk.CTkFrame(
            self.main_scrollable_frame,  # Cambiado: usar frame scrollable
            corner_radius=15,
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#333333"
        )
        mode_frame.pack(fill="x", padx=30, pady=10)
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="🎮 MODO DE JUEGO",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="#4CAF50"
        )
        mode_label.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Radio buttons container
        radio_container = ctk.CTkFrame(mode_frame, fg_color="#2a2a2a")
        radio_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Single Player Card
        single_card = ctk.CTkFrame(
            radio_container, 
            corner_radius=10,
            fg_color="#333333",
            border_width=2,
            border_color="#4CAF50" if self.game_mode.get() == "single_player" else "#444444"
        )
        single_card.pack(fill="x", pady=8)
        
        single_radio = ctk.CTkRadioButton(
            single_card,
            text="🎯 UN JUGADOR",
            variable=self.game_mode,
            value="single_player",
            command=self.on_game_mode_changed,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white"
        )
        single_radio.pack(anchor="w", padx=15, pady=12)
        
        # Two Player Card
        two_player_card = ctk.CTkFrame(
            radio_container, 
            corner_radius=10,
            fg_color="#333333",
            border_width=2,
            border_color="#4CAF50" if self.game_mode.get() == "two_player" else "#444444"
        )
        two_player_card.pack(fill="x", pady=8)
        
        multi_radio = ctk.CTkRadioButton(
            two_player_card,
            text="👥 DOS JUGADORES (Local)",
            variable=self.game_mode,
            value="two_player",
            command=self.on_game_mode_changed,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white"
        )
        multi_radio.pack(anchor="w", padx=15, pady=12)
        
        # Multiplayer Card
        multiplayer_card = ctk.CTkFrame(
            radio_container, 
            corner_radius=10,
            fg_color="#333333",
            border_width=2,
            border_color="#4CAF50" if self.game_mode.get() == MODE_MULTIPLAYER_HOST else "#444444"
        )
        multiplayer_card.pack(fill="x", pady=8)
        
        multiplayer_radio = ctk.CTkRadioButton(
            multiplayer_card,
            text="🌐 MULTIJUGADOR (2-5 jugadores)",
            variable=self.game_mode,
            value=MODE_MULTIPLAYER_HOST,
            command=self.on_game_mode_changed,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white"
        )
        multiplayer_radio.pack(anchor="w", padx=15, pady=12)
    
    def create_multiplayer_section(self):
        """Crear sección de configuración multijugador con diseño moderno"""
        self.multiplayer_frame = ctk.CTkFrame(
            self.main_scrollable_frame,  # Cambiado: usar frame scrollable
            corner_radius=15,
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#333333"
        )
        
        multiplayer_label = ctk.CTkLabel(
            self.multiplayer_frame,
            text="🌐 CONFIGURACIÓN MULTIJUGADOR",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#4CAF50"
        )
        multiplayer_label.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Radio buttons container
        mp_radio_container = ctk.CTkFrame(self.multiplayer_frame, fg_color="#2a2a2a")
        mp_radio_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Host Card
        host_card = ctk.CTkFrame(
            mp_radio_container,
            corner_radius=10,
            fg_color="#333333",
            border_width=2,
            border_color="#4CAF50" if self.multiplayer_mode.get() == "host" else "#444444"
        )
        host_card.pack(fill="x", pady=5)
        
        host_radio = ctk.CTkRadioButton(
            host_card,
            text="🖥️ CREAR SERVIDOR (Host)",
            variable=self.multiplayer_mode,
            value="host",
            command=self.on_multiplayer_mode_changed,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4CAF50",
            text_color="white"
        )
        host_radio.pack(anchor="w", padx=15, pady=10)
        
        # Client Card
        client_card = ctk.CTkFrame(
            mp_radio_container,
            corner_radius=10,
            fg_color="#333333",
            border_width=2,
            border_color="#4CAF50" if self.multiplayer_mode.get() == "client" else "#444444"
        )
        client_card.pack(fill="x", pady=5)
        
        client_radio = ctk.CTkRadioButton(
            client_card,
            text="🔗 UNIRSE A SERVIDOR",
            variable=self.multiplayer_mode,
            value="client",
            command=self.on_multiplayer_mode_changed,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4CAF50",
            text_color="white"
        )
        client_radio.pack(anchor="w", padx=15, pady=10)
        
        # Server configuration
        self.server_config_frame = ctk.CTkFrame(self.multiplayer_frame, fg_color="#2a2a2a")
        self.server_config_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        # IP configuration
        ip_card = ctk.CTkFrame(self.server_config_frame, fg_color="#333333", corner_radius=8)
        ip_card.pack(fill="x", pady=5)
        
        ip_label = ctk.CTkLabel(
            ip_card, 
            text="📍 IP del Servidor:", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#81C784"
        )
        ip_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.ip_entry = ctk.CTkEntry(
            ip_card, 
            textvariable=self.server_ip, 
            width=200,
            placeholder_text="localhost",
            fg_color="#1a1a1a",
            border_color="#4CAF50",
            text_color="white"
        )
        self.ip_entry.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Port configuration
        port_card = ctk.CTkFrame(self.server_config_frame, fg_color="#333333", corner_radius=8)
        port_card.pack(fill="x", pady=5)
        
        port_label = ctk.CTkLabel(
            port_card, 
            text="🔢 Puerto:", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#81C784"
        )
        port_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.port_entry = ctk.CTkEntry(
            port_card, 
            textvariable=self.server_port, 
            width=120,
            placeholder_text="5555",
            fg_color="#1a1a1a",
            border_color="#4CAF50",
            text_color="white"
        )
        self.port_entry.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Network info
        info_card = ctk.CTkFrame(self.multiplayer_frame, fg_color="#333333", corner_radius=8)
        info_card.pack(fill="x", padx=20, pady=(0, 20))
        
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.ip_info_text = f"🌐 Tu IP local: {local_ip} (Comparte esta IP con tus amigos)"
        except:
            self.ip_info_text = "🌐 Tu IP local: No disponible"
            
        self.ip_info_label = ctk.CTkLabel(
            info_card, 
            text=self.ip_info_text, 
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50",
            wraplength=600
        )
        self.ip_info_label.pack(anchor="w", padx=15, pady=10)
        
        # Instructions
        self.instructions_label = ctk.CTkLabel(
            info_card,
            text="💡 Selecciona 'Crear Servidor' para ser host, o 'Unirse a Servidor' para conectar",
            font=ctk.CTkFont(size=11),
            text_color="#81C784",
            wraplength=600
        )
        self.instructions_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Controls info
        controls_info = ctk.CTkLabel(
            info_card,
            text="🎮 Controles: P1(WASD), P2(Flechas), P3(IJKL), P4(Numpad), P5(TFGH)",
            font=ctk.CTkFont(size=10),
            text_color="#BDBDBD",
            wraplength=600
        )
        controls_info.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Actualizar visibilidad inicial
        self.on_multiplayer_mode_changed()
    
    def on_multiplayer_mode_changed(self):
        """Manejar cambio de modo multijugador"""
        if self.multiplayer_mode.get() == "client":
            # Modo Cliente - Mostrar campos y actualizar instrucciones
            self.ip_entry.configure(state="normal", fg_color="#1a1a1a")
            self.port_entry.configure(state="normal", fg_color="#1a1a1a")
            self.instructions_label.configure(
                text="💡 Ingresa la IP del host y haz click en JUGAR para unirte"
            )
            self.ip_info_label.configure(text_color="#4CAF50")
        else:
            # Modo Host - Campos visibles pero IP deshabilitada
            self.ip_entry.configure(state="disabled", fg_color="#2a2a2a")
            self.port_entry.configure(state="normal", fg_color="#1a1a1a")
            self.instructions_label.configure(
                text="💡 Comparte tu IP local con amigos y haz click en JUGAR (mínimo 2 jugadores)"
            )
            self.ip_info_label.configure(text_color="#4CAF50")
    
    def on_game_mode_changed(self):
        """Handle game mode change"""
        self.update_player_fields()
        self.update_leaderboard_ui()

    def create_player_name_section(self):
        """Sección de nombres con diseño moderno"""
        self.player_frame = ctk.CTkFrame(
            self.main_scrollable_frame,  # Cambiado: usar frame scrollable
            corner_radius=15,
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#333333"
        )
        self.player_frame.pack(fill="x", padx=30, pady=10)
        
        name_label = ctk.CTkLabel(
            self.player_frame,
            text="👤 NOMBRES DE JUGADORES",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#4CAF50"
        )
        name_label.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Player 1 name input with card design
        p1_card = ctk.CTkFrame(self.player_frame, fg_color="#333333", corner_radius=8)
        p1_card.pack(fill="x", padx=20, pady=8)
        
        p1_label = ctk.CTkLabel(
            p1_card, 
            text="🎯 Tu nombre:", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#81C784"
        )
        p1_label.pack(anchor="w", padx=15, pady=(12, 5))
        
        p1_entry = ctk.CTkEntry(
            p1_card, 
            textvariable=self.player1_name, 
            width=250,
            fg_color="#1a1a1a",
            border_color="#4CAF50",
            text_color="white",
            placeholder_text="Ingresa tu nombre..."
        )
        p1_entry.pack(anchor="w", padx=15, pady=(0, 12))
        
        # Información sobre nombres en multijugador
        self.name_info_label = ctk.CTkLabel(
            self.player_frame,
            text="💡 En multijugador, cada jugador pone su propio nombre al conectarse",
            font=ctk.CTkFont(size=12),
            text_color="#81C784",
            wraplength=600
        )
        self.name_info_label.pack(anchor="w", padx=20, pady=(5, 15))
        
        # Player 2 name input (solo para two_player local)
        self.p2_card = ctk.CTkFrame(self.player_frame, fg_color="#333333", corner_radius=8)
        
        p2_label = ctk.CTkLabel(
            self.p2_card, 
            text="👥 Jugador 2:", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#81C784"
        )
        p2_label.pack(anchor="w", padx=15, pady=(12, 5))
        
        p2_entry = ctk.CTkEntry(
            self.p2_card, 
            textvariable=self.player2_name, 
            width=250,
            fg_color="#1a1a1a",
            border_color="#4CAF50",
            text_color="white",
            placeholder_text="Nombre del segundo jugador..."
        )
        p2_entry.pack(anchor="w", padx=15, pady=(0, 12))
    
    def create_sound_controls(self):
        # Sound controls section with modern design
        sound_frame = ctk.CTkFrame(
            self.main_scrollable_frame,  # Cambiado: usar frame scrollable
            corner_radius=15,
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#333333"
        )
        sound_frame.pack(fill="x", padx=30, pady=10)
        
        sound_label = ctk.CTkLabel(
            sound_frame,
            text="🔊 CONFIGURACIÓN DE SONIDO",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#4CAF50"
        )
        sound_label.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Sound effects switch with card
        effects_card = ctk.CTkFrame(sound_frame, fg_color="#333333", corner_radius=8)
        effects_card.pack(fill="x", padx=20, pady=8)
        
        effects_switch = ctk.CTkSwitch(
            effects_card,
            text="🎵 Efectos de Sonido",
            variable=self.sound_effects,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4CAF50",
            progress_color="#4CAF50",
            button_color="#1a1a1a",
            button_hover_color="#333333",
            text_color="white"
        )
        effects_switch.pack(anchor="w", padx=15, pady=12)
        
        # Music switch with card
        music_card = ctk.CTkFrame(sound_frame, fg_color="#333333", corner_radius=8)
        music_card.pack(fill="x", padx=20, pady=(8, 20))
        
        music_switch = ctk.CTkSwitch(
            music_card,
            text="🎶 Música de Fondo",
            variable=self.music,
            command=self.toggle_music_from_switch,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4CAF50",
            progress_color="#4CAF50",
            button_color="#1a1a1a",
            button_hover_color="#333333",
            text_color="white"
        )
        music_switch.pack(anchor="w", padx=15, pady=12)
    
    def create_leaderboard(self):
        # Leaderboard section with modern design
        self.lb_frame = ctk.CTkFrame(
            self.main_scrollable_frame,  # Cambiado: usar frame scrollable
            corner_radius=15,
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#333333"
        )
        self.lb_frame.pack(fill="x", padx=30, pady=10)
        
        self.lb_label = ctk.CTkLabel(
            self.lb_frame,
            text="🏆 TABLA DE CLASIFICACIÓN",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#4CAF50"
        )
        self.lb_label.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Leaderboard will be populated by load_leaderboard_data method
        self.lb_frame.pack(pady=(10, 15))
    
    def create_buttons(self):
        # Action buttons with modern design
        button_frame = ctk.CTkFrame(self.main_scrollable_frame, fg_color="#1a1a1a")  # Cambiado
        button_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        # Exit button
        exit_button = ctk.CTkButton(
            button_frame,
            text="🚪 SALIR",
            command=self.exit_program,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            border_width=2,
            border_color="#C0392B"
        )
        exit_button.pack(side="left", padx=10)

        # Mute Button
        self.mute_button = ctk.CTkButton(
            button_frame,
            text="🔇 SILENCIAR",
            command=self.toggle_menu_music,
            fg_color="#F39C12",
            hover_color="#E67E22",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            border_width=2,
            border_color="#E67E22"
        )
        self.mute_button.pack(side="left", padx=10)
        
        # Play button - Main call to action
        play_button = ctk.CTkButton(
            button_frame,
            text="🎮 ¡JUGAR!",
            command=self.start_game,
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=180,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
            border_width=2,
            border_color="#45a049"
        )
        play_button.pack(side="right", padx=10)
    
    def update_player_fields(self):
        """Mostrar/ocultar campos de jugador según modo de juego"""
        if self.game_mode.get() == "single_player":
            self.p2_card.pack_forget()
            if hasattr(self, 'multiplayer_frame') and self.multiplayer_frame.winfo_ismapped():
                self.multiplayer_frame.pack_forget()
            self.name_info_label.configure(
                text="💡 Modo un jugador - Controla la serpiente con WASD"
            )
        elif self.game_mode.get() == "two_player":
            self.p2_card.pack(fill="x", padx=20, pady=8)
            if hasattr(self, 'multiplayer_frame') and self.multiplayer_frame.winfo_ismapped():
                self.multiplayer_frame.pack_forget()
            self.name_info_label.configure(
                text="💡 Modo local - P1 (WASD), P2 (Flechas)"
            )
        else:  # Multijugador
            self.p2_card.pack_forget()
            self.multiplayer_frame.pack(fill="x", padx=30, pady=10)
            self.name_info_label.configure(
                text="💡 En multijugador, cada jugador pone su propio nombre al conectarse"
            )
    
    def load_leaderboard_data(self):
        """Load leaderboard data from database"""
        # Fetch top 5 players (default is single player mode)
        self.leaderboard_data = self.db_service.fetch_leaderboard()
        
        # Update UI with the data
        self.update_leaderboard_ui()
    
    def update_leaderboard_ui(self):
        """Update leaderboard UI elements with current data"""
        # Clear existing elements (except the title label)
        for widget in self.lb_frame.winfo_children():
            if widget != self.lb_label:  # Keep the title
                widget.destroy()
        
        mode = "multi" if self.game_mode.get() in [MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT] else "single"
        self.leaderboard_data = self.db_service.fetch_leaderboard(mode)
        
        # Create leaderboard container
        lb_container = ctk.CTkFrame(self.lb_frame, fg_color="#333333", corner_radius=10)
        lb_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Header row with modern styling
        header_frame = ctk.CTkFrame(lb_container, fg_color="#333333")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
    
        rank_header = ctk.CTkLabel(
            header_frame, 
            text="#", 
            width=50, 
            font=ctk.CTkFont(weight="bold", size=13),
            text_color="#4CAF50"
        )
        rank_header.pack(side="left", padx=5)
    
        name_header = ctk.CTkLabel(
            header_frame, 
            text="JUGADOR", 
            width=150, 
            font=ctk.CTkFont(weight="bold", size=13),
            text_color="#4CAF50"
        )
        name_header.pack(side="left", padx=5)
    
        # Add Wins column for multiplayer mode
        if mode == "multi":
            wins_header = ctk.CTkLabel(
                header_frame, 
                text="VICTORIAS", 
                width=80, 
    font=ctk.CTkFont(weight="bold", size=13),
                text_color="#4CAF50"
            )
            wins_header.pack(side="left", padx=5)
    
        score_header = ctk.CTkLabel(
            header_frame, 
            text="PUNTUACIÓN", 
            width=80, 
            font=ctk.CTkFont(weight="bold", size=13),
            text_color="#4CAF50"
        )
        score_header.pack(side="left", padx=5)
        
        # Fill with leaderboard data
        for i, entry in enumerate(self.leaderboard_data, 1):
            entry_frame = ctk.CTkFrame(lb_container, fg_color="#333333")
            entry_frame.pack(fill="x", padx=15, pady=8)
            
            # Different background for top 3
            if i <= 3:
                medal = ["🥇", "🥈", "🥉"][i-1]
                rank_text = f"{medal}"
            else:
                rank_text = f"{i}"
        
            rank_label = ctk.CTkLabel(
                entry_frame, 
                text=rank_text, 
                width=50,
                font=ctk.CTkFont(weight="bold" if i <= 3 else "normal")
            )
            rank_label.pack(side="left", padx=5)
        
            name_label = ctk.CTkLabel(
                entry_frame, 
                text=entry[0], 
                width=150, 
                anchor="w",
                font=ctk.CTkFont(weight="bold" if i <= 3 else "normal"),
                text_color="#4CAF50" if i == 1 else "white"
            )
            name_label.pack(side="left", padx=5)
        
            if mode == "multi":
                # Format: (name, score, wins)
                wins_label = ctk.CTkLabel(
                    entry_frame, 
                    text=str(entry[2]), 
                    width=80,
                    font=ctk.CTkFont(weight="bold" if i <= 3 else "normal")
                )
                wins_label.pack(side="left", padx=5)
                score_label = ctk.CTkLabel(
                    entry_frame, 
                    text=str(entry[1]), 
                    width=80,
                    font=ctk.CTkFont(weight="bold" if i <= 3 else "normal")
                )
            else:
                # Format: (name, score)
                score_label = ctk.CTkLabel(
                    entry_frame, 
                    text=str(entry[1]), 
                    width=80,
                    font=ctk.CTkFont(weight="bold" if i <= 3 else "normal")
                )
        
            score_label.pack(side="left", padx=5)
            
            # Add separator for all but last entry
            if i < len(self.leaderboard_data):
                separator = ctk.CTkFrame(lb_container, fg_color="#444444", height=1)
                separator.pack(fill="x", padx=20, pady=2)
    
    def exit_program(self):
        try:
            # Stop music before exiting
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            if pygame.get_init():
                pygame.quit()
        except Exception:
            pass
        
        self.exit_reason = "QUIT"
        self.root.destroy()
        sys.exit(0)
    
    def start_menu_music(self):
        """Start playing menu background music"""
        try:
            pygame.mixer.music.load(self.menu_music_path)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            self.music_playing = True
            self.mute_button.configure(text="🔇 SILENCIAR")
        except Exception as e:
            print(f"Error playing music: {e}")
    
    def toggle_menu_music(self):
        """Toggle menu music on/off"""
        if self.music_playing:
            pygame.mixer.music.pause()
            self.music_playing = False
            self.mute_button.configure(text="🔊 SONIDO")
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
            self.mute_button.configure(text="🔇 SILENCIAR")
    
    def toggle_music_from_switch(self):
        """Handle music toggle from the switch in sound settings"""
        if self.music.get():  # If music should be on
            if not self.music_playing:
                pygame.mixer.music.unpause()
                self.music_playing = True
                self.mute_button.configure(text="🔇 SILENCIAR")
        else:  # If music should be off
            if self.music_playing:
                pygame.mixer.music.pause()
                self.music_playing = False
                self.mute_button.configure(text="🔊 SONIDO")
    
    def start_game(self):
        # Get player names
        p1_name = self.player1_name.get()
        p2_name = self.player2_name.get()
        
        # Check if names are provided
        if not p1_name:
            self.show_error("Por favor ingresa un nombre para el Jugador 1")
            return
            
        # Validación según modo de juego
        if self.game_mode.get() == "two_player" and not p2_name:
            self.show_error("Por favor ingresa un nombre para el Jugador 2")
            return
    
        # Validación para multijugador
        if self.game_mode.get() in [MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT]:
            # En multijugador, solo necesitamos el nombre del jugador actual
            if not p1_name:
                self.show_error("Por favor ingresa tu nombre")
                return
            
            # Validar configuración de red para cliente
            if self.multiplayer_mode.get() == "client":
                if not self.server_ip.get().strip():
                    self.show_error("Por favor ingresa la dirección IP del servidor")
                    return
                try:
                    port = int(self.server_port.get())
                    if port < 1 or port > 65535:
                        raise ValueError
                except ValueError:
                    self.show_error("Por favor ingresa un número de puerto válido (1-65535)")
                    return
    
        # Validation checks
        if not p1_name or " " in p1_name:
            self.show_error("El nombre del jugador no puede estar vacío o contener espacios.")
            return
            
        if self.game_mode.get() == "two_player":
            if not p2_name or " " in p2_name:
                self.show_error("El nombre del Jugador 2 no puede estar vacío o contener espacios.")
                return
    
        # Check if username exists
        existing_users = []
        if self.game_mode.get() == "single_player":
            existing_users = self.db_service.check_username(p1_name)
        elif self.game_mode.get() == "two_player":
            existing_users = self.db_service.check_username(p1_name, p2_name)
        else:  # Multijugador - solo verificar el nombre del jugador actual
            existing_users = self.db_service.check_username(p1_name)
        
        if existing_users:
            # Show confirmation dialog for returning players
            self.confirm_returning_players(existing_users)
        else:
            # Register new players
            if self.game_mode.get() == "single_player":
                self.db_service.register_new_player(p1_name)
            elif self.game_mode.get() == "two_player":
                self.db_service.register_new_player(p1_name)
                self.db_service.register_new_player(p2_name)
            else:  # Multijugador - solo registrar el nombre del jugador actual
                self.db_service.register_new_player(p1_name)
            self.launch_game()
    
    def confirm_returning_players(self, existing_users):
        """Show dialog to confirm if the user is the same person as a returning player"""
        # Create confirmation dialog with modern design
        confirm_window = ctk.CTkToplevel(self.root)
        confirm_window.title("Jugador Existente")
        confirm_window.geometry("450x220")
        confirm_window.resizable(False, False)
        confirm_window.configure(fg_color="#2a2a2a")
        
        # Make window appear centered
        confirm_window.transient(self.root)
        confirm_window.grab_set()
        
        # Content frame
        content_frame = ctk.CTkFrame(confirm_window, fg_color="#333333", corner_radius=12)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        if self.game_mode.get() in [MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT]:
            message = f"🎮 El jugador '{existing_users[0]}' ya existe.\n\n¿Eres tú? Haz click en CONTINUAR. Si no, cambia tu nombre."
        else:
            message = f"🎮 El{'s' if len(existing_users) > 1 else ''} jugador{'es' if len(existing_users) > 1 else ''} {', '.join(existing_users)} ya existe{'n' if len(existing_users) > 1 else ''}.\n\n¿Eres{'s' if len(existing_users) > 1 else ''} tú? Haz click en CONTINUAR. Si no, cambia tu nombre."
        
        confirm_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=380,
            text_color="white"
        )
        confirm_label.pack(pady=(30, 25))
        
        button_frame = ctk.CTkFrame(content_frame, fg_color="#333333")
        button_frame.pack(pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ CANCELAR",
            command=confirm_window.destroy,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=120,
            height=35,
            font=ctk.CTkFont(weight="bold")
        )
        cancel_button.pack(side="left", padx=10)
        
        continue_button = ctk.CTkButton(
            button_frame,
            text="✅ CONTINUAR",
            command=lambda: [confirm_window.destroy(), self.launch_game()],
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=120,
            height=35,
            font=ctk.CTkFont(weight="bold")
        )
        continue_button.pack(side="left", padx=10)
        
        self.root.wait_window(confirm_window)
    
    def launch_game(self):
        """Launch the game process"""
        # Get game parameters
        mode = self.game_mode.get()
        p1_name = self.player1_name.get()
        p2_name = self.player2_name.get()
        sound = "on" if self.sound_effects.get() else "off"
        music = "on" if self.music.get() else "off"
        
        # Determinar modo multijugador específico
        if mode in [MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT]:
            is_host = (self.multiplayer_mode.get() == "host")
            actual_mode = MODE_MULTIPLAYER_HOST if is_host else MODE_MULTIPLAYER_CLIENT
            host_ip = "localhost" if is_host else self.server_ip.get()
            port = int(self.server_port.get())
            
            # En multijugador, usar p1_name como nombre del jugador actual
            # y p2_name como placeholder (no se usa realmente)
            player1_name = p1_name
            player2_name = "Player_2"  # Placeholder
        else:
            actual_mode = mode
            is_host = True
            host_ip = "localhost"
            port = 5555
            player1_name = p1_name
            player2_name = p2_name if mode == "two_player" else ""
        
        # Stop music before closing
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            if pygame.get_init():
                pygame.quit()
        except Exception:
            pass
        
        # Close the menu
        self.root.destroy()
        
        # Start a new process for the game
        main_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'main.py')
        python_executable = sys.executable
        
        # Construir comando
        command = [
            python_executable, 
            main_py_path, 
            actual_mode, 
            player1_name, 
            player2_name, 
            sound, 
            music,
            "--host", host_ip,
            "--port", str(port),
            "--is-host", "1" if is_host else "0"
        ]
        
        print(f"🚀 Iniciando juego: {actual_mode}")
        print(f"🎮 Jugador: {player1_name}")
        print(f"🔗 Configuración red: {host_ip}:{port} ({'Host' if is_host else 'Client'})")
        
        # Launch the game in a new process
        subprocess.Popen(command)
        
        # Exit this process completely
        sys.exit(0)
    
    def show_error(self, message):
        error_window = ctk.CTkToplevel(self.root)
        error_window.title("Error")
        error_window.geometry("400x180")
        error_window.resizable(False, False)
        error_window.configure(fg_color="#2a2a2a")
        
        # Make window appear centered
        error_window.transient(self.root)
        error_window.grab_set()
        
        # Content frame
        content_frame = ctk.CTkFrame(error_window, fg_color="#333333", corner_radius=12)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        error_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=350,
            text_color="white"
        )
        error_label.pack(pady=(25, 20))
        
        ok_button = ctk.CTkButton(
            content_frame,
            text="✅ ENTENDIDO",
            command=error_window.destroy,
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049",
            font=ctk.CTkFont(weight="bold")
        )
        ok_button.pack(pady=10)
        
        self.root.wait_window(error_window)

def run_menu():
    app = MainMenu()
    app.root.mainloop()
    return "QUIT"

if __name__ == "__main__":
    run_menu()