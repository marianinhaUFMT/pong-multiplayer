import socket
import json
import threading
import time

class PongClient:
    def __init__(self, server_host='localhost', server_port=5555):
        self.server_address = (server_host, server_port)
        
        # TODO: Inicializar socket UDP
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.settimeout(0.1)  # timeout para não bloquear
        
        # Estado local
        self.connected = False
        self.my_side = None  # 'left' ou 'right'
        self.player_number = None  # 1 ou 2
        self.waiting_for_player = False
        
        # Estado do jogo recebido do servidor
        self.game_state = {
            'ball': {'x': 80, 'y': 60, 'dx': 2, 'dy': 2, 'frozen': True},
            'paddles': {'left': 50, 'right': 50},
            'scores': {'left': 0, 'right': 0},
            'winner': None
        }
        
        # Thread para receber mensagens
        self.running = False
        self.receive_thread = None
    
    def connect(self, player_name="Player"):
        """Conecta ao servidor"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(2.0) # Timeout inicial para a conexão
            
            # Envia pedido de conexão (estilo INSERE do seu exemplo)
            msg = {"type": "connect", "player_name": player_name}
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)
            
            # Aguarda confirmação
            data, addr = self.sock.recvfrom(1024)
            message = json.loads(data.decode())
            
            if message['type'] == 'connection_accepted':
                self.my_side = message['side']
                self.player_number = message['player_number']
                self.connected = True
                self.running = True
                
                # Inicia thread para escutar o servidor continuamente
                self.sock.settimeout(0.1) # Timeout baixo para a thread não travar
                self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
                self.receive_thread.start()
                return True
        except Exception as e:
            print(f"Falha ao conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do servidor"""
        if self.connected:
            try:
                msg = {"type": "disconnect"}
                self.sock.sendto(json.dumps(msg).encode(), self.server_address)
            except:
                pass
            self.running = False
            self.connected = False
            self.sock.close()
    
    def send_paddle_position(self, y_position):
        """Envia posição da raquete para o servidor"""
        if not self.connected: return
        
        try:
            msg = {
                "type": "paddle_update",
                "y": y_position
            }
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)
        except Exception as e:
            print(f"Erro ao enviar posição: {e}")
    
    def send_ping(self):
        """Envia ping para manter conexão ativa"""
        if not self.connected:
            return
        
        try:
            # Cria a mensagem simples de ping seguindo o teu protocolo JSON
            msg = {
                "type": "ping",
                "timestamp": time.time() # Opcional: útil para medir latência (lag)
            }
            # Envia para o endereço do servidor configurado no __init__
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)
        except Exception as e:
            print(f"Erro ao enviar ping: {e}")
    
    def receive_messages(self):
        """Thread que recebe mensagens do servidor continuamente"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                message = json.loads(data.decode())
                
                if message['type'] == 'game_state':
                    self.game_state = message
                    self.waiting_for_player = False
                elif message['type'] == 'player_disconnected':
                    self.waiting_for_player = True
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Erro no recebimento: {e}")
                break
    
    def get_my_paddle_y(self):
        return self.game_state['paddles'].get(self.my_side, 50)

    def get_opponent_paddle_y(self):
        opp_side = 'right' if self.my_side == 'left' else 'left'
        return self.game_state['paddles'].get(opp_side, 50)
    
    def get_ball_state(self):
        """Retorna estado completo da bola"""
        # TODO: Retornar dicionário com x, y, dx, dy, frozen
        return self.game_state['ball']
    
    def get_scores(self):
        """Retorna placar (score_left, score_right)"""
        # TODO: Retornar tupla com placar
        scores = self.game_state['scores']
        return (scores['left'], scores['right'])
    
    def get_winner(self):
        """Retorna vencedor ou None"""
        # TODO: Retornar 'left', 'right' ou None
        return self.game_state['winner']
    
    def is_waiting_for_player(self):
        """Verifica se está aguardando outro jogador"""
        return self.waiting_for_player
    
    def get_my_side(self):
        """Retorna lado do jogador ('left' ou 'right')"""
        return self.my_side

# TODO: Integração com game.py:
# 
# No início de game.py, importar:
# from cliente import PongClient
#
# Criar instância do cliente:
# client = PongClient('localhost', 5555)
#
# No menu, quando escolher jogar online:
# if client.connect():
#     # Conectado com sucesso
#     if client.is_waiting_for_player():
#         # Mostrar tela de aguardo
#     else:
#         # Iniciar jogo
#
# No loop de update():
# # Enviar posição da própria raquete
# if client.get_my_side() == 'left':
#     client.send_paddle_position(p1_y)
# else:
#     client.send_paddle_position(p2_y)
#
# # Receber posição do oponente
# if client.get_my_side() == 'left':
#     p2_y = client.get_opponent_paddle_y()
# else:
#     p1_y = client.get_opponent_paddle_y()
#
# # Receber estado da bola
# ball_state = client.get_ball_state()
# ball_x = ball_state['x']
# ball_y = ball_state['y']
# ball_dx = ball_state['dx']
# ball_dy = ball_state['dy']
#
# # Receber placar
# score1, score2 = client.get_scores()

# TODO: Tratamento de erros e reconexão:
# - Detectar timeout de conexão (servidor não responde)
# - Tentar reconectar automaticamente
# - Mostrar mensagem de erro ao usuário
# - Opção de voltar ao menu se conexão falhar

# TODO: Otimizações:
# - Interpolação de posições para suavizar movimento
# - Predição de movimento para compensar latência
# - Compressão de mensagens se necessário
# - Rate limiting de envio de posições

if __name__ == "__main__":
    # TODO: Teste do cliente
    # client = PongClient('localhost', 5555)
    # if client.connect():
    #     print("Conectado!")
    #     # Simular envio de posições
    # else:
    #     print("Falha na conexão")
    print("Cliente Pong UDP")
    print("TODO: Implementar cliente completo")