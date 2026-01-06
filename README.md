# pong-multiplayer 🎮

Um jogo de Pong clássico com modo multiplayer online via UDP, desenvolvido em Python com Pyxel.

## Sobre o Projeto

Este é um remake moderno do clássico Pong:

- 🌐 Suporte para multiplayer online via protocolo UDP
- 🎨 Visual retrô com Pyxel
- 🎵 Efeitos sonoros e música de fundo

## Estrutura do Projeto

```
pong_online/
├── game.py           # Interface gráfica e lógica do jogo (Pyxel)
├── servidor.py       # Servidor UDP
├── cliente.py        # Cliente UDP
└── game.pyxres       # Recursos gráficos e sonoros do Pyxel
```

## Requisitos

- Python 3.8+
- Pyxel 1.9.0+

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/pong-multiplayer.git
cd pong-multiplayer
```

2. Instale o Pyxel:
```bash
pip install pyxel
```

3. Execute o jogo (modo local):
```bash
python game.py
```

## Como Jogar

- Primeiro jogador a alcançar **10 pontos** vence

**Jogador 1 (Esquerda):**
- `W` - Mover para cima
- `S` - Mover para baixo

**Jogador 2 (Direita):**
- `↑` - Mover para cima
- `↓` - Mover para baixo

**Controles Gerais:**
- `SPACE` - Reiniciar jogo (após vitória)
- `ESC` - Sair do jogo

### Arquitetura

O sistema multiplayer utilizará o protocolo UDP para comunicação em tempo real:

```
┌─────────────┐         UDP          ┌─────────────┐
│  Cliente 1  │ ◄─────────────────► │  Servidor   │
│  (game.py)  │                      │(servidor.py)│
└─────────────┘                      └─────────────┘
                                            ▲
                                            │ UDP
                                            ▼
                                     ┌─────────────┐
                                     │  Cliente 2  │
                                     │  (game.py)  │
                                     └─────────────┘
```

## Autores

- **Mariana Sanchez Pedroni**
- **Anna Bheatryz Martins dos Santos**
