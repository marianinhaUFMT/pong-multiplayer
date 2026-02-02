import pyxel, sys, time
from cliente import PongClient

class Game:
    def __init__(self):
        ip = input("IP do servidor: ").strip() or "localhost"
        pyxel.init(160, 120, title="Pong Online")
        self.client = PongClient(ip, 5555)
        self.local_paddle_y = 50
        if not self.client.connect(): sys.exit()
        pyxel.run(self.update, self.draw)

    def draw_text_centered(self, y, text, color):
        x = (pyxel.width - len(text) * 4) // 2
        pyxel.text(x, y, text, color)

    def update(self):
        if not self.client.is_alive(): return
        dy = (pyxel.btn(pyxel.KEY_S) - pyxel.btn(pyxel.KEY_W)) * 2.5
        self.local_paddle_y = max(0, min(104, self.local_paddle_y + dy))
        self.client.send_paddle_position(self.local_paddle_y)
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

        # 3. Bola (so aparece se nao estiver em "Contagem de Inicio")
        if not ball.get('frozen') or (ball.get('frozen') and not ball.get('is_starting')):
            pyxel.circ(ball.get('x', 80), ball.get('y', 60), 2, 7)

        # 4. Interface de Mensagens
        now = time.time()
        
        # Caso de Desconexao (Prioridade maxima por 5 segundos)
        if disc_info and (now - disc_info['time'] < 5.0):
            pyxel.rect(10, 50, 140, 25, 0)
            side = disc_info['side'].upper()
            self.draw_text_centered(55, f"JOGADOR {side} DESCONECTADO", 8)
        
        # Caso de Vitoria
        elif winner:
            self.draw_text_centered(45, f"VITORIA: {winner.upper()}", pyxel.frame_count % 16)

            if my_side in votes:
                self.draw_text_centered(80, "AGUARDANDO OPONENTE...", 7)
            else:
                self.draw_text_centered(65, "SPACE PARA REINICIAR", 7)

        
        # Caso de Aguardando Oponente
        elif not state.get('game_started'):
            self.draw_text_centered(55, "AGUARDANDO OPONENTE...", pyxel.frame_count % 16)
            self.draw_text_centered(110, f"VOCE E LADO: {self.client.my_side.upper()}", 13)

        # Contagem Regressiva (Apenas no inicio ou reinicio)
        elif ball.get('frozen') and ball.get('is_starting'):
            seconds = (ball['freeze_timer'] // 60) + 1
            pyxel.circb(80, 60, 12, 7)
            pyxel.text(79, 58, str(seconds), 7)
            self.draw_text_centered(78, "PREPARE-SE", 6)

if __name__ == "__main__":
    Game()