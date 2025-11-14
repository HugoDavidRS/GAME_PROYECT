import pygame
import os
import sys
from pygame.math import Vector2
from src.constants import CELL_SIZE, CELL_NUMBER, GRASS_COLOR, GRASS_COLOR_ALT
from src.sprites.snake import Snake
from src.sprites.fruit import Fruit
from src.sprites.button import Button
from src.sprites.mines import Mines
from src.services.dbhelper import DatabaseService
from src.services.network import GameClient, GameServer
from src.services.protocol import GameProtocol

class MultiplayerGame:
    def __init__(self, game_mode="multiplayer_host", p1_name="Player 1", p2_name="Player 2", 
                 sound="on", music="on", host=None, port=5555, is_host=True):
        
        # Configuración de pantalla
        self.screen = pygame.display.set_mode((CELL_NUMBER * CELL_SIZE, CELL_NUMBER * CELL_SIZE))
        self.clock = pygame.time.Clock()
        font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Font", "PoetsenOne-Regular.ttf")
        self.game_font = pygame.font.Font(font_path, 50)
        
        # Configuración de red
        self.is_host = is_host
        self.host = host
        self.port = port
        self.client = None
        self.server = None
        self.protocol = GameProtocol()
        
        # Configuración del juego
        self.game_mode = game_mode
        self.p1_name = p1_name
        self.p2_name = p2_name
        self.sound_enabled = sound == "on"
        self.music_enabled = music == "on"
        
        # Estado del juego
        self.game_state = 'connecting'
        self.connection_status = "Conectando..."
        self.player_number = 1 if is_host else None  # Se asignará cuando se conecte
        self.game_can_start = False
        
        # Inicializar objetos del juego para 5 jugadores
        self._initialize_game_objects()
        
        # Base de datos
        self.db_service = DatabaseService()
        
        # Contador
        self.countdown = 4
        self.last_countdown_tick = None
        
        # Timer para updates
        self.SCREEN_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(self.SCREEN_UPDATE, 150)
        
        # Conectar a red
        self._connect_to_network()

    def _initialize_game_objects(self):
        """Inicializar objetos del juego para 5 jugadores"""
        # Posiciones iniciales para 5 jugadores
        start_positions = [
            (3, 10),   # Jugador 1 - Esquina superior izquierda
            (22, 10),  # Jugador 2 - Esquina superior derecha  
            (3, 20),   # Jugador 3 - Esquina inferior izquierda
            (22, 20),  # Jugador 4 - Esquina inferior derecha
            (12, 15)   # Jugador 5 - Centro
        ]
        
        # Direcciones iniciales
        start_directions = [
            Vector2(1, 0),   # Jugador 1 - Derecha
            Vector2(-1, 0),  # Jugador 2 - Izquierda
            Vector2(1, 0),   # Jugador 3 - Derecha  
            Vector2(-1, 0),  # Jugador 4 - Izquierda
            Vector2(0, -1)   # Jugador 5 - Arriba
        ]
        
        # Inicializar serpientes para 5 jugadores
        self.snakes = {}
        for i in range(1, 6):  # Jugadores 1-5
            self.snakes[i] = Snake(start_position=start_positions[i-1], player_number=i)
            self.snakes[i].direction = start_directions[i-1]
        
        # Fruta y mina
        self.fruit = Fruit()
        self.mine = Mines()
        if self.is_host:
            self.validate_mine_position()
        
        # Nombres de jugadores (se actualizarán con los nombres reales)
        self.player_names = {
            1: self.p1_name if self.is_host else "Player_1",
            2: self.p2_name if self.is_host else "Player_2",
            3: "Player_3",
            4: "Player_4", 
            5: "Player_5"
        }
        
        # Botones
        self._initialize_buttons()

    def _initialize_buttons(self):
        """Inicializar botones de la interfaz"""
        button_width, button_height = 200, 50
        button_x = (CELL_NUMBER * CELL_SIZE - button_width) // 2
        button_y = (CELL_NUMBER * CELL_SIZE - button_height) // 2
        
        self.start_button = Button(button_x, button_y, button_width, button_height, 
                                   'Start Game', (0, 200, 0), (255, 255, 255))
        
        self.reset_button = Button(button_x, button_y, button_width, button_height, 
                                   'Replay!', (255, 165, 0), (0, 0, 0))
        
        spacing = 10
        adjusted_height = button_height - 5
        
        self.quit_button = Button(button_x, button_y + adjusted_height + spacing, 
                                  button_width, adjusted_height, 
                                  'Quit Game', (200, 0, 0), (255, 255, 255))
        
        self.menu_button = Button(button_x, button_y + 2 * (adjusted_height + spacing), 
                                  button_width, adjusted_height, 
                                  'Menu', (0, 150, 255), (0, 0, 0))
        
        # Botones de conexión
        self.retry_button = Button(button_x, button_y + 100, button_width, button_height,
                                   'Reintentar', (255, 165, 0), (0, 0, 0))
        
        self.back_button = Button(button_x, button_y + 170, button_width, button_height,
                                  'Volver al Menú', (150, 150, 150), (0, 0, 0))

    def _connect_to_network(self):
        """Conectar a la red según el modo"""
        try:
            if self.is_host:
                # El host crea servidor y se conecta como cliente
                self.server = GameServer(host='0.0.0.0', port=self.port)
                if self.server.start_server():
                    self.connection_status = f"Servidor creado en puerto {self.port}. Esperando jugadores..."
                    print(self.connection_status)
                else:
                    self.connection_status = "Error creando servidor"
                    self.game_state = 'connection_failed'
                    return
            
            # Todos los jugadores (incluido host) se conectan como clientes
            self.client = GameClient()
            connect_host = 'localhost' if self.is_host else self.host
            
            if self.client.connect_to_server(connect_host, self.port):
                self.connection_status = f"Conectado a {connect_host}:{self.port}"
                print(self.connection_status)
                
                # Enviar nombre del jugador al servidor
                if self.is_host:
                    self.client.send_player_name(self.p1_name)
                else:
                    # Los clientes envían su nombre (usarán player2_name como su nombre)
                    self.client.send_player_name(self.p2_name)
                    
            else:
                self.connection_status = f"Error conectando a {connect_host}:{self.port}"
                self.game_state = 'connection_failed'
                    
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            self.connection_status = f"Error: {str(e)}"
            self.game_state = 'connection_failed'

    def update_player_name(self, player_number, name):
        """Actualizar nombre de jugador recibido por red"""
        if 1 <= player_number <= 5:
            self.player_names[player_number] = name
            print(f"📝 Jugador {player_number} ahora es: {name}")

    def update(self):
        """Actualizar estado del juego"""
        if self.game_state == 'connecting':
            self._handle_connecting_state()
        elif self.game_state == 'countdown':
            self._handle_countdown()
        elif self.game_state == 'playing':
            self._handle_playing_state()

    def _handle_connecting_state(self):
        """Manejar estado de conexión"""
        if self.client and self.client.connected:
            # Si somos host y hay al menos 2 jugadores, permitir inicio
            if self.is_host and self.game_can_start:
                self.connection_status = f"✅ {self.client.connected_players}/5 jugadores - Click 'Start Game'"
            elif not self.is_host:
                self.connection_status = f"✅ Conectado - Esperando que el host inicie el juego"

    def _handle_countdown(self):
        """Manejar cuenta regresiva"""
        current_time = pygame.time.get_ticks()
        if self.last_countdown_tick is None or current_time - self.last_countdown_tick >= 1000:
            self.countdown -= 1
            self.last_countdown_tick = current_time
            
            # Sincronizar cuenta regresiva si somos host
            if self.is_host and self.client:
                self.client.send_game_state(self)
            
            if self.countdown <= 0:
                self.game_state = 'playing'
                if self.music_enabled:
                    self._start_game_music()

    def _handle_playing_state(self):
        """Manejar estado de juego activo para 5 jugadores"""
        # Solo el host ejecuta la lógica del juego
        if self.is_host:
            # Mover todas las serpientes activas
            for snake in self.snakes.values():
                if snake:  # Solo mover serpientes que existen
                    snake.move_snake()
            
            self.check_collision()
            self.check_fail()
            
            # Sincronizar estado con clientes
            if self.client:
                self.client.send_game_state(self)

    def handle_network_messages(self):
        """Procesar mensajes de red"""
        self.protocol.process_network_messages(self)

    def _start_game_music(self):
        """Iniciar música del juego"""
        try:
            game_music = os.path.join(os.path.dirname(__file__), "..", "assets", "Sound", "game_music.wav")
            pygame.mixer.init()
            pygame.mixer.music.load(game_music)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"❌ Error cargando música: {e}")

    # Métodos del juego (solo ejecutados por el host)
    def validate_mine_position(self):
        """Validar posición de la mina (solo host)"""
        if not self.is_host:
            return
            
        valid_position = False
        while not valid_position:
            in_restricted_area = False
            
            if self.mine.pos.y < 2:
                if self.mine.pos.x < 3 or self.mine.pos.x >= CELL_NUMBER - 3:
                    in_restricted_area = True
            
            on_fruit = self.mine.pos == self.fruit.pos
            
            # Verificar colisión con cualquier serpiente
            on_snake = False
            for snake in self.snakes.values():
                if snake and any(self.mine.pos == block for block in snake.body):
                    on_snake = True
                    break
            
            if not in_restricted_area and not on_fruit and not on_snake:
                valid_position = True
            else:
                self.mine.randomize()

    def check_collision(self):
        """Verificar colisiones (solo host)"""
        if not self.is_host:
            return
            
        # Colisiones con fruta
        for player_num, snake in self.snakes.items():
            if snake and self.fruit.pos == snake.body[0]:
                self.fruit.randomize()
                snake.add_block()
                if self.sound_enabled:
                    snake.play_crunch_sound()
        
        # Colisiones con minas
        for player_num, snake in self.snakes.items():
            if snake and self.mine.pos == snake.body[0]:
                if self.sound_enabled:
                    snake.play_boom_sound()
                self._handle_mine_collision(snake, player_num)
            
        # Validar posiciones
        self._validate_positions()

    def _handle_mine_collision(self, snake, player_num):
        """Manejar colisión con mina"""
        if len(snake.body) >= 5:
            snake.body.pop()
            snake.body.pop()
        elif len(snake.body) == 4:
            snake.body.pop()
        elif len(snake.body) == 3:
            # Determinar ganador (el jugador con más puntos)
            self._determine_winner()
        
        self.mine.randomize()
        self.validate_mine_position()

    def _determine_winner(self):
        """Determinar ganador entre todos los jugadores"""
        scores = {}
        for player_num, snake in self.snakes.items():
            if snake:
                scores[player_num] = len(snake.body) - 3
        
        # Encontrar jugador con máxima puntuación
        max_score = max(scores.values()) if scores else 0
        winners = [player_num for player_num, score in scores.items() if score == max_score]
        
        if len(winners) == 1:
            self.game_over(winners[0])
        else:
            self.game_over(0)  # Empate

    def _validate_positions(self):
        """Validar posiciones de fruta y mina"""
        # Obtener todos los bloques de todas las serpientes
        all_blocks = []
        for snake in self.snakes.values():
            if snake:
                all_blocks.extend(snake.body[1:])  # Excluir cabezas
        
        # Evitar que fruta aparezca en cuerpos de serpientes
        for block in all_blocks:
            if block == self.fruit.pos:
                self.fruit.randomize()
                break
        
        # Evitar que fruta y mina estén en la misma posición
        if self.fruit.pos == self.mine.pos:
            self.fruit.randomize()
            
        # Evitar áreas restringidas
        for y in range(2):
            for x in range(3):
                if self.fruit.pos == (x, y) or self.mine.pos == (x, y):
                    if self.fruit.pos == (x, y):
                        self.fruit.randomize()
                    if self.mine.pos == (x, y):
                        self.mine.randomize()
                        self.validate_mine_position()

            for x in range(CELL_NUMBER - 3, CELL_NUMBER):
                if self.fruit.pos == (x, y) or self.mine.pos == (x, y):
                    if self.fruit.pos == (x, y):
                        self.fruit.randomize()
                    if self.mine.pos == (x, y):
                        self.mine.randomize()
                        self.validate_mine_position()

    def check_fail(self):
        """Verificar condiciones de fin de juego (solo host)"""
        if not self.is_host:
            return
            
        dead_players = []
        
        for player_num, snake in self.snakes.items():
            if snake and self._is_snake_dead(snake, player_num):
                dead_players.append(player_num)
        
        # Si todos los jugadores están muertos, determinar ganador
        if dead_players and len(dead_players) == len([s for s in self.snakes.values() if s]):
            self._determine_winner()

    def _is_snake_dead(self, snake, player_num):
        """Verificar si una serpiente está muerta"""
        # Colisión con paredes
        if not 0 <= snake.body[0].x < CELL_NUMBER or not 0 <= snake.body[0].y < CELL_NUMBER:
            return True
            
        # Colisión consigo misma
        for block in snake.body[1:]:
            if block == snake.body[0]:
                return True
                
        # Colisión con otras serpientes
        for other_player_num, other_snake in self.snakes.items():
            if other_snake and other_player_num != player_num:
                for block in other_snake.body:
                    if block == snake.body[0]:
                        if hasattr(snake, 'play_hiss_sound'):
                            snake.play_hiss_sound()
                        return True
                
        return False

    def game_over(self, winner):
        """Manejar fin del juego"""
        self.game_state = 'game_over'
        self.winner = winner
        
        # Actualizar base de datos para todos los jugadores
        for player_num, snake in self.snakes.items():
            if snake and player_num in self.player_names:
                score = len(snake.body) - 3
                self.db_service.update_score_multiplayer(self.player_names[player_num], score)
        
        if winner != 0 and winner in self.player_names:
            self.db_service.update_multiplayer_win(self.player_names[winner])
            
        # Notificar a clientes
        if self.is_host and self.client:
            self.client.send_game_state(self)

    def start_countdown(self):
        """Iniciar cuenta regresiva"""
        self.game_state = 'countdown'
        self.countdown = 4
        self.last_countdown_tick = None

    def reset_game(self):
        """Reiniciar juego"""
        # Reiniciar todas las serpientes
        start_positions = [(3, 10), (22, 10), (3, 20), (22, 20), (12, 15)]
        start_directions = [Vector2(1, 0), Vector2(-1, 0), Vector2(1, 0), Vector2(-1, 0), Vector2(0, -1)]
        
        for i in range(1, 6):
            if i in self.snakes:
                self.snakes[i].reset(start_position=start_positions[i-1], player_number=i)
                self.snakes[i].direction = start_directions[i-1]
        
        self.fruit.randomize()
        self.mine.randomize()
        if self.is_host:
            self.validate_mine_position()
        self.start_countdown()

    # Métodos de dibujo para 5 jugadores
    def draw_elements(self):
        """Dibujar elementos del juego para 5 jugadores"""
        self.draw_grass()
        
        if self.game_state == 'connecting' or self.game_state == 'connection_failed':
            self.draw_connection_screen()
        elif self.game_state == 'start':
            if self.is_host and self.game_can_start:
                self.start_button.draw(self.screen)
        elif self.game_state == 'countdown':
            self.draw_countdown()
        elif self.game_state == 'playing':
            self.fruit.draw_fruit(self.screen, CELL_SIZE)
            self.mine.draw_mine(self.screen, CELL_SIZE)
            
            # Dibujar todas las serpientes activas
            for snake in self.snakes.values():
                if snake:
                    snake.draw_snake(self.screen, CELL_SIZE)
                    
        elif self.game_state == 'game_over':
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
            self.draw_game_over()
            
        self.draw_score()

    def draw_connection_screen(self):
        """Dibujar pantalla de conexión"""
        font = pygame.font.Font(None, 36)
        
        # Mostrar estado de conexión
        status_text = font.render(self.connection_status, True, (255, 255, 255))
        status_rect = status_text.get_rect(center=(CELL_NUMBER * CELL_SIZE // 2, CELL_NUMBER * CELL_SIZE // 2 - 50))
        self.screen.blit(status_text, status_rect)
        
        # Mostrar información adicional para host
        if self.is_host and hasattr(self, 'client') and self.client:
            players_text = font.render(f"Jugadores conectados: {self.client.connected_players}/5", True, (200, 200, 100))
            players_rect = players_text.get_rect(center=(CELL_NUMBER * CELL_SIZE // 2, CELL_NUMBER * CELL_SIZE // 2))
            self.screen.blit(players_text, players_rect)
            
            if self.game_can_start:
                start_text = font.render("Click 'Start Game' para iniciar", True, (100, 255, 100))
                start_rect = start_text.get_rect(center=(CELL_NUMBER * CELL_SIZE // 2, CELL_NUMBER * CELL_SIZE // 2 + 50))
                self.screen.blit(start_text, start_rect)
        
        if self.game_state == 'connection_failed':
            self.retry_button.draw(self.screen)
            self.back_button.draw(self.screen)

    def draw_countdown(self):
        """Dibujar cuenta regresiva"""
        countdown_text = self.game_font.render(str(self.countdown), True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(CELL_NUMBER * CELL_SIZE // 2, CELL_NUMBER * CELL_SIZE // 2))
        self.screen.blit(countdown_text, countdown_rect)

    def draw_game_over(self):
        """Dibujar pantalla de fin de juego"""
        font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Font", "PoetsenOne-Regular.ttf")
        font = pygame.font.Font(font_path, 50)

        if self.winner == 0:
            game_over_text = "It's a Tie!"
            text_color = (255, 0, 0)
        elif self.winner in self.player_names:
            game_over_text = f"{self.player_names[self.winner]} Wins!"
            text_color = (0, 0, 200)
        else:
            game_over_text = "Game Over"
            text_color = (255, 0, 0)

        game_over_surface = font.render(game_over_text, True, text_color)
        text_rect = game_over_surface.get_rect(center=(CELL_NUMBER * CELL_SIZE // 2, CELL_NUMBER * CELL_SIZE // 2 - 100))
        self.screen.blit(game_over_surface, text_rect)

        self.reset_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        self.menu_button.draw(self.screen)

    def draw_score(self):
        """Dibujar puntuaciones para 5 jugadores"""
        if self.game_state != 'playing':
            return
            
        margin = 20
        snake_size = 30  # Más pequeño para 5 jugadores
        padding = 6
        bottom_padding = 2
        
        # Posiciones para los 5 jugadores
        score_positions = [
            (margin, margin + 12),                           # Jugador 1 - Superior izquierda
            (CELL_SIZE * CELL_NUMBER - margin, margin + 12), # Jugador 2 - Superior derecha
            (margin, CELL_SIZE * CELL_NUMBER - margin - 10), # Jugador 3 - Inferior izquierda  
            (CELL_SIZE * CELL_NUMBER - margin, CELL_SIZE * CELL_NUMBER - margin - 10), # Jugador 4 - Inferior derecha
            (CELL_SIZE * CELL_NUMBER // 2, margin + 12)      # Jugador 5 - Centro superior
        ]
        
        # Alineaciones
        alignments = ['midleft', 'midright', 'midleft', 'midright', 'center']
        
        for i in range(1, 6):
            if i in self.snakes and self.snakes[i] and len(self.snakes[i].body) >= 3:
                score_text = str(len(self.snakes[i].body) - 3)
                score_surface = self.game_font.render(score_text, True, (56, 74, 12))
                
                # Cargar imagen de serpiente según jugador (usar p1 o p2 como fallback)
                try:
                    player_img_num = min(i, 2)  # Usar imágenes de player1 o player2
                    snake_image = pygame.transform.scale(getattr(self.fruit, f'p{player_img_num}'), (snake_size, snake_size))
                except:
                    # Fallback si no hay imagen específica
                    snake_image = pygame.transform.scale(self.fruit.p1, (snake_size, snake_size))
                
                # Posicionar según alineación
                if alignments[i-1] == 'midleft':
                    snake_rect = snake_image.get_rect(midleft=(score_positions[i-1][0], score_positions[i-1][1]))
                    score_rect = score_surface.get_rect(midleft=(snake_rect.right + 5, snake_rect.centery))
                elif alignments[i-1] == 'midright':
                    score_rect = score_surface.get_rect(midright=(score_positions[i-1][0], score_positions[i-1][1]))
                    snake_rect = snake_image.get_rect(midright=(score_rect.left - 5, score_rect.centery))
                else:  # center
                    snake_rect = snake_image.get_rect(center=(score_positions[i-1][0] - 20, score_positions[i-1][1]))
                    score_rect = score_surface.get_rect(center=(score_positions[i-1][0] + 20, score_positions[i-1][1]))
                
                # Dibujar fondo
                bg_width = snake_rect.width + score_rect.width + padding * 2 + 8
                bg_height = max(snake_rect.height, score_rect.height) + padding + bottom_padding
                bg_rect = pygame.Rect(
                    min(snake_rect.left, score_rect.left) - padding,
                    snake_rect.top - padding,
                    bg_width,
                    bg_height
                )
                
                pygame.draw.rect(self.screen, (167, 209, 61), bg_rect, border_radius=5)
                pygame.draw.rect(self.screen, (56, 74, 12), bg_rect, 1, border_radius=5)
                
                # Dibujar elementos
                self.screen.blit(snake_image, snake_rect)
                self.screen.blit(score_surface, score_rect)
                
                # Dibujar nombre del jugador (opcional, más pequeño)
                name_font = pygame.font.Font(None, 16)
                name_surface = name_font.render(self.player_names[i], True, (56, 74, 12))
                name_rect = name_surface.get_rect(midtop=(bg_rect.centerx, bg_rect.bottom + 1))
                self.screen.blit(name_surface, name_rect)

    def draw_grass(self):
        """Dibujar fondo de césped"""
        for row in range(CELL_NUMBER):
            if row % 2 == 0:
                for col in range(CELL_NUMBER):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, GRASS_COLOR, grass_rect)
            else:
                for col in range(CELL_NUMBER):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, GRASS_COLOR, grass_rect)

    def handle_input(self, event):
        """Manejar entrada del usuario"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN and self.game_state == 'playing':
            self._handle_key_input(event)

    def _handle_mouse_click(self, pos):
        """Manejar clics del mouse"""
        if self.game_state == 'start' and self.is_host and self.game_can_start:
            if self.start_button.is_clicked(pos):
                self.start_countdown()
                # Notificar a todos que el juego inicia
                if self.client:
                    self.client.send_game_state(self)
        elif self.game_state == 'game_over':
            if self.reset_button.is_clicked(pos):
                self.reset_game()
            elif self.quit_button.is_clicked(pos):
                pygame.quit()
                os._exit(0)
            elif self.menu_button.is_clicked(pos):
                self.game_state = "MENU"
        elif self.game_state == 'connection_failed':
            if self.retry_button.is_clicked(pos):
                self._connect_to_network()
                self.game_state = 'connecting'
            elif self.back_button.is_clicked(pos):
                self.game_state = "MENU"

    def _handle_key_input(self, event):
        """Manejar entrada de teclado para 5 jugadores"""
        if not self.player_number or self.game_state != 'playing':
            return
            
        # El jugador local controla SU serpiente según su player_number
        if self.player_number in self.snakes and self.snakes[self.player_number]:
            snake = self.snakes[self.player_number]
            
            # Controles para el jugador local
            if self.player_number == 1:  # WASD
                if event.key == pygame.K_w and snake.direction.y != 1:
                    snake.direction = Vector2(0, -1)
                elif event.key == pygame.K_s and snake.direction.y != -1:
                    snake.direction = Vector2(0, 1)
                elif event.key == pygame.K_d and snake.direction.x != -1:
                    snake.direction = Vector2(1, 0)
                elif event.key == pygame.K_a and snake.direction.x != 1:
                    snake.direction = Vector2(-1, 0)
                    
            elif self.player_number == 2:  # Flechas
                if event.key == pygame.K_UP and snake.direction.y != 1:
                    snake.direction = Vector2(0, -1)
                elif event.key == pygame.K_DOWN and snake.direction.y != -1:
                    snake.direction = Vector2(0, 1)
                elif event.key == pygame.K_RIGHT and snake.direction.x != -1:
                    snake.direction = Vector2(1, 0)
                elif event.key == pygame.K_LEFT and snake.direction.x != 1:
                    snake.direction = Vector2(-1, 0)
                    
            # Controles adicionales para jugadores 3-5
            elif self.player_number == 3:  # IJKL
                if event.key == pygame.K_i and snake.direction.y != 1:
                    snake.direction = Vector2(0, -1)
                elif event.key == pygame.K_k and snake.direction.y != -1:
                    snake.direction = Vector2(0, 1)
                elif event.key == pygame.K_l and snake.direction.x != -1:
                    snake.direction = Vector2(1, 0)
                elif event.key == pygame.K_j and snake.direction.x != 1:
                    snake.direction = Vector2(-1, 0)
                    
            elif self.player_number == 4:  # Numpad 8456
                if event.key == pygame.K_8 and snake.direction.y != 1:
                    snake.direction = Vector2(0, -1)
                elif event.key == pygame.K_5 and snake.direction.y != -1:
                    snake.direction = Vector2(0, 1)
                elif event.key == pygame.K_6 and snake.direction.x != -1:
                    snake.direction = Vector2(1, 0)
                elif event.key == pygame.K_4 and snake.direction.x != 1:
                    snake.direction = Vector2(-1, 0)
                    
            elif self.player_number == 5:  # TFGH
                if event.key == pygame.K_t and snake.direction.y != 1:
                    snake.direction = Vector2(0, -1)
                elif event.key == pygame.K_g and snake.direction.y != -1:
                    snake.direction = Vector2(0, 1)
                elif event.key == pygame.K_h and snake.direction.x != -1:
                    snake.direction = Vector2(1, 0)
                elif event.key == pygame.K_f and snake.direction.x != 1:
                    snake.direction = Vector2(-1, 0)
            
            # Enviar input al servidor
            if self.client and self.client.connected:
                input_str = self._get_input_string(event)
                if input_str:
                    self.client.send_input(input_str)

    def _get_input_string(self, event):
        """Convertir evento de tecla a string para red"""
        key_mapping = {
            # Jugador 1 (WASD)
            pygame.K_w: 'up', pygame.K_s: 'down', pygame.K_a: 'left', pygame.K_d: 'right',
            # Jugador 2 (Flechas)
            pygame.K_UP: 'up', pygame.K_DOWN: 'down', pygame.K_LEFT: 'left', pygame.K_RIGHT: 'right',
            # Jugador 3 (IJKL)
            pygame.K_i: 'up', pygame.K_k: 'down', pygame.K_j: 'left', pygame.K_l: 'right',
            # Jugador 4 (Numpad)
            pygame.K_8: 'up', pygame.K_5: 'down', pygame.K_4: 'left', pygame.K_6: 'right',
            # Jugador 5 (TFGH)
            pygame.K_t: 'up', pygame.K_g: 'down', pygame.K_f: 'left', pygame.K_h: 'right'
        }
        return key_mapping.get(event.key)

    def cleanup(self):
        """Limpiar recursos"""
        if self.client:
            self.client.disconnect()
        if self.server:
            self.server.stop_server()