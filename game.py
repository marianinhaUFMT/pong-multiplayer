import pyxel, sys, time
from cliente import PongClient

class Game:
    def __init__(self):
        ip = input("IP do servidor: ").strip() or "localhost"
        pyxel.init(160, 120, title="Pong Online")
        
        try:
            pyxel.load("game.pyxres")
        except:
            print("Erro: Arquivo game.pyxres não encontrado!")

        self.client = PongClient(ip, 5555)
        self.local_paddle_y = 50
        self.music_started = False
        
        # Variáveis para controle de som reativo
        self.last_score = {"esquerdo": 0, "direito": 0}
        self.last_ball_dx = 0 # Para detectar colisão pela mudança de direção

        if not self.client.connect(): sys.exit()
        pyxel.run(self.update, self.draw)

    def start_music(self):
        if not self.music_started:
            # Canal 1: Bateria (Som 4), Canal 2: Harmonia (Som 5)
            pyxel.play(1, 4, loop=True)
            pyxel.play(2, 5, loop=True)
            self.music_started = True

    def draw_text_centered(self, y, text, color):
        x = (pyxel.width - len(text) * 4) // 2
        pyxel.text(x, y, text, color)

    def update(self):
        if not self.client.is_alive(): return
        
        # Inicia a música assim que o jogo começar
        if self.client.game_state.get('game_started'):
            self.start_music()

        dy = (pyxel.btn(pyxel.KEY_S) - pyxel.btn(pyxel.KEY_W)) * 2.5
        self.local_paddle_y = max(0, min(104, self.local_paddle_y + dy))
        self.client.send_paddle_position(self.local_paddle_y)
        
        # --- LÓGICA DE SONS DE EVENTO ---
        state = self.client.game_state
        scores = state.get('scores', {"esquerdo": 0, "direito": 0})
        ball = state.get('ball', {})
        
        # 1. Som de Pontuação (Score)
        if scores.get('esquerdo') != self.last_score['esquerdo'] or \
           scores.get('direito') != self.last_score['direito']:
            pyxel.play(0, 0) # Som 0: Score
            self.last_score = scores.copy()

        # 2. Som de Rebatida (Hit)
        # Detectamos a rebatida quando a velocidade X da bola inverte
        current_dx = ball.get('dx', 0)
        if self.last_ball_dx != 0 and current_dx != 0:
            if (self.last_ball_dx > 0 and current_dx < 0) or \
               (self.last_ball_dx < 0 and current_dx > 0):
                # Só toca o hit se não for um reset de bola (bola no centro)
                if ball.get('x', 80) < 30 or ball.get('x', 80) > 130:
                    pyxel.play(0, 2) # Som 2: Hit
        self.last_ball_dx = current_dx

        if self.client.get_winner() and pyxel.btnp(pyxel.KEY_SPACE):
            self.client.send_restart_request()

    def draw(self):
        pyxel.cls(0)
        state = self.client.game_state
        ball = state.get('ball', {})
        winner = state.get('winner')
        votes = state.get('restart_votes', [])
        my_side = self.client.my_side
        disc_info = state.get('disconnected_info')

        # 1. Campo e Placar
        pyxel.line(80, 0, 80, 120, 13)
        scores = state.get('scores', {})
        pyxel.text(60, 8, str(scores.get('esquerdo', 0)), 12)
        pyxel.text(95, 8, str(scores.get('direito', 0)), 8)

        # 2. Raquetes
        paddles = state.get('paddles', {})
        pyxel.rect(3, paddles.get('esquerdo', 50), 4, 16, 12)
        pyxel.rect(153, paddles.get('direito', 50), 4, 16, 8)

        # 3. Bola
        if not ball.get('frozen') or (ball.get('frozen') and not ball.get('is_starting')):
            pyxel.circ(ball.get('x', 80), ball.get('y', 60), 2, 7)

        # 4. Interface de Mensagens
        now = time.time()
        
        if disc_info and (now - disc_info['time'] < 5.0):
            pyxel.rect(10, 50, 140, 25, 0)
            side = disc_info['side'].upper()
            self.draw_text_centered(55, f"JOGADOR {side} DESCONECTADO", 8)
        
        elif winner:
            self.draw_text_centered(45, f"VITORIA: {winner.upper()}", pyxel.frame_count % 16)
            if my_side in votes:
                self.draw_text_centered(80, "AGUARDANDO OPONENTE...", 7)
            else:
                self.draw_text_centered(65, "SPACE PARA REINICIAR", 7)
        
        elif not state.get('game_started'):
            self.draw_text_centered(55, "AGUARDANDO OPONENTE...", pyxel.frame_count % 16)
            self.draw_text_centered(110, f"VOCE E LADO: {self.client.my_side.upper()}", 13)

        elif ball.get('frozen') and ball.get('is_starting'):
            seconds = (ball['freeze_timer'] // 60) + 1
            pyxel.circb(80, 60, 12, 7)
            pyxel.text(79, 58, str(seconds), 7)
            self.draw_text_centered(78, "PREPARE-SE", 6)

if __name__ == "__main__":
    Game()