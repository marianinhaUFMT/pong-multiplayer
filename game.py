import pyxel
from cliente import PongClient  # Importa o arquivo que você já tem

class Game:
    def __init__(self):
        # 1. Inicia o Pyxel
        pyxel.init(160, 120, title="Pong Online")
        
        # 2. Inicia o Cliente (Troque 'localhost' pelo IP do servidor na rede)
        self.client = PongClient('localhost', 5555)
        
        # 3. Variável local para controlar a raquete antes de enviar ao servidor
        self.y_local = 50
        
        # Tenta conectar imediatamente
        if not self.client.connect("Jogador"):
            print("Não foi possível conectar ao servidor.")
            # Aqui você poderia voltar para um menu, por enquanto vamos fechar
            # pyxel.quit() 

        # 4. Carrega sons/imagens se necessário
        #pyxel.load("game.pyxres")

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.client.disconnect()
            pyxel.quit()

        if not self.client.connected:
            return

        # MOVIMENTO LOCAL
        # O jogador só controla a raquete dele. O servidor decide qual lado ele é.
        if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP):
            self.y_local -= 2
        if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
            self.y_local += 2
        
        # Limites da tela
        self.y_local = max(0, min(self.y_local, 104))
        
        # ENVIA PARA O SERVIDOR
        self.client.send_paddle_position(self.y_local)

    def draw(self):
        pyxel.cls(0)
        
        state = self.client.game_state
        ball = state['ball']
        paddles = state['paddles']
        scores = state['scores']

        # TELA DE ESPERA
        # Se a bola estiver congelada e o jogo não começou, avisa o usuário
        if ball.get('frozen') and scores['left'] == 0 and scores['right'] == 0:
            pyxel.text(45, 50, "AGUARDANDO OPONENTE...", pyxel.frame_count % 16)
            pyxel.text(55, 70, f"VOCE E O LADO: {self.client.my_side}", 7)

        # TELA DE VITORIA
        winner = state['winner']
        if winner is not None:
            msg = f"PLAYER DA {winner} VENCEU!"
            x_pos = 80 - (len(msg) * 2)
            pyxel.text(x_pos, 50, msg, pyxel.frame_count % 16) 
            msg2 = "SPACE: Restart"
            x_pos2 = 80 - (len(msg2) * 2)
            pyxel.text(x_pos2, 70, msg2, 7)
            msg3 = "ESC: Quit"
            x_pos3 = 80 - (len(msg3) * 2)
            pyxel.text(x_pos3, 80, msg3, 7)
            return
        
        # Meio de campo
        pyxel.line(80, 0, 80, 120, 13)

        # Placar
        pyxel.text(60, 10, str(scores['left']), 12)
        pyxel.text(95, 10, str(scores['right']), 8)

        # Raquetes
        pyxel.rect(3, paddles.get('left', 50), 4, 16, 12)    # Azul
        pyxel.rect(153, paddles.get('right', 50), 4, 16, 8) # Vermelho

        # Bola
        pyxel.circ(ball['x'], ball['y'], 2, 7)

# Para rodar o jogo
if __name__ == "__main__":
    Game()