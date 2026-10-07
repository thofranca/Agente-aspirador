import pygame
import sys
import time
import random

def iniciar_gui(robozin, ambiente, metrica):
    pygame.init()
    pygame.font.init()

    TAMANHO_CELULA = 60
    LARGURA = len(ambiente.map[0]) * TAMANHO_CELULA
    ALTURA = len(ambiente.map) * TAMANHO_CELULA
    PAINEL_LATERAL = 250

    tela = pygame.display.set_mode((LARGURA + PAINEL_LATERAL, ALTURA))
    pygame.display.set_caption("Aspirador Inteligente - IA")

    COR_FUNDO = (30, 30, 40)
    COR_CHAO = (240, 240, 245)
    COR_LINHA = (200, 200, 215)
    COR_PAREDE = (65, 75, 85)
    COR_ROBO_CORPO = (45, 45, 45)
    COR_ROBO_DETALHE = (0, 255, 120)
    COR_SUJEIRA = (120, 85, 60)
    COR_PAINEL = (40, 45, 55)
    COR_TEXTO = (240, 240, 240)
    COR_DESTAQUE = (100, 200, 255)

    fonte = pygame.font.SysFont("segoeui", 18, bold=True)
    fonte_titulo = pygame.font.SysFont("segoeui", 24, bold=True)


    estado = {'terminado': False, 'tipo_estrategia': "proximidade"}

    def atualizar_interface_sync(terminado=False):
        estado['terminado'] = terminado
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        tela.fill(COR_FUNDO)

        for i in range(len(ambiente.map)):
            for j in range(len(ambiente.map[0])):
                retangulo = pygame.Rect(j * TAMANHO_CELULA, i * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
                
                if robozin.sight_range == 0 or (i, j) in robozin.observados:
                    valor = ambiente.map[i][j]
                    if valor == 9:
                        pygame.draw.rect(tela, COR_PAREDE, retangulo)
                        pygame.draw.rect(tela, (85, 95, 105), retangulo, 2)
                    else:
                        pygame.draw.rect(tela, COR_CHAO, retangulo)
                        pygame.draw.rect(tela, COR_LINHA, retangulo, 1)

                    if valor == 1:
                        # Geração determinística de partículas espalhadas para parecer poeira
                        # Usamos as coordenadas (i, j) para criar uma variação visual estrita sem usar 'random'
                        pseudo_val = (i * 73856093 ^ j * 19349663)
                        num_particles = 6 + (pseudo_val % 4)
                        
                        for p in range(num_particles):
                            # Extraindo offsets e raio a partir do pseudo_val
                            ox = ((pseudo_val >> (p * 4)) % 30) - 15
                            oy = ((pseudo_val >> (p * 4 + 2)) % 30) - 15
                            r = ((pseudo_val >> (p * 2)) % 3) + 1  # raio de 1 a 3 para parecer poeira fina
                            
                            # Pequena variação na cor para dar textura
                            cor_variacao = ((pseudo_val >> (p * 3)) % 40) - 20
                            cor_particula = (
                                max(0, min(255, COR_SUJEIRA[0] + cor_variacao)),
                                max(0, min(255, COR_SUJEIRA[1] + cor_variacao)),
                                max(0, min(255, COR_SUJEIRA[2] + cor_variacao))
                            )
                            
                            cx = retangulo.centerx + ox
                            cy = retangulo.centery + oy
                            pygame.draw.circle(tela, cor_particula, (cx, cy), r)


        # --- DESENHA A ESTAÇÃO ---
        ex, ey = robozin.estacao_loc
        cx_est = ey * TAMANHO_CELULA + TAMANHO_CELULA // 2
        cy_est = ex * TAMANHO_CELULA + TAMANHO_CELULA // 2
        
        # Base da estação (plataforma de metal com bordas duplas)
        rect_estacao = pygame.Rect(ey * TAMANHO_CELULA + 8, ex * TAMANHO_CELULA + 8, TAMANHO_CELULA - 16, TAMANHO_CELULA - 16)
        pygame.draw.rect(tela, (40, 45, 50), rect_estacao, border_radius=10) # Fundo escuro
        rect_estacao_inner = pygame.Rect(ey * TAMANHO_CELULA + 12, ex * TAMANHO_CELULA + 12, TAMANHO_CELULA - 24, TAMANHO_CELULA - 24)
        pygame.draw.rect(tela, (65, 75, 85), rect_estacao_inner, border_radius=6) # Centro metálico
        
        # Pinos / Placa de carregamento com brilho verde neon
        pygame.draw.circle(tela, (0, 150, 80), (cx_est, cy_est), TAMANHO_CELULA // 4 - 2)
        pygame.draw.circle(tela, (0, 255, 120), (cx_est, cy_est), TAMANHO_CELULA // 4 - 4)
        pygame.draw.rect(tela, (15, 20, 25), (cx_est - 3, cy_est - 8, 6, 16), border_radius=2) # Conector escuro no meio

        # --- DESENHA O ROBÔ ---
        rx, ry = robozin.x, robozin.y
        cx_robo = ry * TAMANHO_CELULA + TAMANHO_CELULA // 2
        cy_robo = rx * TAMANHO_CELULA + TAMANHO_CELULA // 2
        raio_robo = TAMANHO_CELULA // 2 - 8
        
        # Calculando a cor do LED do robô com base na bateria atual
        bat_atual = max(0, (robozin.bateria / 100.0) * 100)
        cor_led = (0, 255, 120) if bat_atual > 40 else (255, 200, 0) if bat_atual > 15 else (255, 50, 50)
        
        # Sombra sob o robô para dar sensação de volume
        pygame.draw.circle(tela, (20, 20, 25), (cx_robo + 3, cy_robo + 4), raio_robo)
        
        # Corpo principal metálico escuro (Roomba)
        pygame.draw.circle(tela, (35, 38, 42), (cx_robo, cy_robo), raio_robo)
        
        # Bumper (borda de proteção frontal um pouco mais clara)
        pygame.draw.circle(tela, (80, 85, 90), (cx_robo, cy_robo), raio_robo, width=3)
        
        # Camada interna do design (círculo recuado)
        pygame.draw.circle(tela, (25, 25, 30), (cx_robo, cy_robo), raio_robo - 6)
        
        # Detalhe central (LED principal do robô)
        pygame.draw.circle(tela, cor_led, (cx_robo, cy_robo), 4)
        pygame.draw.circle(tela, (255, 255, 255), (cx_robo, cy_robo), 1) # Brilho no meio do LED
        
        # Escovinha rotativa amarela saindo pelo canto inferior esquerdo (típico de aspiradores)
        escova_x, escova_y = cx_robo - (raio_robo - 6), cy_robo + (raio_robo - 6)
        pygame.draw.line(tela, (220, 200, 50), (escova_x, escova_y), (escova_x - 6, escova_y + 4), 2)
        pygame.draw.line(tela, (220, 200, 50), (escova_x, escova_y), (escova_x - 1, escova_y + 7), 2)
        pygame.draw.line(tela, (220, 200, 50), (escova_x, escova_y), (escova_x - 7, escova_y - 1), 2)

        rect_painel = pygame.Rect(LARGURA, 0, PAINEL_LATERAL, ALTURA)
        pygame.draw.rect(tela, COR_PAINEL, rect_painel)
        pygame.draw.line(tela, COR_DESTAQUE, (LARGURA, 0), (LARGURA, ALTURA), 3)

        titulo = fonte_titulo.render("MÉTRICAS", True, COR_DESTAQUE)
        tela.blit(titulo, (LARGURA + 20, 20))

        bateria_perc = max(0, (robozin.bateria / 100.0) * 100)
        sujeiras_reais = sum(linha.count(1) for linha in ambiente.map)

        textos = [
            f"Passos: {metrica.movimentos}",
            f"Aspiradas: {metrica.aspiracoes}",
            f"Suj. Restante: {sujeiras_reais}"
        ]
        
        y_texto = 80
        for t in textos:
            img_texto = fonte.render(t, True, COR_TEXTO)
            tela.blit(img_texto, (LARGURA + 20, y_texto))
            y_texto += 35

        y_bateria = y_texto + 10
        tela.blit(fonte.render("Bateria:", True, COR_TEXTO), (LARGURA + 20, y_bateria))
        
        bar_width = PAINEL_LATERAL - 40
        bar_height = 22
        rect_bar_bg = pygame.Rect(LARGURA + 20, y_bateria + 30, bar_width, bar_height)
        pygame.draw.rect(tela, (60, 60, 70), rect_bar_bg, border_radius=6)
        
        fill_width = int(bar_width * (bateria_perc / 100))
        if fill_width > 0:
            rect_bar_fg = pygame.Rect(LARGURA + 20, y_bateria + 30, fill_width, bar_height)
            pygame.draw.rect(tela, COR_ROBO_DETALHE, rect_bar_fg, border_radius=6)
            
        bat_texto = fonte.render(f"{int(bateria_perc)}%", True, (20, 20, 20) if bateria_perc > 20 else (255,255,255))
        tela.blit(bat_texto, (LARGURA + 20 + bar_width // 2 - bat_texto.get_width() // 2, y_bateria + 30))

        if terminado:
            if robozin.sight_range == 0:
                if estado['tipo_estrategia'] == 'cima-baixo':
                    est_texto = "Passagem Cima-Baixo (sem visão)"
                else:
                    est_texto = "Passagem Esquerda-Direita (sem visão)"
            elif estado['tipo_estrategia'] == 'ordem':
                est_texto = "Ordem em que foram encontradas"
            else:
                est_texto = "Célula suja mais próxima"
                
            suj_reais = sum(linha.count(1) for linha in ambiente.map)
            
            linhas_relatorio = [
                f"Estratégia: {est_texto}",
                f"Movimentos realizados: {metrica.movimentos}",
                f"Ações de aspiração: {metrica.aspiracoes}",
                f"Total de ações: {metrica.total_acoes}",
                f"Células inicialmente sujas: {metrica.celulas_sujas_iniciais}",
                f"Células efetivamente limpas: {metrica.celulas_limpas}",
                f"Células sujas restantes: {suj_reais}",
                f"Carga restante na bateria: {int(robozin.bateria)}%",
                f"Recargas efetuadas: {metrica.recargas}"
            ]
            
            if robozin.sight_range > 0:
                linhas_relatorio.append(f"Células únicas exploradas: {len(metrica.celulas_visitadas_exploracao)}")
            
            s = pygame.Surface((LARGURA + PAINEL_LATERAL, ALTURA))
            s.set_alpha(200)
            s.fill((10, 10, 15))
            tela.blit(s, (0,0))
            
            painel_fim_w = min(600, (LARGURA + PAINEL_LATERAL) - 20)
            painel_fim_h = 390
            painel_fim = pygame.Rect((LARGURA + PAINEL_LATERAL)//2 - painel_fim_w//2, ALTURA//2 - painel_fim_h//2, painel_fim_w, painel_fim_h)
            pygame.draw.rect(tela, (40, 45, 55), painel_fim, border_radius=15)
            pygame.draw.rect(tela, (50, 255, 100), painel_fim, 3, border_radius=15)
            
            titulo_fim = fonte_titulo.render("RELATÓRIO FINAL", True, (50, 255, 100))
            tela.blit(titulo_fim, (painel_fim.centerx - titulo_fim.get_width()//2, painel_fim.y + 15))
            
            y_rel = painel_fim.y + 60
            fonte_rel = pygame.font.SysFont("segoeui", 17, bold=True)
            for linha in linhas_relatorio:
                img = fonte_rel.render(linha, True, (240, 240, 240))
                tela.blit(img, (painel_fim.x + 20, y_rel))
                y_rel += 30

        pygame.display.flip()
        if not terminado:
            time.sleep(0.25)

    original_movimento = type(robozin).movimento
    original_aspirar = type(robozin).aspirar
    def novo_movimento(self, amb, met):
        resultado = original_movimento(self, amb, met)
        atualizar_interface_sync(False)
        return resultado
    def novo_aspirar(self, amb, met):
        resultado = original_aspirar(self, amb, met)
        atualizar_interface_sync(False)
        return resultado
        
    type(robozin).movimento = novo_movimento
    type(robozin).aspirar = novo_aspirar

    escolhendo = True
    painel_w, painel_h = 450, 260
    painel_rect = pygame.Rect((LARGURA + PAINEL_LATERAL)//2 - painel_w//2, ALTURA//2 - painel_h//2, painel_w, painel_h)
    btn_ordem = pygame.Rect(painel_rect.centerx - 160, painel_rect.y + 100, 320, 50)
    btn_prox = pygame.Rect(painel_rect.centerx - 160, painel_rect.y + 170, 320, 50)

    if robozin.sight_range > 0:
        texto_op1 = "Ordem em que foram encontradas"
        texto_op2 = "Sempre a sujeira mais próxima"
        val_op1 = "ordem"
        val_op2 = "proximidade"
    else:
        texto_op1 = "Cima-Baixo (Coluna por Coluna)"
        texto_op2 = "Esquerda-Direita (Linha por Linha)"
        val_op1 = "cima-baixo"
        val_op2 = "esquerda-direita"

    while escolhendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if btn_ordem.collidepoint(evento.pos):
                    estado['tipo_estrategia'] = val_op1
                    escolhendo = False
                elif btn_prox.collidepoint(evento.pos):
                    estado['tipo_estrategia'] = val_op2
                    escolhendo = False
                
        tela.fill((25, 25, 35))
        pygame.draw.rect(tela, (40, 45, 55), painel_rect, border_radius=20)
        pygame.draw.rect(tela, COR_DESTAQUE, painel_rect, 3, border_radius=20)
        titulo = fonte_titulo.render("Escolha a Estratégia de Limpeza", True, (255, 255, 255))
        tela.blit(titulo, (painel_rect.centerx - titulo.get_width()//2, painel_rect.y + 30))
        mouse_pos = pygame.mouse.get_pos()
        
        fonte_botao = pygame.font.SysFont("segoeui", 18, bold=True)
        cor_ordem = (100, 200, 255) if btn_ordem.collidepoint(mouse_pos) else (60, 130, 180)
        pygame.draw.rect(tela, cor_ordem, btn_ordem, border_radius=10)
        txt_ordem = fonte_botao.render(texto_op1, True, (20, 20, 20))
        tela.blit(txt_ordem, (btn_ordem.centerx - txt_ordem.get_width()//2, btn_ordem.centery - txt_ordem.get_height()//2))
        
        cor_prox = (100, 200, 255) if btn_prox.collidepoint(mouse_pos) else (60, 130, 180)
        pygame.draw.rect(tela, cor_prox, btn_prox, border_radius=10)
        txt_prox = fonte_botao.render(texto_op2, True, (20, 20, 20))
        tela.blit(txt_prox, (btn_prox.centerx - txt_prox.get_width()//2, btn_prox.centery - txt_prox.get_height()//2))
        
        pygame.display.flip()

    atualizar_interface_sync(False)
    
    return estado['tipo_estrategia'], atualizar_interface_sync

if __name__ == '__main__':
    # Mantendo a funcionalidade antiga caso rodem direto o interface.py
    import parser
    from classes import Robot, Environment, Metrics
    if len(sys.argv) < 2:
        print("Uso: python interface.py <arquivo_de_entrada>")
        sys.exit(1)
        
    config = parser.load_config(sys.argv[1])
    robozin = Robot(config.start, config.sight_range, config.charge_per_movement, config.charge_per_vacuum, config.power_station_loc, max_steps=config.max_steps)
    ambiente = Environment(config.map, cell_dirt_prob=config.cell_dirt_prob, semente=config.random_seed)
    metrica = Metrics()
    metrica.celulas_sujas_iniciais = ambiente.sujeira

    tipo_estrategia, atualizar = iniciar_gui(robozin, ambiente, metrica)
    robozin.limpeza(ambiente, metrica, tipo_estrategia)
    
    while True:
        atualizar(True)
        time.sleep(0.1)
