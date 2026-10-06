#!/usr/bin/env python3

from classes import Metrics
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

robozin = Robot(config.start, config.sight_range, config.charge_per_movement, config.charge_per_vacuum, config.power_station_loc, config.max_steps)
ambiente = Environment(config.map, config.cell_dirt_prob, config.random_seed)
metrica = Metrics()
metrica.celulas_sujas_iniciais = ambiente.sujeira

#robozin.limpeza(ambiente, metrica, "ordem")
robozin.limpeza(ambiente, metrica, "proximidade")
    

print("número de movimentos realizados: ", metrica.movimentos)
print("número de ações de aspiração realizadas: ", metrica.aspiracoes)
print("número total de ações: ", metrica.total_acoes)
print("quantidade de células inicialmente sujas: ", metrica.celulas_sujas_iniciais)
print("quantidade de células efetivamente limpas: ", metrica.celulas_limpas)
print("quantidade de sujas restantes:",metrica.celulas_sujas_restantes(robozin))