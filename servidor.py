import socket
import json
import time
import random

# Configurações do servidor
HOST = '0.0.0.0'  # Escuta em todas as interfaces
PORT = 5555
BUFFER_SIZE = 1024

class PongServer:
    def __init__(self):
        # TODO: Inicializar socket UDP
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.bind((HOST, PORT))
        
        # Estado do jogo
        self.players = {}  # {addr: {'side': 'left'/'right', 'y': 50}}
        self.ball = {
            'x': 80,
            'y': 60,
            'dx': 2,
            'dy': 2,
            'speed': 2,
            'frozen': True,
            'freeze_timer': 30
        }
        self.scores = {'left': 0, 'right': 0}
        self.game_started = False
        
        print(f"Servidor iniciado em {HOST}:{PORT}")
    
    def reset_ball(self):
        """Reseta a bola para o centro com direção aleatória"""
        # TODO: Implementar reset da bola
        # - Posicionar no centro (80, 60)
        # - Direção horizontal aleatória (esquerda ou direita)
        # - Ângulo vertical aleatório
        # - Resetar velocidade para 2
        # - Congelar por 30 frames
        pass
    
    def handle_player_connection(self, addr, data):
        """Gerencia conexão de novo jogador"""
        # TODO: Implementar lógica de conexão
        # - Verificar se já existem 2 jogadores conectados
        # - Atribuir lado (left/right) ao jogador
        # - Adicionar jogador ao dicionário self.players
        # - Enviar confirmação com o lado atribuído
        # - Se 2 jogadores conectados, iniciar jogo (self.game_started = True)
        pass
    
    def handle_paddle_update(self, addr, data):
        """Atualiza posição da raquete do jogador"""
        # TODO: Implementar atualização de raquete
        # - Verificar se o endereço está em self.players
        # - Atualizar posição Y da raquete do jogador
        # - Validar limites (0 <= y <= 104)
        pass
    
    def update_ball_physics(self):
        """Atualiza física da bola (colisões, movimento)"""
        # TODO: Implementar física da bola
        # - Gerenciar timer de congelamento
        # - Atualizar posição (x += dx, y += dy)
        # - Detectar colisão com paredes superior/inferior
        # - Detectar colisão com raquetes (calcular ângulo baseado na posição de impacto)
        # - Aumentar velocidade gradualmente a cada colisão
        # - Detectar pontos (bola sai pelas laterais)
        # - Atualizar placar
        # - Resetar bola após ponto
        pass
    
    def broadcast_game_state(self):
        """Envia estado do jogo para todos os jogadores"""
        # TODO: Implementar broadcast
        # - Criar dicionário com estado completo:
        #   * Posições das raquetes (left_y, right_y)
        #   * Posição e velocidade da bola
        #   * Placar (score_left, score_right)
        #   * Status do jogo (started, frozen, winner)
        # - Serializar para JSON
        # - Enviar via UDP para todos os endereços em self.players
        pass
    
    def handle_disconnection(self, addr):
        """Gerencia desconexão de jogador"""
        # TODO: Implementar desconexão
        # - Remover jogador de self.players
        # - Notificar outro jogador (se houver)
        # - Pausar/resetar jogo se necessário
        # - Aguardar reconexão ou novo jogador
        pass
    
    def run(self):
        """Loop principal do servidor"""
        # TODO: Implementar loop principal
        # while True:
        #     # Receber mensagens dos clientes (non-blocking ou com timeout)
        #     # Processar mensagens (conexão, movimento, ping)
        #     # Atualizar física do jogo se game_started
        #     # Broadcast do estado para todos os jogadores
        #     # Controlar taxa de atualização (~60 FPS)
        #     time.sleep(1/60)
        pass

# TODO: Protocolo de comunicação (formato das mensagens JSON):
# 
# Cliente -> Servidor:
# {
#     "type": "connect",
#     "player_name": "Player1"  # opcional
# }
# {
#     "type": "paddle_update",
#     "y": 50
# }
# {
#     "type": "ping"  # para manter conexão ativa
# }
# {
#     "type": "disconnect"
# }
#
# Servidor -> Cliente:
# {
#     "type": "connection_accepted",
#     "side": "left",  # ou "right"
#     "player_number": 1  # ou 2
# }
# {
#     "type": "waiting_player",
#     "waiting_for": 2  # número do jogador que falta
# }
# {
#     "type": "game_state",
#     "ball": {"x": 80, "y": 60, "dx": 2, "dy": 2, "frozen": false},
#     "paddles": {"left": 50, "right": 50},
#     "scores": {"left": 0, "right": 0},
#     "winner": null  # ou "left"/"right"
# }
# {
#     "type": "player_disconnected",
#     "side": "right"
# }

if __name__ == "__main__":
    # TODO: Criar instância do servidor e executar
    # server = PongServer()
    # server.run()
    print("Servidor Pong UDP")
    print("TODO: Implementar servidor completo")