import pickle
from datetime import datetime
from pygame.math import Vector2

class GameProtocol:
    """
    Protocolo para la comunicación entre cliente y servidor
    Define los tipos de mensajes y su estructura
    """
    
    # Tipos de mensajes
    MSG_ASSIGN_PLAYER = 'assign_player'
    MSG_PLAYER_JOINED = 'player_joined'
    MSG_GAME_START = 'game_start'
    MSG_PLAYER_INPUT = 'player_input'
    MSG_GAME_STATE = 'game_state'
    MSG_GAME_STATE_UPDATE = 'game_state_update'
    MSG_GAME_OVER = 'game_over'
    MSG_PLAYER_DISCONNECTED = 'player_disconnected'
    MSG_ERROR = 'error'
    
    def __init__(self):
        self.version = "1.0"
    
    def assign_player(self, player_number):
        """Asignar número de jugador al cliente"""
        return {
            'type': self.MSG_ASSIGN_PLAYER,
            'player_number': player_number,
            'timestamp': self._get_timestamp()
        }
    
    def player_joined(self, player_number):
        """Notificar que un jugador se unió"""
        return {
            'type': self.MSG_PLAYER_JOINED,
            'player_number': player_number,
            'timestamp': self._get_timestamp()
        }
    
    def game_start(self):
        """Notificar inicio del juego"""
        return {
            'type': self.MSG_GAME_START,
            'timestamp': self._get_timestamp()
        }
    
    def player_input(self, player_number, input_data):
        """Enviar input de jugador"""
        return {
            'type': self.MSG_PLAYER_INPUT,
            'player_number': player_number,
            'input': input_data,
            'timestamp': self._get_timestamp()
        }
    
    def game_state(self, game_state):
        """Enviar estado completo del juego"""
        return {
            'type': self.MSG_GAME_STATE,
            'state': self._serialize_game_state(game_state),
            'timestamp': self._get_timestamp()
        }
    
    def game_state_update(self, game_state):
        """Enviar actualización del estado del juego"""
        return {
            'type': self.MSG_GAME_STATE_UPDATE,
            'state': self._serialize_game_state(game_state),
            'timestamp': self._get_timestamp()
        }
    
    def game_over(self, winner, scores):
        """Notificar fin del juego"""
        return {
            'type': self.MSG_GAME_OVER,
            'winner': winner,
            'scores': scores,
            'timestamp': self._get_timestamp()
        }
    
    def player_disconnected(self, player_number):
        """Notificar que un jugador se desconectó"""
        return {
            'type': self.MSG_PLAYER_DISCONNECTED,
            'player_number': player_number,
            'timestamp': self._get_timestamp()
        }
    
    def error(self, error_message):
        """Enviar mensaje de error"""
        return {
            'type': self.MSG_ERROR,
            'message': error_message,
            'timestamp': self._get_timestamp()
        }
    
    def _serialize_game_state(self, game_state):
        """
        Serializar el estado del juego para transferencia de red
        Convierte objetos complejos en estructuras simples
        """
        if not game_state:
            return None
            
        serialized = {}
        
        # Estado básico del juego
        serialized['game_state'] = getattr(game_state, 'game_state', 'playing')
        serialized['game_mode'] = getattr(game_state, 'game_mode', 'multiplayer')
        serialized['countdown'] = getattr(game_state, 'countdown', 0)
        serialized['winner'] = getattr(game_state, 'winner', None)
        
        # Serializar serpientes
        serialized['snakes'] = {}
        if hasattr(game_state, 'snake') and game_state.snake:
            serialized['snakes'][1] = self._serialize_snake(game_state.snake)
        
        if hasattr(game_state, 'snake2') and game_state.snake2:
            serialized['snakes'][2] = self._serialize_snake(game_state.snake2)
        
        # Serializar fruta
        if hasattr(game_state, 'fruit') and game_state.fruit:
            serialized['fruit'] = {
                'pos': self._vector_to_dict(game_state.fruit.pos),
                'x': game_state.fruit.x,
                'y': game_state.fruit.y
            }
        
        # Serializar mina
        if hasattr(game_state, 'mine') and game_state.mine:
            serialized['mine'] = {
                'pos': self._vector_to_dict(game_state.mine.pos),
                'x': game_state.mine.x,
                'y': game_state.mine.y
            }
        
        # Puntuaciones
        serialized['scores'] = {}
        if hasattr(game_state, 'snake') and game_state.snake:
            serialized['scores'][1] = len(game_state.snake.body) - 3
        
        if hasattr(game_state, 'snake2') and game_state.snake2:
            serialized['scores'][2] = len(game_state.snake2.body) - 3
        
        # Información de jugadores
        serialized['players'] = {
            'p1_name': getattr(game_state, 'p1_name', 'Player 1'),
            'p2_name': getattr(game_state, 'p2_name', 'Player 2')
        }
        
        return serialized
    
    def _serialize_snake(self, snake):
        """Serializar una serpiente"""
        if not snake:
            return None
            
        return {
            'body': [self._vector_to_dict(pos) for pos in snake.body],
            'direction': self._vector_to_dict(snake.direction),
            'new_block': getattr(snake, 'new_block', False)
        }
    
    def _vector_to_dict(self, vector):
        """Convertir Vector2 a diccionario"""
        if hasattr(vector, 'x') and hasattr(vector, 'y'):
            return {'x': vector.x, 'y': vector.y}
        return vector
    
    def _dict_to_vector(self, vector_dict):
        """Convertir diccionario a Vector2"""
        if isinstance(vector_dict, dict) and 'x' in vector_dict and 'y' in vector_dict:
            return Vector2(vector_dict['x'], vector_dict['y'])
        return vector_dict
    
    def deserialize_game_state(self, serialized_state, game_instance=None):
        """
        Deserializar estado del juego recibido por red
        Convierte estructuras simples de nuevo en objetos del juego
        """
        if not serialized_state:
            return None
            
        # Si tenemos una instancia de juego, actualizarla
        if game_instance:
            self._update_game_instance(game_instance, serialized_state)
            return game_instance
        
        # Si no, crear un estado mínimo (para visualización)
        return serialized_state
    
    def _update_game_instance(self, game_instance, serialized_state):
        """Actualizar instancia del juego con datos serializados"""
        try:
            # Actualizar estado básico
            game_instance.game_state = serialized_state.get('game_state', 'playing')
            game_instance.countdown = serialized_state.get('countdown', 0)
            game_instance.winner = serialized_state.get('winner', None)
            
            # Actualizar serpientes
            snakes_data = serialized_state.get('snakes', {})
            
            # Serpiente 1
            if 1 in snakes_data and hasattr(game_instance, 'snake') and game_instance.snake:
                self._update_snake(game_instance.snake, snakes_data[1])
            
            # Serpiente 2
            if 2 in snakes_data and hasattr(game_instance, 'snake2') and game_instance.snake2:
                self._update_snake(game_instance.snake2, snakes_data[2])
            
            # Actualizar fruta
            fruit_data = serialized_state.get('fruit')
            if fruit_data and hasattr(game_instance, 'fruit') and game_instance.fruit:
                game_instance.fruit.pos = self._dict_to_vector(fruit_data['pos'])
                game_instance.fruit.x = fruit_data['x']
                game_instance.fruit.y = fruit_data['y']
            
            # Actualizar mina
            mine_data = serialized_state.get('mine')
            if mine_data and hasattr(game_instance, 'mine') and game_instance.mine:
                game_instance.mine.pos = self._dict_to_vector(mine_data['pos'])
                game_instance.mine.x = mine_data['x']
                game_instance.mine.y = mine_data['y']
                
        except Exception as e:
            print(f"❌ Error actualizando instancia del juego: {e}")
    
    def _update_snake(self, snake, snake_data):
        """Actualizar una serpiente con datos serializados"""
        if not snake_data:
            return
            
        try:
            # Actualizar cuerpo
            if 'body' in snake_data and snake_data['body']:
                snake.body = [self._dict_to_vector(pos) for pos in snake_data['body']]
            
            # Actualizar dirección
            if 'direction' in snake_data and snake_data['direction']:
                direction = self._dict_to_vector(snake_data['direction'])
                snake.direction = direction
            
            # Actualizar estado de nuevo bloque
            if 'new_block' in snake_data:
                snake.new_block = snake_data['new_block']
                
        except Exception as e:
            print(f"❌ Error actualizando serpiente: {e}")
    
    def _get_timestamp(self):
        """Obtener timestamp actual"""
        return datetime.now().isoformat()
    
    def validate_message(self, message):
        """Validar estructura del mensaje"""
        required_fields = ['type', 'timestamp']
        
        if not isinstance(message, dict):
            return False
        
        for field in required_fields:
            if field not in message:
                return False
        
        return True
    
    def process_network_messages(self, game_instance):
        """Procesar mensajes de red para una instancia de juego"""
        if not hasattr(game_instance, 'client') or not game_instance.client:
            return
            
        messages = game_instance.client.get_messages()
        for message in messages:
            self._process_single_message(game_instance, message)
    
    def _process_single_message(self, game_instance, message):
        """Procesar un solo mensaje de red"""
        msg_type = message.get('type')
        
        if msg_type == self.MSG_PLAYER_INPUT:
            # Aplicar input de jugador remoto
            player_num = message['player_number']
            input_data = message['input']
            self._apply_remote_input(game_instance, player_num, input_data)
            
        elif msg_type == self.MSG_GAME_STATE_UPDATE:
            # Actualizar estado del juego desde el host
            if not getattr(game_instance, 'is_host', True):  # Los clientes reciben el estado
                self.deserialize_game_state(message['state'], game_instance)
                
        elif msg_type == self.MSG_GAME_START:
            # Iniciar juego
            if hasattr(game_instance, 'start_countdown'):
                game_instance.start_countdown()
                
        elif msg_type == self.MSG_GAME_OVER:
            # Fin del juego
            game_instance.game_state = 'game_over'
            game_instance.winner = message['winner']
    
    def _apply_remote_input(self, game_instance, player_number, input_data):
        """Aplicar input de jugador remoto"""
        try:
            # Determinar qué serpiente controla el jugador remoto
            if player_number == 1:
                snake = game_instance.snake
            else:
                snake = game_instance.snake2
            
            if not snake:
                return
                
            # Aplicar dirección según input
            if input_data == 'up' and snake.direction.y != 1:
                snake.direction = Vector2(0, -1)
            elif input_data == 'down' and snake.direction.y != -1:
                snake.direction = Vector2(0, 1)
            elif input_data == 'right' and snake.direction.x != -1:
                snake.direction = Vector2(1, 0)
            elif input_data == 'left' and snake.direction.x != 1:
                snake.direction = Vector2(-1, 0)
                
        except Exception as e:
            print(f"❌ Error aplicando input remoto: {e}")