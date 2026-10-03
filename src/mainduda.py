# #!/usr/bin/env python3

# import sys
# import parser


# if __name__ == '__main__':
#     if len(sys.argv) < 2:
#         print("usage: python ARQUIVO-DE-CONFIGURACAO.txt")
#         sys.exit(-1)

#     config = parser.load_config(sys.argv[1])

#     print("Mapa:")
#     for row in config.map:
#         print(row)

#     print()
#     print("Posição inicial:", config.start)
#     print("Campo de visão:", config.sight_range)
#     print("Custo de movimento:", config.charge_per_movement)
#     print("Custo de aspiração:", config.charge_per_vacuum)
#     print("Estação:", config.power_station_loc)
#     print("Probabilidade de sujeira:", config.cell_dirt_prob)
#     print("Seed:", config.random_seed)
#     print("Máximo de passos:", config.max_steps)

# ambiente = config.map
# qtt_movimentos = 0
# qtt_aspiracao = 0

# start = (0,0)

# cima =(-1,0)
# baixo =(1,0)
# esquerda =(0,-1)
# direita =(0,1)
# movimento = direita

# def andar(posicao, movimento):
#     linha , coluna = posicao
#     m_linha , m_coluna = movimento

#     nova_posicao = (linha+m_linha, coluna+m_coluna)
#     return nova_posicao

# for linha in range(len(ambiente)):
#     for coluna in range(len(ambiente[0])):
#         linha_atual, coluna_atual = start
#         print(start)

#         if ambiente[linha_atual][coluna_atual] == 1:
#             print(ambiente)
#             ambiente[linha_atual][coluna_atual] = 0
#             qtt_aspiracao += 1
#             print(f"limpando celula")
#             print(ambiente)

#         if coluna_atual == len(ambiente[0])-1 and movimento == direita:
#             if linha_atual<len(ambiente)-1:
#                 start = andar(start,baixo)
#                 qtt_movimentos += 1
#                 movimento = esquerda
#         elif coluna_atual == 0 and movimento == esquerda:
#             if linha_atual < len(ambiente)-1:
#                 start = andar(start,baixo)
#                 qtt_movimentos += 1
#                 movimento = direita
#         else:
#             start = andar(start,movimento)
#             qtt_movimentos += 1

        
# print("Movimentos:", qtt_movimentos)
# print("Aspirações:", qtt_aspiracao)
# print(ambiente)

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = []

    def move(self, direction):
        return (self.x+direction[0],self.y+direction[1])

    def varredura(self, ambiente):
        if self.move((1,0)) not in ambiente.parede:
            self.x += 1
        elif self.move((0,1)) not in ambiente.parede:
            self.x -= 1
        elif self.move((-1,0)) not in ambiente.parede:
            self.y += 1
        elif self.move((0,-1)) not in ambiente.parede:
            self.y -= 1
        print(f"Posição atual: ({self.x}, {self.y})")

    def movimento(self,movimento):    
        m_linha , m_coluna = movimento
        self.x + m_linha
        self.y + m_coluna
        print(f"Posição atual: ({self.x}, {self.y})")

    def ver_sujeira(self, ambiente):
        if ambiente[self.x][self.y] == 1:
            print(f"Sujeira encontrada na posição ({self.x}, {self.y})")
            print("Aspirando...")
            ambiente.sujeira[self.x][self.y] = 0


    
class Environment:
    def __init__(self, map):
        self.map = map
        self.__parede = []

    @property 
    def parede(self):
        map = self.map
        for i in range(len(map)):
            self.__parede.append((i,-1))
            self.__parede.append((i,len(map[0])))
        for i in range(len(map[0])):
            self.__parede.append((-1,i))
            self.__parede.append((len(map),i))
        return self.__parede
    
    

    

