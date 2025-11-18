import customtkinter as ctk
import subprocess
import sys
import os
import socket
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pygame
from src.services.dbhelper import DatabaseService
from src.constants import MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT

class MainMenu:
    def __init__(self):
        # =============================================================================
        # CONFIGURACIÓN INICIAL PREMIUM
        # =============================================================================
        self._setup_appearance()
        self._initialize_variables()
        self._setup_window()
        self._initialize_services()
        self._create_main_interface()
        self._finalize_setup()

    def _setup_appearance(self):
        """Configurar apariencia profesional de la aplicación"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Paleta de colores profesional
        self.COLORS = {
            'primary': '#2E8B57',
            'primary_dark': '#1F6B4D',
            'primary_light': '#3CA374',
            'secondary': '#3498DB',
            'accent': '#E74C3C',
            'success': '#27AE60',
            'warning': '#F39C12',
            'danger': '#E74C3C',
            'dark_bg': '#1A1A2E',
            'dark_card': '#16213E',
            'dark_text': '#ECF0F1',
            'light_bg': '#F8F9FA',
            'light_card': '#FFFFFF',
            'light_text': '#2C3E50'
        }

    def _initialize_variables(self):
        """Inicializar todas las variables del sistema"""
        # Variables de estado
        self.exit_reason = "PLAY"
        self.music_playing = False
        self.current_theme = "dark"
        self.connection_status = "disconnected"
        self.server_status = "inactive"
        
        # Variables de juego
        self.game_mode = ctk.StringVar(value="single_player")
        self.player1_name = ctk.StringVar(value="SnakeMaster")
        self.player2_name = ctk.StringVar(value="Player2")
        self.sound_effects = ctk.BooleanVar(value=True)
        self.music = ctk.BooleanVar(value=True)
        self.game_difficulty = ctk.StringVar(value="medium")
        
        # Variables de red
        self.multiplayer_mode = ctk.StringVar(value="host")
        self.server_ip = ctk.StringVar(value="localhost")
        self.server_port = ctk.StringVar(value="5555")
        self.auto_discover = ctk.BooleanVar(value=False)
        
        # Estadísticas
        self.total_games_played = 0
        self.best_score = 0
        self.player_level = 1

    def _setup_window(self):
        """Configurar ventana principal con diseño premium"""
        self.root = ctk.CTk()
        self.root.title("🐍 Snake Arena Pro - Ultimate Multiplayer Experience")
        self.root.geometry("900x1000")
        self.root.resizable(True, True)
        self.root.minsize(850, 950)
        
        # Configurar protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._graceful_exit)

    def _initialize_services(self):
        """Inicializar servicios externos"""
        # Servicio de base de datos
        self.db_service = DatabaseService()
        
        # Sistema de audio
        self._initialize_audio_system()
        
        # Sistema de red
        self._initialize_network_system()

    def _initialize_audio_system(self):
        """Inicializar sistema de audio profesional"""
        try:
            pygame.init()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.menu_music_path = self._get_music_path()
            self.sound_effects_enabled = True
        except Exception as e:
            print(f"Audio system warning: {e}")
            self.sound_effects_enabled = False

    def _get_music_path(self):
        """Obtener ruta de la música del menú"""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "assets", "Sound", "menu_bgm.mp3"),
            os.path.join(os.path.dirname(__file__), "..", "..", "assets", "Sound", "menu_bgm.wav"),
            "menu_music.mp3"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _initialize_network_system(self):
        """Inicializar sistema de detección de red"""
        self.local_ip = self._get_local_ip()
        self.network_status = "unknown"
        self.available_servers = []

    def _get_local_ip(self):
        """Obtener IP local del sistema"""
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "127.0.0.1"

    def _create_main_interface(self):
        """Crear interfaz principal completa"""
        self._create_background()
        self._create_main_container()
        self._create_navigation_bar()
        self._create_content_area()
        self._create_status_bar()

    def _create_background(self):
        """Crear fondo profesional con gradiente"""
        try:
            self.background_image = self._create_gradient_background()
        except Exception as e:
            print(f"Background creation warning: {e}")

    def _create_gradient_background(self):
        """Crear fondo con gradiente profesional"""
        width, height = 900, 1000
        image = Image.new('RGB', (width, height), color=self.COLORS['dark_bg'])
        draw = ImageDraw.Draw(image)
        
        # Gradiente complejo
        for y in range(height):
            progress = y / height
            r = int(26 + progress * 20)
            g = int(26 + progress * 40)
            b = int(46 + progress * 30)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return ImageTk.PhotoImage(image)

    def _create_main_container(self):
        """Crear contenedor principal"""
        self.main_container = ctk.CTkFrame(
            self.root, 
            fg_color=self.COLORS['dark_bg'],
            corner_radius=0
        )
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

    def _create_navigation_bar(self):
        """Crear barra de navegación superior"""
        self.nav_bar = ctk.CTkFrame(
            self.main_container,
            fg_color=self.COLORS['dark_card'],
            height=60,
            corner_radius=0
        )
        self.nav_bar.pack(fill="x", padx=0, pady=0)
        self.nav_bar.pack_propagate(False)
        
        self._create_nav_content()

    def _create_nav_content(self):
        """Crear contenido de la barra de navegación"""
        # Logo y título
        logo_frame = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        logo_frame.pack(side="left", padx=20, pady=10)
        
        title_label = ctk.CTkLabel(
            logo_frame,
            text="🐍 SNAKE ARENA PRO",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color=self.COLORS['primary_light']
        )
        title_label.pack(side="left")
        
        # Navegación
        nav_buttons_frame = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        nav_buttons_frame.pack(side="right", padx=20, pady=10)
        
        nav_buttons = [
            ("🎮 Play", self._show_play_section),
            ("📊 Stats", self._show_stats_section),
            ("⚙️ Settings", self._show_settings_section),
            ("❓ Help", self._show_help_section)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                nav_buttons_frame,
                text=text,
                command=command,
                fg_color="transparent",
                hover_color=self.COLORS['primary_dark'],
                font=ctk.CTkFont(size=12, weight="bold"),
                width=80
            )
            btn.pack(side="left", padx=5)

    def _create_content_area(self):
        """Crear área de contenido principal"""
        self.content_area = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        self.content_area.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Inicializar con sección de juego
        self._create_play_section()

    def _create_play_section(self):
        """Crear sección principal de juego"""
        self.play_section = ctk.CTkFrame(
            self.content_area,
            fg_color=self.COLORS['dark_card'],
            corner_radius=15
        )
        self.play_section.pack(fill="both", expand=True, padx=0, pady=0)
        
        self._create_game_mode_section()
        self._create_player_section()
        self._create_multiplayer_section()
        self._create_quick_settings()
        self._create_action_buttons()

    def _create_game_mode_section(self):
        """Crear sección de selección de modo de juego"""
        mode_section = ctk.CTkFrame(
            self.play_section,
            fg_color="transparent"
        )
        mode_section.pack(fill="x", padx=25, pady=(25, 15))
        
        # Título de sección
        section_title = ctk.CTkLabel(
            mode_section,
            text="🎯 SELECT GAME MODE",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color=self.COLORS['primary_light']
        )
        section_title.pack(anchor="w", pady=(0, 15))
        
        # Opciones de modo de juego
        mode_options_frame = ctk.CTkFrame(mode_section, fg_color="transparent")
        mode_options_frame.pack(fill="x", padx=10)
        
        modes = [
            {
                "icon": "👑",
                "title": "SOLO CHALLENGE", 
                "description": "Test your skills against AI opponents",
                "value": "single_player",
                "color": self.COLORS['secondary']
            },
            {
                "icon": "👥", 
                "title": "LOCAL DUEL",
                "description": "2 players on the same device",
                "value": "two_player", 
                "color": self.COLORS['warning']
            },
            {
                "icon": "🌐",
                "title": "ONLINE BATTLE", 
                "description": "2-5 players online multiplayer",
                "value": MODE_MULTIPLAYER_HOST,
                "color": self.COLORS['success']
            }
        ]
        
        for mode in modes:
            self._create_mode_card(mode_options_frame, mode)

    def _create_mode_card(self, parent, mode_data):
        """Crear tarjeta de modo de juego"""
        card = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            border_width=2,
            border_color=mode_data["color"],
            corner_radius=12
        )
        card.pack(fill="x", pady=8)
        
        card_content = ctk.CTkFrame(card, fg_color="transparent")
        card_content.pack(fill="x", padx=15, pady=12)
        
        # Header de la tarjeta
        header_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        header_frame.pack(fill="x")
        
        # Radio button y contenido
        radio_btn = ctk.CTkRadioButton(
            header_frame,
            text="",
            variable=self.game_mode,
            value=mode_data["value"],
            command=self._on_game_mode_changed,
            fg_color=mode_data["color"],
            hover_color=mode_data["color"],
            width=20,
            height=20
        )
        radio_btn.pack(side="left")
        
        # Contenido de la tarjeta
        content_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        content_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Título y icono
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(fill="x")
        
        icon_label = ctk.CTkLabel(
            title_frame,
            text=mode_data["icon"],
            font=ctk.CTkFont(size=18)
        )
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=mode_data["title"],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS['dark_text']
        )
        title_label.pack(side="left", padx=(8, 0))
        
        # Descripción
        desc_label = ctk.CTkLabel(
            content_frame,
            text=mode_data["description"],
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        desc_label.pack(anchor="w", pady=(5, 0))

    def _create_player_section(self):
        """Crear sección de información del jugador"""
        self.player_section = ctk.CTkFrame(
            self.play_section,
            fg_color="transparent"
        )
        self.player_section.pack(fill="x", padx=25, pady=15)
        
        # Título de sección
        section_title = ctk.CTkLabel(
            self.player_section,
            text="👤 PLAYER PROFILE",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.COLORS['primary_light']
        )
        section_title.pack(anchor="w", pady=(0, 12))
        
        # Contenido del perfil
        profile_content = ctk.CTkFrame(self.player_section, fg_color="transparent")
        profile_content.pack(fill="x", padx=10)
        
        # Campo de nombre principal
        name_frame = ctk.CTkFrame(profile_content, fg_color="transparent")
        name_frame.pack(fill="x", pady=8)
        
        name_label = ctk.CTkLabel(
            name_frame,
            text="Player Name:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120
        )
        name_label.pack(side="left")
        
        name_entry = ctk.CTkEntry(
            name_frame,
            textvariable=self.player1_name,
            placeholder_text="Enter your legendary snake name...",
            font=ctk.CTkFont(size=13),
            width=250,
            height=35
        )
        name_entry.pack(side="left", padx=(10, 0))
        
        # Información contextual
        self.name_info_label = ctk.CTkLabel(
            profile_content,
            text="This name will be displayed to other players in online matches",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        self.name_info_label.pack(anchor="w", padx=(120, 0), pady=(5, 0))

    def _create_multiplayer_section(self):
        """Crear sección de configuración multijugador"""
        self.multiplayer_section = ctk.CTkFrame(
            self.play_section,
            fg_color="transparent"
        )
        
        # Título de sección
        section_title = ctk.CTkLabel(
            self.multiplayer_section,
            text="🌐 MULTIPLAYER SETTINGS",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.COLORS['primary_light']
        )
        section_title.pack(anchor="w", padx=25, pady=(0, 15))
        
        # Contenido multijugador
        multiplayer_content = ctk.CTkFrame(
            self.multiplayer_section,
            fg_color=self.COLORS['dark_bg'],
            corner_radius=12
        )
        multiplayer_content.pack(fill="x", padx=25, pady=(0, 15))
        
        self._create_connection_options(multiplayer_content)
        self._create_server_config(multiplayer_content)
        self._create_network_info(multiplayer_content)

    def _create_connection_options(self, parent):
        """Crear opciones de conexión"""
        connection_frame = ctk.CTkFrame(parent, fg_color="transparent")
        connection_frame.pack(fill="x", padx=20, pady=20)
        
        connection_label = ctk.CTkLabel(
            connection_frame,
            text="Connection Type:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        connection_label.pack(anchor="w", pady=(0, 10))
        
        # Opciones de conexión
        options_frame = ctk.CTkFrame(connection_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=10)
        
        host_option = ctk.CTkRadioButton(
            options_frame,
            text="🎪 HOST GAME - Create server for others to join",
            variable=self.multiplayer_mode,
            value="host",
            command=self._on_multiplayer_mode_changed,
            font=ctk.CTkFont(size=13)
        )
        host_option.pack(anchor="w", pady=8)
        
        client_option = ctk.CTkRadioButton(
            options_frame,
            text="🔗 JOIN GAME - Connect to existing server", 
            variable=self.multiplayer_mode,
            value="client",
            command=self._on_multiplayer_mode_changed,
            font=ctk.CTkFont(size=13)
        )
        client_option.pack(anchor="w", pady=8)

    def _create_server_config(self, parent):
        """Crear configuración del servidor"""
        self.server_config_section = ctk.CTkFrame(parent, fg_color="transparent")
        self.server_config_section.pack(fill="x", padx=20, pady=(0, 15))
        
        # Configuración de IP
        ip_frame = ctk.CTkFrame(self.server_config_section, fg_color="transparent")
        ip_frame.pack(fill="x", pady=8)
        
        ip_label = ctk.CTkLabel(
            ip_frame,
            text="Server IP Address:",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140
        )
        ip_label.pack(side="left")
        
        self.ip_entry = ctk.CTkEntry(
            ip_frame,
            textvariable=self.server_ip,
            placeholder_text="Enter host IP address (e.g., 192.168.1.100)",
            font=ctk.CTkFont(size=12),
            width=220,
            height=32
        )
        self.ip_entry.pack(side="left", padx=(10, 0))
        
        # Configuración de puerto
        port_frame = ctk.CTkFrame(self.server_config_section, fg_color="transparent")
        port_frame.pack(fill="x", pady=8)
        
        port_label = ctk.CTkLabel(
            port_frame,
            text="Server Port:",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140
        )
        port_label.pack(side="left")
        
        self.port_entry = ctk.CTkEntry(
            port_frame,
            textvariable=self.server_port,
            placeholder_text="5555",
            font=ctk.CTkFont(size=12),
            width=120,
            height=32
        )
        self.port_entry.pack(side="left", padx=(10, 0))

    def _create_network_info(self, parent):
        """Crear información de red"""
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Información de IP local
        ip_info_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        ip_info_frame.pack(fill="x", pady=8)
        
        self.ip_info_label = ctk.CTkLabel(
            ip_info_frame,
            text=f"📍 Your Local IP: {self.local_ip}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.COLORS['success']
        )
        self.ip_info_label.pack(anchor="w")
        
        # Instrucciones
        instructions_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        instructions_frame.pack(fill="x", pady=8)
        
        self.instructions_label = ctk.CTkLabel(
            instructions_frame,
            text="Share your IP with friends to host a game, or enter a host IP to join",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        self.instructions_label.pack(anchor="w")
        
        # Controles
        controls_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=8)
        
        controls_text = "🎮 Controls: P1(WASD) • P2(Arrows) • P3(IJKL) • P4(Numpad 8456) • P5(TFGH)"
        controls_label = ctk.CTkLabel(
            controls_frame,
            text=controls_text,
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        controls_label.pack(anchor="w")

    def _create_quick_settings(self):
        """Crear configuración rápida"""
        settings_section = ctk.CTkFrame(
            self.play_section,
            fg_color="transparent"
        )
        settings_section.pack(fill="x", padx=25, pady=15)
        
        # Título de sección
        section_title = ctk.CTkLabel(
            settings_section,
            text="⚡ QUICK SETTINGS",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.COLORS['primary_light']
        )
        section_title.pack(anchor="w", pady=(0, 12))
        
        # Contenido de configuración
        settings_content = ctk.CTkFrame(settings_section, fg_color="transparent")
        settings_content.pack(fill="x", padx=10)
        
        # Audio settings
        audio_frame = ctk.CTkFrame(settings_content, fg_color="transparent")
        audio_frame.pack(fill="x", pady=8)
        
        sound_switch = ctk.CTkSwitch(
            audio_frame,
            text="🔊 Sound Effects",
            variable=self.sound_effects,
            font=ctk.CTkFont(size=13),
            progress_color=self.COLORS['primary']
        )
        sound_switch.pack(side="left", padx=(0, 20))
        
        music_switch = ctk.CTkSwitch(
            audio_frame,
            text="🎵 Background Music",
            variable=self.music,
            command=self._on_music_toggle,
            font=ctk.CTkFont(size=13),
            progress_color=self.COLORS['primary']
        )
        music_switch.pack(side="left")

    def _create_action_buttons(self):
        """Crear botones de acción"""
        action_section = ctk.CTkFrame(
            self.play_section,
            fg_color="transparent"
        )
        action_section.pack(fill="x", padx=25, pady=25)
        
        # Botones principales
        buttons_frame = ctk.CTkFrame(action_section, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)
        
        # Botón salir
        exit_button = ctk.CTkButton(
            buttons_frame,
            text="🚪 EXIT",
            command=self._graceful_exit,
            fg_color=self.COLORS['danger'],
            hover_color="#C0392B",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
            height=40,
            corner_radius=10
        )
        exit_button.pack(side="left", padx=(0, 15))
        
        # Botón música
        self.music_button = ctk.CTkButton(
            buttons_frame,
            text="🔇 MUTE MUSIC",
            command=self._toggle_music,
            fg_color=self.COLORS['warning'],
            hover_color="#E67E22", 
            font=ctk.CTkFont(size=14, weight="bold"),
            width=140,
            height=40,
            corner_radius=10
        )
        self.music_button.pack(side="left", padx=(0, 15))
        
        # Botón jugar (principal)
        play_button = ctk.CTkButton(
            buttons_frame,
            text="🎮 START BATTLE",
            command=self._start_game_flow,
            fg_color=self.COLORS['success'],
            hover_color="#229954",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=45,
            corner_radius=12
        )
        play_button.pack(side="right")

    def _create_status_bar(self):
        """Crear barra de estado inferior"""
        self.status_bar = ctk.CTkFrame(
            self.main_container,
            fg_color=self.COLORS['dark_card'],
            height=40,
            corner_radius=0
        )
        self.status_bar.pack(fill="x", side="bottom", padx=0, pady=0)
        self.status_bar.pack_propagate(False)
        
        self._create_status_content()

    def _create_status_content(self):
        """Crear contenido de la barra de estado"""
        # Estado de conexión
        connection_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        connection_frame.pack(side="left", padx=20, pady=10)
        
        self.connection_status_label = ctk.CTkLabel(
            connection_frame,
            text="🔴 Offline",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        self.connection_status_label.pack(side="left")
        
        # Información del sistema
        system_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        system_frame.pack(side="right", padx=20, pady=10)
        
        version_label = ctk.CTkLabel(
            system_frame,
            text="Snake Arena Pro v2.1.0",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        version_label.pack(side="right")

    def _finalize_setup(self):
        """Finalizar configuración inicial"""
        self._update_interface_state()
        self._load_player_stats()
        self._start_background_music()
        self._initialize_network_discovery()

    # =============================================================================
    # MÉTODOS DE ACTUALIZACIÓN DE INTERFAZ
    # =============================================================================

    def _on_game_mode_changed(self):
        """Manejar cambio de modo de juego"""
        self._update_interface_state()
        self._update_player_section()

    def _on_multiplayer_mode_changed(self):
        """Manejar cambio de modo multijugador"""
        if self.multiplayer_mode.get() == "client":
            self._enable_client_mode()
        else:
            self._enable_host_mode()

    def _enable_client_mode(self):
        """Habilitar modo cliente"""
        self.ip_entry.configure(state="normal")
        self.port_entry.configure(state="normal")
        self.instructions_label.configure(
            text="Enter the host IP address and click START BATTLE to join the game"
        )
        self.ip_info_label.configure(text_color=self.COLORS['secondary'])

    def _enable_host_mode(self):
        """Habilitar modo host"""
        self.ip_entry.configure(state="disabled")
        self.port_entry.configure(state="normal")
        self.instructions_label.configure(
            text="Share your IP address with friends and click START BATTLE to host"
        )
        self.ip_info_label.configure(text_color=self.COLORS['success'])

    def _update_interface_state(self):
        """Actualizar estado completo de la interfaz"""
        # Ocultar todas las secciones condicionales primero
        self.multiplayer_section.pack_forget()
        
        # Mostrar secciones según el modo
        if self.game_mode.get() == "single_player":
            self._show_single_player_interface()
        elif self.game_mode.get() == "two_player":
            self._show_two_player_interface()
        else:
            self._show_multiplayer_interface()

    def _show_single_player_interface(self):
        """Mostrar interfaz para un jugador"""
        self.name_info_label.configure(
            text="Solo challenge - Test your skills against AI opponents"
        )
        self._update_connection_status("Solo mode - No network required")

    def _show_two_player_interface(self):
        """Mostrar interfaz para dos jugadores"""
        self.name_info_label.configure(
            text="Local duel - Player 1 (WASD) vs Player 2 (Arrow keys)"
        )
        self._update_connection_status("Local multiplayer - No network required")

    def _show_multiplayer_interface(self):
        """Mostrar interfaz multijugador"""
        self.multiplayer_section.pack(fill="x", padx=0, pady=15)
        self.name_info_label.configure(
            text="Online battle - Each player uses their own device and name"
        )
        self._update_connection_status("Online multiplayer - Network connection required")

    def _update_connection_status(self, status):
        """Actualizar estado de conexión"""
        self.connection_status_label.configure(text=f"📡 {status}")

    def _update_player_section(self):
        """Actualizar sección del jugador"""
        # Implementar lógica de actualización según estadísticas
        pass

    # =============================================================================
    # MÉTODOS DE AUDIO
    # =============================================================================

    def _start_background_music(self):
        """Iniciar música de fondo"""
        if not self.menu_music_path or not self.music.get():
            return
            
        try:
            pygame.mixer.music.load(self.menu_music_path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)
            self.music_playing = True
            self.music_button.configure(text="🔇 MUTE MUSIC")
        except Exception as e:
            print(f"Music error: {e}")

    def _toggle_music(self):
        """Alternar música"""
        if self.music_playing:
            pygame.mixer.music.pause()
            self.music_playing = False
            self.music_button.configure(text="🔊 UNMUTE MUSIC")
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
            self.music_button.configure(text="🔇 MUTE MUSIC")

    def _on_music_toggle(self):
        """Manejar cambio de estado de música"""
        if self.music.get():
            if not self.music_playing:
                self._start_background_music()
        else:
            if self.music_playing:
                pygame.mixer.music.pause()
                self.music_playing = False

    # =============================================================================
    # MÉTODOS DE NAVEGACIÓN (Placeholders)
    # =============================================================================

    def _show_play_section(self):
        """Mostrar sección de juego"""
        print("Navigating to Play section")

    def _show_stats_section(self):
        """Mostrar sección de estadísticas"""
        print("Navigating to Stats section")

    def _show_settings_section(self):
        """Mostrar sección de configuración"""
        print("Navigating to Settings section")

    def _show_help_section(self):
        """Mostrar sección de ayuda"""
        print("Navigating to Help section")

    # =============================================================================
    # MÉTODOS DE JUEGO PRINCIPALES
    # =============================================================================

    def _start_game_flow(self):
        """Iniciar flujo de juego"""
        if not self._validate_inputs():
            return
            
        if not self._check_player_registration():
            return
            
        self._launch_game_session()

    def _validate_inputs(self):
        """Validar entradas del usuario"""
        player_name = self.player1_name.get().strip()
        
        if not player_name:
            self._show_error_dialog("Player name cannot be empty", "Please enter your player name")
            return False
            
        if " " in player_name:
            self._show_error_dialog("Invalid player name", "Player name cannot contain spaces")
            return False
            
        # Validación multijugador
        if self.game_mode.get() in [MODE_MULTIPLAYER_HOST, MODE_MULTIPLAYER_CLIENT]:
            if self.multiplayer_mode.get() == "client":
                if not self.server_ip.get().strip():
                    self._show_error_dialog("Server IP required", "Please enter the host server IP address")
                    return False
                    
                try:
                    port = int(self.server_port.get())
                    if not (1 <= port <= 65535):
                        raise ValueError
                except ValueError:
                    self._show_error_dialog("Invalid port", "Please enter a valid port number (1-65535)")
                    return False
                    
        return True

    def _check_player_registration(self):
        """Verificar registro del jugador"""
        player_name = self.player1_name.get().strip()
        existing_users = self.db_service.check_username(player_name)
        
        if existing_users:
            return self._show_returning_player_dialog(existing_users[0])
        else:
            self.db_service.register_new_player(player_name)
            return True

    def _show_returning_player_dialog(self, username):
        """Mostrar diálogo para jugador existente"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Welcome Back!")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Contenido del diálogo
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        welcome_label = ctk.CTkLabel(
            content_frame,
            text=f"Welcome back, {username}!",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        welcome_label.pack(pady=(0, 20))

        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        cancel_button.pack(side="left", padx=10)

        continue_button = ctk.CTkButton(
            button_frame,
            text="Continue",
            command=lambda: [dialog.destroy(), self.launch_game()],
            fg_color="#2ECC71",
            hover_color="#27AE60"
        )
        continue_button.pack(side="right", padx=10)

        self.root.wait_window(dialog)
        return True


def run_menu():
    app = MainMenu()
    app.root.mainloop()
    return "QUIT"


if __name__ == "__main__":
    run_menu()