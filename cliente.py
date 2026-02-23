import socket, json, threading, time, sys

class PongClient:
    def __init__(self, server_host='localhost', server_port=5555):
        self.server_address = (server_host, server_port)
        self.sock = None
        self.connected = False
        self.my_side = None          # 'esquerdo' ou 'direito'
        self.player_number = None    # 1 ou 2
        self.game_state = {
            'ball': {'x': 80, 'y': 60, 'frozen': True},
            'paddles': {'esquerdo': 50, 'direito': 50},
            'scores': {'esquerdo': 0, 'direito': 0},
            'winner': None
        }
        self.last_received = 0
        self.running = False
        self.receive_thread = None
        self.last_send_time = 0
        self.HEARTBEAT_INTERVAL = 1.5   # segundos

    """funcao para conectar ao servidor"""
    def connect(self, player_name="Jogador"):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(3.0)  # timeout maior so na conexao inicial

            msg = {"type": "connect", "name": player_name}
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)

            data, _ = self.sock.recvfrom(1024)
            resp = json.loads(data.decode())

            if resp.get('type') != 'connection_accepted':
                print("Servidor rejeitou conexão:", resp)
                return False

            self.my_side = resp['side']
            self.player_number = resp.get('player_number')
            self.connected = True
            self.running = True
            self.last_received = time.time()

            # timeout baixo para loop de receive
            self.sock.settimeout(0.15)

            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()

            print(f"Conectado! Você é o jogador {self.player_number} → lado {self.my_side}")
            return True

        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    """funcao para desconectar do servidor"""
    def disconnect(self):
        if not self.connected:
            return
        try:
            msg = {"type": "disconnect"}
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)
        except:
            pass
        finally:
            self.running = False
            self.connected = False
            if self.sock:
                self.sock.close()
            print("Desconectado do servidor.")

    """funcao para receber mensagens do servidor em loop"""
    def _receive_loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(4096)
                msg = json.loads(data.decode())
                self.last_received = time.time()

                if msg['type'] == 'game_state':
                    self.game_state = msg
                elif msg['type'] == 'player_disconnected':
                    print("O outro jogador desconectou.")
                elif msg['type'] == 'connection_lost':
                    print("Servidor considera você desconectado.")
                    self.running = False

            except socket.timeout:
                continue
            except json.JSONDecodeError:
                continue
            except Exception as e:
                if self.running:
                    print(f"Erro na thread de receive: {e}")
                break

    """funcao para verificar se a conexao do cliente ainda esta ativa"""
    def is_alive(self):
        """Verifica se a conexão ainda está ativa (timeout de ~5s)"""
        if not self.connected:
            return False
        return (time.time() - self.last_received) < 5.0

    """funcao para enviar a posicao da raquete para o servidor"""
    def send_paddle_position(self, y):
        if not self.connected or not self.is_alive():
            return

        now = time.time()
        if now - self.last_send_time < 0.033:  # ~30 envios/seg
            return

        self.last_send_time = now
        try:
            msg = {"type": "paddle_update", "y": int(y)}
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)
        except:
            pass

    """funcao para enviar o ping para o servidor"""
    def send_heartbeat(self):
        if not self.connected or not self.is_alive():
            return
        try:
            msg = {"type": "ping", "t": time.time()}
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)
        except:
            pass
    """funcao para enviar pedido de restart para o servidor"""
    def send_restart_request(self):
        if not self.connected:
            return
        try:
            msg = {"type": "restart"}
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)
        except:
            pass

    # Getters convenientes
    def get_ball(self):      return self.game_state.get('ball', {})
    def get_paddles(self):   return self.game_state.get('paddles', {})
    def get_scores(self):    return self.game_state.get('scores', {})
    def get_winner(self):    return self.game_state.get('winner')
    def get_my_paddle_y(self): return self.get_paddles().get(self.my_side, 50)
    def is_waiting(self):    return self.game_state.get('ball', {}).get('frozen', True) and all(v == 0 for v in self.get_scores().values())