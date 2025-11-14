import socket
import threading
import pickle
import time
from src.services.protocol import GameProtocol

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.game_state = None
        self.running = False
        self.protocol = GameProtocol()
        
    def start_server(self):
        """Iniciar el servidor"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(2)  # Máximo 2 jugadores
            self.running = True
            
            print(f"🎮 Servidor iniciado en {self.host}:{self.port}")
            print("Esperando jugadores...")
            
            # Hilo para aceptar conexiones
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")
            return False
    
    def _accept_connections(self):
        """Aceptar conexiones de clientes"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"✅ Jugador conectado desde {address}")
                
                # Asignar número de jugador
                player_number = len(self.clients) + 1
                
                client_handler = ClientHandler(client_socket, address, player_number, self)
                self.clients.append(client_handler)
                
                # Iniciar hilo para el cliente
                client_thread = threading.Thread(target=client_handler.handle_client)
                client_thread.daemon = True
                client_thread.start()
                
                # Notificar a todos los clientes sobre el nuevo jugador
                self.broadcast(self.protocol.player_joined(player_number))
                
                # Si hay 2 jugadores, iniciar juego
                if len(self.clients) == 2:
                    print("🎯 2 jugadores conectados - Iniciando juego...")
                    self.broadcast(self.protocol.game_start())
                    
            except Exception as e:
                if self.running:
                    print(f"❌ Error aceptando conexión: {e}")
    
    def broadcast(self, data):
        """Enviar datos a todos los clientes"""
        for client in self.clients[:]:  # Copia de la lista para evitar problemas
            try:
                client.send(data)
            except:
                self.clients.remove(client)
    
    def update_game_state(self, game_state):
        """Actualizar estado del juego y enviar a clientes"""
        self.game_state = game_state
        if self.clients:
            self.broadcast(self.protocol.game_state_update(game_state))
    
    def handle_player_input(self, player_number, input_data):
        """Manejar input de jugador y broadcast"""
        self.broadcast(self.protocol.player_input(player_number, input_data))
    
    def stop_server(self):
        """Detener servidor"""
        self.running = False
        for client in self.clients:
            client.disconnect()
        if self.server_socket:
            self.server_socket.close()
        print("🛑 Servidor detenido")


class ClientHandler:
    def __init__(self, socket, address, player_number, server):
        self.socket = socket
        self.address = address
        self.player_number = player_number
        self.server = server
        self.running = True
    
    def handle_client(self):
        """Manejar comunicación con el cliente"""
        try:
            # Enviar número de jugador al cliente
            self.send(self.server.protocol.assign_player(self.player_number))
            
            while self.running:
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                # Procesar mensaje del cliente
                message = pickle.loads(data)
                self._process_message(message)
                
        except Exception as e:
            print(f"❌ Error con cliente {self.player_number}: {e}")
        finally:
            self.disconnect()
    
    def _process_message(self, message):
        """Procesar mensaje del cliente"""
        msg_type = message.get('type')
        
        if msg_type == 'player_input':
            # Reenviar input a todos los clientes
            self.server.handle_player_input(self.player_number, message['input'])
            
        elif msg_type == 'game_state':
            # Actualizar estado del juego en servidor
            self.server.update_game_state(message['state'])
    
    def send(self, data):
        """Enviar datos al cliente"""
        try:
            self.socket.send(pickle.dumps(data))
        except:
            self.disconnect()
    
    def disconnect(self):
        """Desconectar cliente"""
        self.running = False
        try:
            self.socket.close()
        except:
            pass
        
        if self in self.server.clients:
            self.server.clients.remove(self)
            print(f"👋 Jugador {self.player_number} desconectado")
            # Notificar a otros clientes
            self.server.broadcast(self.server.protocol.player_disconnected(self.player_number))


class GameClient:
    def __init__(self):
        self.socket = None
        self.server_address = None
        self.player_number = None
        self.connected = False
        self.running = False
        self.protocol = GameProtocol()
        self.message_queue = []  # Cola para almacenar mensajes recibidos
        
    def connect_to_server(self, host, port):
        """Conectar al servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # Timeout para conexión
            self.server_address = (host, port)
            self.socket.connect(self.server_address)
            self.socket.settimeout(None)  # Quitar timeout después de conectar
            self.connected = True
            self.running = True
            
            print(f"✅ Conectado al servidor {host}:{port}")
            
            # Hilo para recibir mensajes
            receive_thread = threading.Thread(target=self._receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
            
        except socket.timeout:
            print(f"❌ Timeout conectando al servidor {host}:{port}")
            return False
        except Exception as e:
            print(f"❌ Error conectando al servidor {host}:{port}: {e}")
            return False
    
    def _receive_messages(self):
        """Recibir mensajes del servidor"""
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                message = pickle.loads(data)
                self._handle_server_message(message)
                
            except socket.timeout:
                continue  # Timeout normal, continuar recibiendo
            except Exception as e:
                if self.running:
                    print(f"❌ Error recibiendo mensaje: {e}")
                break
        
        self.disconnect()
    
    def _handle_server_message(self, message):
        """Manejar mensaje del servidor"""
        msg_type = message.get('type')
        
        if msg_type == 'assign_player':
            self.player_number = message['player_number']
            print(f"🎮 Eres el Jugador {self.player_number}")
            
        elif msg_type == 'player_joined':
            print(f"👥 Jugador {message['player_number']} se unió")
            
        elif msg_type == 'game_start':
            print("🎯 ¡Juego iniciado!")
            
        elif msg_type == 'player_disconnected':
            print(f"👋 Jugador {message['player_number']} se desconectó")
            
        # Almacenar todos los mensajes en la cola para que el juego los procese
        self.message_queue.append(message)
    
    def get_messages(self):
        """Obtener todos los mensajes en cola y limpiar la cola"""
        messages = self.message_queue[:]
        self.message_queue.clear()
        return messages
    
    def send_input(self, input_data):
        """Enviar input al servidor"""
        if self.connected:
            message = self.protocol.player_input(self.player_number, input_data)
            self._send_message(message)
    
    def send_game_state(self, game_state):
        """Enviar estado del juego al servidor (solo host)"""
        if self.connected:
            message = self.protocol.game_state(game_state)
            self._send_message(message)
    
    def _send_message(self, message):
        """Enviar mensaje al servidor"""
        try:
            self.socket.send(pickle.dumps(message))
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            self.disconnect()
    
    def disconnect(self):
        """Desconectar del servidor"""
        self.running = False
        self.connected = False
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        print("👋 Desconectado del servidor")