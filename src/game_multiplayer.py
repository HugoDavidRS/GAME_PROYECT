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
        self.player_number = 1 if is_host else 2
        
        # Inicializar objetos del juego
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
        """Inicializar objetos del juego"""
        # Serpientes
        self.snake = Snake(start_position=(3, 10), player_number=1)
        self.snake2 = Snake(start_position=(22, 10), player_number=2)
        
        # Fruta y mina
        self.fruit = Fruit()
        self.mine = Mines()
        if self.is_host:
            self.validate_mine_position()
        
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
                    self.connection_status = f"Servidor creado en puerto {self.port}. Esperando jugador..."
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
            else:
                self.connection_status = f"Error conectando a {connect_host}:{self.port}"
                self.game_state = 'connection_failed'
                    
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            self.connection_status = f"Error: {str(e)}"
            self.game_state = 'connection_failed'

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
            # Verificar si hay 2 jugadores conectados
            if self.is_host and self.server and len(self.server.clients) == 2:
                self.start_countdown()
                # Notificar a todos que el juego inicia
                if self.client:
                    self.client.send_game_state(self)

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
        """Manejar estado de juego activo"""
        # Solo el host ejecuta la lógica del juego
        if self.is_host:
            self.snake.move_snake()
            self.snake2.move_snake()
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
            on_snake = any(self.mine.pos == block for block in self.snake.body)
            on_snake2 = any(self.mine.pos == block for block in self.snake2.body)
            
            if not in_restricted_area and not on_fruit and not on_snake and not on_snake2:
                valid_position = True
            else:
                self.mine.randomize()

    def check_collision(self):
        """Verificar colisiones (solo host)"""
        if not self.is_host:
            return
            
        # Colisiones con fruta
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            if self.sound_enabled:
                self.snake.play_crunch_sound()
            
        if self.fruit.pos == self.snake2.body[0]:
            self.fruit.randomize()
            self.snake2.add_block()
            if self.sound_enabled:
                self.snake2.play_crunch_sound()
        
        # Colisiones con minas
        if self.mine.pos == self.snake.body[0]:
            if self.sound_enabled:
                self.snake.play_boom_sound()
            self._handle_mine_collision(self.snake, 2)
            
        if self.mine.pos == self.snake2.body[0]:
            if self.sound_enabled:
                self.snake.play_boom_sound()
            self._handle_mine_collision(self.snake2, 1)
            
        # Validar posiciones
        self._validate_positions()

    def _handle_mine_collision(self, snake, winner_if_dead):
        """Manejar colisión con mina"""
        if len(snake.body) >= 5:
            snake.body.pop()
            snake.body.pop()
        elif len(snake.body) == 4:
            snake.body.pop()
        elif len(snake.body) == 3:
            self.game_over(winner_if_dead)
        
        self.mine.randomize()
        self.validate_mine_position()

    def _validate_positions(self):
        """Validar posiciones de fruta y mina"""
        # Evitar que fruta aparezca en lugares no válidos
        all_blocks = self.snake.body[1:] + self.snake2.body[1:]
        for block in all_blocks:
            if block == self.fruit.pos:
                self.fruit.randomize()
                break
        
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
            
        snake1_dead = self._is_snake_dead(self.snake, self.snake2)
        snake2_dead = self._is_snake_dead(self.snake2, self.snake)
        
        # Lógica de fin de juego
        if snake1_dead and snake2_dead:
            snake1_score = len(self.snake.body) - 3
            snake2_score = len(self.snake2.body) - 3
            
            if snake1_score > snake2_score:
                self.game_over(1)
            elif snake1_score < snake2_score:
                self.game_over(2)
            else:
                self.game_over(0)
        elif snake1_dead:
            self.game_over(2)
        elif snake2_dead:
            self.game_over(1)

    def _is_snake_dead(self, snake, other_snake):
        """Verificar si una serpiente está muerta"""
        # Colisión con paredes
        if not 0 <= snake.body[0].x < CELL_NUMBER or not 0 <= snake.body[0].y < CELL_NUMBER:
            return True
            
        # Colisión consigo misma
        for block in snake.body[1:]:
            if block == snake.body[0]:
                return True
                
        # Colisión con otra serpiente
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
        
        # Actualizar base de datos
        score1 = len(self.snake.body) - 3
        score2 = len(self.snake2.body) - 3
        
        self.db_service.update_score_multiplayer(self.p1_name, score1)
        self.db_service.update_score_multiplayer(self.p2_name, score2)
        
        if winner == 1:
            self.db_service.update_multiplayer_win(self.p1_name)
        elif winner == 2:
            self.db_service.update_multiplayer_win(self.p2_name)
            
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
        self.snake.reset(start_position=(3, 10), player_number=1)
        self.snake2.reset(start_position=(22, 10), player_number=2)
        self.fruit.randomize()
        self.mine.randomize()
        if self.is_host:
            self.validate_mine_position()
        self.start_countdown()

    # Métodos de dibujo
    def draw_elements(self):
        """Dibujar elementos del juego"""
        self.draw_grass()
        
        if self.game_state == 'connecting' or self.game_state == 'connection_failed':
            self.draw_connection_screen()
        elif self.game_state == 'start':
            self.start_button.draw(self.screen)
        elif self.game_state == 'countdown':
            self.draw_countdown()
        elif self.game_state == 'playing':
            self.fruit.draw_fruit(self.screen, CELL_SIZE)
            self.mine.draw_mine(self.screen, CELL_SIZE)
            self.snake.draw_snake(self.screen, CELL_SIZE)
            self.snake2.draw_snake(self.screen, CELL_SIZE)
        elif self.game_state == 'game_over':
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
            self.draw_game_over()
            
        self.draw_score()

    def draw_connection_screen(self):
        """Dibujar pantalla de conexión"""
        font = pygame.font.Font(None, 36)
        text = font.render(self.connection_status, True, (255, 255, 255))
        text_rect = text.get_rect(center=(CELL_NUMBER * CELL_SIZE // 2, CELL_NUMBER * CELL_SIZE // 2 - 50))
        self.screen.blit(text, text_rect)
        
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

        if self.winner == 1:
            game_over_text = f"{self.p1_name} Wins!"
            text_color = (0, 0, 200)
        elif self.winner == 2:
            game_over_text = f"{self.p2_name} Wins!"
            text_color = (0, 0, 200)
        elif self.winner == 0:
            game_over_text = "It's a Tie!"
            text_color = (255, 0, 0)
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
        """Dibujar puntuaciones"""
        margin = 20
        snake_size = 40
        padding = 10
        bottom_padding = 2

        # Player 1 (Left)
        score_text_p1 = str(len(self.snake.body) - 3)
        score_surface_p1 = self.game_font.render(score_text_p1, True, (56, 74, 12))
        snake_image_p1 = pygame.transform.scale(self.fruit.p1, (snake_size, snake_size))
        snake_rect_p1 = snake_image_p1.get_rect(midleft=(margin, margin + 12))
        score_rect_p1 = score_surface_p1.get_rect(midleft=(snake_rect_p1.right + 10, snake_rect_p1.centery))

        bg_rect_p1 = pygame.Rect(
            snake_rect_p1.left - padding, snake_rect_p1.top - padding,
            snake_rect_p1.width + score_rect_p1.width + padding * 2 + 10,
            max(snake_rect_p1.height, score_rect_p1.height) + padding + bottom_padding
        )

        pygame.draw.rect(self.screen, (167, 209, 61), bg_rect_p1, border_radius=8)
        pygame.draw.rect(self.screen, (56, 74, 12), bg_rect_p1, 2, border_radius=8)
        self.screen.blit(snake_image_p1, snake_rect_p1)
        self.screen.blit(score_surface_p1, score_rect_p1)

        # Player 2 (Right)
        score_text_p2 = str(len(self.snake2.body) - 3)
        score_surface_p2 = self.game_font.render(score_text_p2, True, (56, 74, 12))
        snake_image_p2 = pygame.transform.scale(self.fruit.p2, (snake_size, snake_size))
        score_rect_p2 = score_surface_p2.get_rect(midright=(CELL_SIZE * CELL_NUMBER - margin, margin + 12))
        snake_rect_p2 = snake_image_p2.get_rect(midright=(score_rect_p2.left - 10, score_rect_p2.centery))

        bg_rect_p2 = pygame.Rect(
            snake_rect_p2.left - padding, snake_rect_p2.top - padding,
            snake_rect_p2.width + score_rect_p2.width + padding * 2 + 10,
            max(snake_rect_p2.height, score_rect_p2.height) + padding + bottom_padding
        )

        pygame.draw.rect(self.screen, (167, 209, 61), bg_rect_p2, border_radius=8)
        pygame.draw.rect(self.screen, (56, 74, 12), bg_rect_p2, 2, border_radius=8)
        self.screen.blit(snake_image_p2, snake_rect_p2)
        self.screen.blit(score_surface_p2, score_rect_p2)

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
        if self.game_state == 'start':
            if self.start_button.is_clicked(pos):
                self.start_countdown()
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
        """Manejar entrada de teclado"""
        # Jugador local (dependiendo de si es host o cliente)
        if self.player_number == 1:
            self._handle_player1_input(event)
        else:
            self._handle_player2_input(event)
            
        # Enviar input al servidor
        if self.client and self.client.connected:
            input_str = self._get_input_string(event)
            if input_str:
                self.client.send_input(input_str)

    def _handle_player1_input(self, event):
        """Manejar input del jugador 1 (WASD)"""
        if event.key == pygame.K_w and self.snake.direction.y != 1:
            self.snake.direction = Vector2(0, -1)
        elif event.key == pygame.K_s and self.snake.direction.y != -1:
            self.snake.direction = Vector2(0, 1)
        elif event.key == pygame.K_d and self.snake.direction.x != -1:
            self.snake.direction = Vector2(1, 0)
        elif event.key == pygame.K_a and self.snake.direction.x != 1:
            self.snake.direction = Vector2(-1, 0)

    def _handle_player2_input(self, event):
        """Manejar input del jugador 2 (Flechas)"""
        if event.key == pygame.K_UP and self.snake2.direction.y != 1:
            self.snake2.direction = Vector2(0, -1)
        elif event.key == pygame.K_DOWN and self.snake2.direction.y != -1:
            self.snake2.direction = Vector2(0, 1)
        elif event.key == pygame.K_RIGHT and self.snake2.direction.x != -1:
            self.snake2.direction = Vector2(1, 0)
        elif event.key == pygame.K_LEFT and self.snake2.direction.x != 1:
            self.snake2.direction = Vector2(-1, 0)

    def _get_input_string(self, event):
        """Convertir evento de tecla a string para red"""
        key_mapping = {
            pygame.K_w: 'up', pygame.K_s: 'down', pygame.K_a: 'left', pygame.K_d: 'right',
            pygame.K_UP: 'up', pygame.K_DOWN: 'down', pygame.K_LEFT: 'left', pygame.K_RIGHT: 'right'
        }
        return key_mapping.get(event.key)

    def cleanup(self):
        """Limpiar recursos"""
        if self.client:
            self.client.disconnect()
        if self.server:
            self.server.stop_server()