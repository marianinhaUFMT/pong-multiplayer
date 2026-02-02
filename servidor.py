import socket, json, time, random

HOST = '0.0.0.0'
PORT = 5555
BUFFER_SIZE = 1024

class PongServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try: 
            self.sock.bind((HOST, PORT))
            print(f'Servidor Pong iniciado em {HOST}:{PORT}')
        except OSError as e:
            print(f"Erro ao iniciar servidor: {e}")
            exit(1)
        self.sock.setblocking(False)
        
        self.players = {} 
        self.ball = {'x': 80, 'y': 60, 'dx': 0, 'dy': 0, 'frozen': True, 'freeze_timer': 0, 'is_starting': False}
        self.scores = {'esquerdo': 0, 'direito': 0}
        self.winner = None
        self.game_started = False
        self.disconnected_info = None 
        self.restart_votes = set()

    def reset_ball(self, countdown_seconds=3, is_starting=False):
        self.ball.update({
            'x': 80, 'y': 60,
            'frozen': True,
            'freeze_timer': countdown_seconds * 60,
            'is_starting': is_starting,
            'dx': 2.0 * (1 if random.random() > 0.5 else -1),
            'dy': random.uniform(-1.2, 1.2)
        })

    def handle_messages(self):
        try:
            while True:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                msg = json.loads(data.decode())
                
                if msg['type'] == 'connect':
                    if len(self.players) < 2 and addr not in self.players:
                        # Lógica para definir lado e número do jogador
                        player_count = len(self.players) + 1
                        side = 'esquerdo' if player_count == 1 else 'direito'
                        
                        self.players[addr] = {'side': side, 'y': 50, 'last_seen': time.time()}
                        
                        # ENVIA O NÚMERO DO JOGADOR AQUI
                        resp = {
                            "type": "connection_accepted", 
                            "side": side, 
                            "player_number": player_count
                        }
                        self.sock.sendto(json.dumps(resp).encode(), addr)
                        
                        if len(self.players) == 2:
                            self.game_started = True
                            self.disconnected_info = None
                            self.reset_ball(3, is_starting=True)

                elif msg['type'] == 'paddle_update' and addr in self.players:
                    self.players[addr]['y'] = msg.get('y', 50)
                    self.players[addr]['last_seen'] = time.time()

                elif msg['type'] == 'ping' and addr in self.players:
                    self.players[addr]['last_seen'] = time.time()

                elif msg['type'] == 'restart' and self.winner:
                    if addr in self.players:
                        self.restart_votes.add(addr)
                    if len(self.restart_votes) >= len(self.players) and len(self.players) == 2:
                        self.scores = {'esquerdo': 0, 'direito': 0}
                        self.winner = None
                        self.restart_votes.clear()
                        self.reset_ball(3, is_starting=True)

                elif msg['type'] == 'disconnect' and addr in self.players:
                    self._handle_disconnect(self.players[addr]['side'])
                    if addr in self.restart_votes:
                        self.restart_votes.remove(addr)
                    del self.players[addr]
        except (BlockingIOError, json.JSONDecodeError): pass

    def _handle_disconnect(self, side):
        print(f"Jogador {side} desconectado.")
        self.disconnected_info = {'side': side, 'time': time.time()}
        self.game_started = False
        self.winner = None
        self.ball['frozen'] = True
        self.scores = {'esquerdo': 0, 'direito': 0}
        self.restart_votes.clear() # se alguem sai

    def check_timeouts(self):
        now = time.time()
        to_delete = [addr for addr, p in self.players.items() if now - p['last_seen'] > 5.0]
        for addr in to_delete:
            self._handle_disconnect(self.players[addr]['side'])
            del self.players[addr]

    def update_physics(self):
        if not self.game_started or self.winner: return

        if self.ball['frozen']:
            if self.ball['freeze_timer'] > 0:
                self.ball['freeze_timer'] -= 1
            if self.ball['freeze_timer'] <= 0 and len(self.players) == 2:
                self.ball['frozen'] = False
                self.ball['is_starting'] = False
            return

        self.ball['x'] += self.ball['dx']
        self.ball['y'] += self.ball['dy']
        if self.ball['y'] <= 2 or self.ball['y'] >= 118: self.ball['dy'] *= -1

        paddles = {p['side']: p['y'] for p in self.players.values()}
        if 3 <= self.ball['x'] <= 7 and paddles.get('esquerdo', 50) <= self.ball['y'] <= paddles.get('esquerdo', 50) + 16:
            self.ball['dx'] = abs(self.ball['dx']) + 0.1
            self.ball['x'] = 8
        elif 153 <= self.ball['x'] <= 157 and paddles.get('direito', 50) <= self.ball['y'] <= paddles.get('direito', 50) + 16:
            self.ball['dx'] = -(abs(self.ball['dx']) + 0.1)
            self.ball['x'] = 152

        if self.ball['x'] < 0:
            self.scores['direito'] += 1
            if self.scores['direito'] >= 10: self.winner = "direito"
            else: self.reset_ball(1, is_starting=False)
        elif self.ball['x'] > 160:
            self.scores['esquerdo'] += 1
            if self.scores['esquerdo'] >= 10: self.winner = "esquerdo"
            else: self.reset_ball(1, is_starting=False)

    def broadcast(self):
        if not self.players: return

        voted_sides = [self.players[addr]['side'] for addr in self.restart_votes if addr in self.players]
        state = {
            "type": "game_state", "ball": self.ball, 
            "paddles": {p['side']: p['y'] for p in self.players.values()},
            "scores": self.scores, "winner": self.winner, "game_started": self.game_started,
            "disconnected_info": self.disconnected_info,
            "restart_votes": voted_sides
        }
        package = json.dumps(state).encode()
        for addr in self.players:
            try: self.sock.sendto(package, addr)
            except: pass

    def run(self):
        print("Aguardando conexões...")
        try:
            while True:
                self.handle_messages()
                self.check_timeouts()
                self.update_physics()
                self.broadcast()
                time.sleep(1/60)
        except KeyboardInterrupt:
            self.sock.close()
            print("\nServidor desligado.")

if __name__ == "__main__":
    PongServer().run()