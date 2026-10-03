#!/usr/bin/env python3

import sys
import parser
from classes import *


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python ARQUIVO-DE-CONFIGURACAO.txt")
        sys.exit(-1)

    config = parser.load_config(sys.argv[1])

    print("Mapa:")
    for row in config.map:
        print(row)

    print()
    print("Posição inicial:", config.start)
    print("Campo de visão:", config.sight_range)
    print("Custo de movimento:", config.charge_per_movement)
    print("Custo de aspiração:", config.charge_per_vacuum)
    print("Estação:", config.power_station_loc)
    print("Probabilidade de sujeira:", config.cell_dirt_prob)
    print("Seed:", config.random_seed)
    print("Máximo de passos:", config.max_steps)

robozin = Robot(config.start[0],config.start[1])
ambiente = Environment(config.map)

while len(robozin.visited) != (len(config.map) * len(config.map[0])):
    robozin.varredura(ambiente)
    
# indo = True
# subindo = True
# numero_mov = 0
# numero_asp = 0
# qnt_suj = 0
# inicio = config.start
# posicao = inicio
# visitado = [inicio] 
# parede = []   
# mapa = config.map
# for i in range(len(mapa)):
#     parede.append((i,-1))
#     parede.append((i,len(mapa[0])))
# for i in range(len(mapa[0])):
#     parede.append((-1,i))
#     parede.append((len(mapa),i))

# while len(visitado) < (len(mapa) * len(mapa[0])):
#     print(posicao)
#     if (posicao[0],posicao[1]+1) not in visitado and (posicao[0],posicao[1]+1) not in parede:
#         indo = True
#         i = posicao[0]
#         j = posicao[1]+1
#         posicao = (i,j)
#         numero_mov += 1
#         visitado.append((i,j))
#         if mapa[i][j] == 1: 
#             print(f"Sujeira encontrada na posição ({i}, {j})")
#             print("Limpando...")
#             qnt_suj += 1
#             mapa[i][j] = 0
#             numero_asp += 1
#     elif (posicao[0],posicao[1]-1) not in visitado and (posicao[0],posicao[1]-1) not in parede:
#         indo = False
#         i = posicao[0]
#         j = posicao[1]-1
#         posicao = (i,j)
#         numero_mov += 1
#         visitado.append((i,j))
#         if mapa[i][j] == 1:
#             print(f"Sujeira encontrada na posição ({i}, {j})")
#             print("Limpando...")
#             qnt_suj += 1
#             mapa[i][j] = 0
#             numero_asp += 1
#     elif (posicao[0]+1,posicao[1]) not in visitado and (posicao[0]+1,posicao[1]) not in parede:
#         indo = True
#         i = posicao[0]+1
#         j = posicao[1]
#         posicao = (i,j)
#         numero_mov += 1
#         visitado.append((i,j))
#         if mapa[i][j] == 1: 
#             print(f"Sujeira encontrada na posição ({i}, {j})")
#             print("Limpando...")
#             qnt_suj += 1
#             mapa[i][j] = 0
#             numero_asp += 1
#     elif (posicao[0]-1,posicao[1]) not in visitado and (posicao[0]-1,posicao[1]) not in parede:
#         indo = False
#         i = posicao[0]-1
#         j = posicao[1]
#         posicao = (i,j)
#         numero_mov += 1
#         visitado.append((i,j))
#         if mapa[i][j] == 1:
#             print(f"Sujeira encontrada na posição ({i}, {j})")
#             print("Limpando...")
#             qnt_suj += 1
#             mapa[i][j] = 0
#             numero_asp += 1
#     else:
#         print("ESTAMOS ENCURRALADOS!!!!")
#         break
   

# print("número de movimentos realizados: ", numero_mov)
# print("número de ações de aspiração realizadas: ", numero_asp)
# print("número total de ações: ", numero_mov + numero_asp)
# print("quantidade de células inicialmente sujas: ", qnt_suj)
# print("quantidade de células efetivamente limpas: ", qnt_suj)
# print("quantidade de células sujas restantes: ", 0)