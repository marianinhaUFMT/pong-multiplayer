import pyxel 
from pyxel import *
import random

init(160, 120, title="Pong Online")
load("game.pyxres")

# TODO: Implementar tela inicial com:
# - Logo/título do jogo
# - Opção "Jogar Local" (2 jogadores no mesmo computador)
# - Opção "Jogar Online" (conectar ao servidor)
# - Opção "Criar Sala" (hospedar servidor)
# - Opção "Configurações" (volume, controles, etc)
# - Opção "Sair"

# TODO: Implementar tela de aguardo quando conectado mas oponente não:
# - Mostrar "Aguardando jogador 1..." ou "Aguardando jogador 2..."
# - Animação de carregamento/piscando
# - Opção de cancelar e voltar ao menu
# - Mostrar seu lado (esquerda/direita)

# TODO: Integração com cliente.py:
# - Importar classe Client de cliente.py
# - Enviar posição da raquete a cada frame
# - Receber posição da raquete do oponente
# - Receber estado da bola (posição, velocidade)
# - Receber placar atualizado
# - Tratar desconexão do oponente

# variaveis globais do jogo
p1_y = 50
p2_y = 50
ball_x = 80
ball_y = 60
ball_dx = 2
ball_dy = 2
ball_speed = 2  # velocidade base
score1 = 0
score2 = 0
music_playing = False
winner = None
ball_frozen = True  # bola começa parada
freeze_timer = 30  # 0.5 segundo (30 frames)

# funcoes auxiliares
def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy, ball_speed, ball_frozen, freeze_timer
    ball_x = 80
    ball_y = 60
    ball_speed = 2  # reseta velocidade
    
    # direcao aleatoia (esquerda ou direita)
    ball_dx = ball_speed if random.choice([True, False]) else -ball_speed
    # ângulo vertical aleatório
    ball_dy = random.uniform(-1.5, 1.5)
    
    # congela a bola por 1 segundo
    ball_frozen = True
    freeze_timer = 30
    
    play(0, 0)

def reset_game():
    global score1, score2, winner, p1_y, p2_y
    score1 = 0
    score2 = 0
    winner = None
    p1_y = 50
    p2_y = 50
    reset_ball()

# loop principal
def update():
    global p1_y, p2_y, ball_x, ball_y, ball_dx, ball_dy, ball_speed
    global score1, score2, winner, music_playing, ball_frozen, freeze_timer

    # exit
    if btnp(KEY_ESCAPE):
        quit()

    # vitoria
    if winner is not None:
        if btnp(KEY_SPACE):
            reset_game()
        return

    if not music_playing:
        play(1, 4, loop=True)
        play(2, 5, loop=True)
        music_playing = True

    # movimento raquetes
    if btn(KEY_W): p1_y -= 2
    if btn(KEY_S): p1_y += 2
    if btn(KEY_UP): p2_y -= 2
    if btn(KEY_DOWN): p2_y += 2

    p1_y = max(0, min(p1_y, 104))
    p2_y = max(0, min(p2_y, 104))

    # TODO: Enviar posição da raquete local via cliente.py
    # client.send_paddle_position(p1_y or p2_y, dependendo do lado)

    # TODO: Receber posição da raquete do oponente via cliente.py
    # opponent_y = client.get_opponent_position()
    # Atualizar p1_y ou p2_y com opponent_y

    # gerencia timer da bola congelada
    if ball_frozen:
        freeze_timer -= 1
        if freeze_timer <= 0:
            ball_frozen = False
        return  # não atualiza física enquanto congelada

    # fisica bola
    ball_x += ball_dx
    ball_y += ball_dy

    # TODO: No modo online, receber estado da bola do servidor
    # ball_state = client.get_ball_state()
    # ball_x, ball_y, ball_dx, ball_dy = ball_state

    # rebote nas paredes superior/inferior
    if ball_y <= 0 or ball_y >= 120:
        ball_dy *= -1

    # colisão com raquete esquerda (P1)
    if 3 <= ball_x <= 7 and p1_y <= ball_y <= p1_y + 16:
        # calcula onde a bola bateu na raquete (0 = topo, 1 = base)
        hit_pos = (ball_y - p1_y) / 16
        
        # ajusta trajetória: topo rebate pra cima, base pra baixo, meio reto
        ball_dy = (hit_pos - 0.5) * 4  # varia de -2 a +2
        
        # inverte direção horizontal
        ball_dx = abs(ball_dx)
        ball_x = 7
        
        # aumenta velocidade gradualmente
        ball_speed += 0.1
        ball_dx = ball_speed if ball_dx > 0 else -ball_speed
        
        play(0, 2)

    # colisão com raquete direita (P2)
    if 153 <= ball_x <= 157 and p2_y <= ball_y <= p2_y + 16:
        # calcula onde a bola bateu na raquete
        hit_pos = (ball_y - p2_y) / 16
        
        # ajusta trajetória
        ball_dy = (hit_pos - 0.5) * 4
        
        # inverte direção horizontal
        ball_dx = -abs(ball_dx)
        ball_x = 153
        
        # aumenta velocidade gradualmente
        ball_speed += 0.1
        ball_dx = ball_speed if ball_dx > 0 else -ball_speed
        
        play(0, 2)

    # pontuacao
    if ball_x < 0:
        score2 += 1
        if score2 >= 10:
            winner = "DIREITA"
            stop(1) 
            stop(2)
            music_playing = False
            play(0, 1) 
        else:
            reset_ball()

    if ball_x > 160:
        score1 += 1
        if score1 >= 10:
            winner = "ESQUERDA"
            stop(1)
            stop(2)
            music_playing = False
            play(0, 1)
        else:
            reset_ball()

    # TODO: Receber placar atualizado do servidor
    # score1, score2 = client.get_scores()

def draw():
    cls(0)

    if winner is not None:
        msg = f"PLAYER DA {winner} VENCEU!"
        x_pos = 80 - (len(msg) * 2)
        text(x_pos, 50, msg, pyxel.frame_count % 16) 
        msg2 = "SPACE: Restart"
        x_pos2 = 80 - (len(msg2) * 2)
        text(x_pos2, 70, msg2, 7)
        msg3 = "ESC: Quit"
        x_pos3 = 80 - (len(msg3) * 2)
        text(x_pos3, 80, msg3, 7)
        return

    line(80, 0, 80, 120, 13)
    text(60, 10, str(score1), 12)
    text(95, 10, str(score2), 8)
    
    rect(3, p1_y, 4, 16, 12)  # azul royal
    rect(153, p2_y, 4, 16, 8)  # vermelho sangue
    circ(ball_x, ball_y, 2, 7)

run(update, draw)