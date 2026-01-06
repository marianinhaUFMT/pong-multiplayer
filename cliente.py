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
        # TODO: Implementar conexão
        # - Criar mensagem JSON do tipo "connect"
        # - Enviar para o servidor
        # - Aguardar resposta "connection_accepted" ou "waiting_player"
        # - Armazenar self.my_side e self.player_number
        # - Iniciar thread de recebimento
        # - Retornar True se sucesso, False se falha
        pass
    
    def disconnect(self):
        """Desconecta do servidor"""
        # TODO: Implementar desconexão
        # - Enviar mensagem "disconnect" ao servidor
        # - Parar thread de recebimento (self.running = False)
        # - Fechar socket
        pass
    
    def send_paddle_position(self, y_position):
        """Envia posição da raquete para o servidor"""
        # TODO: Implementar envio de posição
        # - Criar mensagem JSON do tipo "paddle_update"
        # - Incluir posição Y
        # - Enviar via UDP ao servidor
        # - Tratar erros de envio
        pass
    
    def send_ping(self):
        """Envia ping para manter conexão ativa"""
        # TODO: Implementar ping
        # - Criar mensagem JSON do tipo "ping"
        # - Enviar ao servidor
        # - Chamar periodicamente (a cada 1-2 segundos)
        pass
    
    def receive_messages(self):
        """Thread que recebe mensagens do servidor continuamente"""
        # TODO: Implementar recebimento de mensagens
        # while self.running:
        #     try:
        #         # Receber dados do socket
        #         data, addr = self.sock.recvfrom(1024)
        #         message = json.loads(data.decode())
        #         
        #         # Processar mensagem baseado no tipo
        #         if message['type'] == 'game_state':
        #             self.game_state = message
        #         elif message['type'] == 'waiting_player':
        #             self.waiting_for_player = True
        #         elif message['type'] == 'player_disconnected':
        #             # Tratar desconexão do oponente
        #             pass
        #     except socket.timeout:
        #         continue
        #     except Exception as e:
        #         print(f"Erro ao receber: {e}")
        pass
    
    def get_my_paddle_y(self):
        """Retorna posição Y da minha raquete"""
        # TODO: Retornar posição baseado no lado
        # if self.my_side == 'left':
        #     return self.game_state['paddles']['left']
        # else:
        #     return self.game_state['paddles']['right']
        return 50
    
    def get_opponent_paddle_y(self):
        """Retorna posição Y da raquete do oponente"""
        # TODO: Retornar posição baseado no lado oposto
        # if self.my_side == 'left':
        #     return self.game_state['paddles']['right']
        # else:
        #     return self.game_state['paddles']['left']
        return 50
    
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