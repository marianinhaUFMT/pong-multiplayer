import socket
import json
import time
import random

HOST = '0.0.0.0'
PORT = 5555
BUFFER_SIZE = 1024

class PongServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.sock.bind((HOST, PORT))
        except OSError:
            print(f"ERRO: Porta {PORT} ocupada. Use 'fuser -k {PORT}/udp'.")
            exit(1)
            
        self.sock.setblocking(False)
        
        self.players = {}  # {addr: {'side': 'left', 'y': 50}}
        self.ball = {'x': 80, 'y': 60, 'dx': 2, 'dy': 2, 'speed': 2, 'frozen': True, 'freeze_timer': 30}
        self.scores = {'left': 0, 'right': 0}
        self.winner = None
        self.game_started = False
        print(f"Servidor Pong Online iniciado em {HOST}:{PORT}")

    def reset_ball(self):
        """Lógica de reset vinda do seu código original"""
        self.ball.update({
            'x': 80,
            'y': 60,
            'speed': 2,
            'frozen': True,
            'freeze_timer': 30,
            'dx': 2 if random.choice([True, False]) else -2,
            'dy': random.uniform(-1.5, 1.5)
        })

    def reset_game(self):
        """Zera o placar e reinicia o estado"""
        self.scores = {'left': 0, 'right': 0}
        self.winner = None
        self.reset_ball()

    def handle_messages(self):
        try:
            while True:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                msg = json.loads(data.decode())
                
                if msg['type'] == 'connect':
                    if len(self.players) < 2 and addr not in self.players:
                        side = 'left' if len(self.players) == 0 else 'right'
                        self.players[addr] = {'side': side, 'y': 50}
                        resp = {"type": "connection_accepted", "side": side, "player_number": len(self.players)}
                        self.sock.sendto(json.dumps(resp).encode(), addr)
                        if len(self.players) == 2:
                            self.game_started = True
                            self.reset_ball()

                elif msg['type'] == 'paddle_update':
                    if addr in self.players:
                        self.players[addr]['y'] = max(0, min(msg.get('y', 50), 104))

                elif msg['type'] == 'restart':
                    if self.winner: # Só permite restart se alguém venceu
                        self.reset_game()

                elif msg['type'] == 'disconnect':
                    if addr in self.players:
                        del self.players[addr]
                        self.game_started = False
                        self.winner = None

        except BlockingIOError:
            pass

    def update_physics(self):
        if not self.game_started or self.winner:
            return

        if self.ball['frozen']:
            self.ball['freeze_timer'] -= 1
            if self.ball['freeze_timer'] <= 0:
                self.ball['frozen'] = False
            return

        # Movimentação
        self.ball['x'] += self.ball['dx']
        self.ball['y'] += self.ball['dy']

        # Rebote Teto/Chão
        if self.ball['y'] <= 0 or self.ball['y'] >= 120:
            self.ball['dy'] *= -1

        # Posições das raquetes para colisão
        p1_y = next((p['y'] for p in self.players.values() if p['side'] == 'left'), 50)
        p2_y = next((p['y'] for p in self.players.values() if p['side'] == 'right'), 50)

        # Colisão Raquete Esquerda (Lógica hit_pos do seu código)
        if 3 <= self.ball['x'] <= 7 and p1_y <= self.ball['y'] <= p1_y + 16:
            hit_pos = (self.ball['y'] - p1_y) / 16
            self.ball['dy'] = (hit_pos - 0.5) * 4
            self.ball['dx'] = abs(self.ball['dx']) + 0.1
            self.ball['x'] = 7

        # Colisão Raquete Direita
        if 153 <= self.ball['x'] <= 157 and p2_y <= self.ball['y'] <= p2_y + 16:
            hit_pos = (self.ball['y'] - p2_y) / 16
            self.ball['dy'] = (hit_pos - 0.5) * 4
            self.ball['dx'] = -(abs(self.ball['dx']) + 0.1)
            self.ball['x'] = 153

        # Pontuação até 10
        if self.ball['x'] < 0:
            self.scores['right'] += 1
            if self.scores['right'] >= 10: self.winner = "DIREITA"
            else: self.reset_ball()
        elif self.ball['x'] > 160:
            self.scores['left'] += 1
            if self.scores['left'] >= 10: self.winner = "ESQUERDA"
            else: self.reset_ball()

    def broadcast(self):
        if not self.players: return
        paddles = {p['side']: p['y'] for p in self.players.values()}
        state = {
            "type": "game_state",
            "ball": self.ball,
            "paddles": paddles,
            "scores": self.scores,
            "winner": self.winner
        }
        package = json.dumps(state).encode()
        for addr in self.players:
            self.sock.sendto(package, addr)

    def run(self):
        while True:
            self.handle_messages()
            self.update_physics()
            self.broadcast()
            time.sleep(1/60)

if __name__ == "__main__":
    server = PongServer()
    try:
        server.run()
    except KeyboardInterrupt:
        server.sock.close()