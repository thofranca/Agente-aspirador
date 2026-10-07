#!/usr/bin/env python3

import sys
import parser
import time
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

    import interface
    tipo_estrategia, atualizar_gui = interface.iniciar_gui(robozin, ambiente, metrica)
    
    robozin.limpeza(ambiente, metrica, tipo_estrategia)
    
    if robozin.sight_range == 0:
        if tipo_estrategia == "cima-baixo":
            nome_estrategia = "Cima-Baixo (Busca às cegas)"
        else:
            nome_estrategia = "Esquerda-Direita (Busca às cegas)"
    elif tipo_estrategia == "ordem":
        nome_estrategia = "Ordem em que foram encontradas"
    else:
        nome_estrategia = "Célula suja mais próxima"

    sujeiras_reais_restantes = sum(linha.count(1) for linha in ambiente.map)

    print(f"\nEstrategia: {nome_estrategia}")
    print(f"número de movimentos realizados: {metrica.movimentos}")
    print(f"número de ações de aspiração realizadas: {metrica.aspiracoes}")
    print(f"número total de ações: {metrica.total_acoes}")
    print(f"quantidade de células inicialmente sujas: {metrica.celulas_sujas_iniciais}")
    print(f"quantidade de células efetivamente limpas: {metrica.celulas_limpas}")
    print(f"quantidade de células sujas restantes: {sujeiras_reais_restantes}")
    print(f"carga restante na bateria: {robozin.bateria}")
    print(f"número de recargas efetuadas: {metrica.recargas}")

    if robozin.sight_range > 0:
        print(f"número de células únicas visitadas na exploração: {len(metrica.celulas_visitadas_exploracao)}")
    print("")
    
    try:
        while True:
            atualizar_gui(True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        sys.exit(0)