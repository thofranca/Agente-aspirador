import pygame
import sys
import time
import random
from classes import Robot, Environment, Metrics
import parser
if len(sys.argv) < 2:
    print("Uso: python interface.py <arquivo_de_entrada>")
    sys.exit(1)

arquivo_entrada = sys.argv[1]
config = parser.load_config(arquivo_entrada)

robozin = Robot(config.start, config.sight_range)
ambiente = Environment(config.map)
metrica = Metrics()
metrica.celulas_sujas_iniciais = ambiente.sujeira

# Configurações do Pygame
pygame.init()
pygame.font.init()

TAMANHO_CELULA = 60
LARGURA = len(ambiente.map[0]) * TAMANHO_CELULA
ALTURA = len(ambiente.map) * TAMANHO_CELULA
PAINEL_LATERAL = 250 # Espaço para os status laterais

tela = pygame.display.set_mode((LARGURA + PAINEL_LATERAL, ALTURA))
pygame.display.set_caption("Aspirador Inteligente - IA")

# Paleta de Cores Moderna
COR_FUNDO = (30, 30, 40)         # Área não explorada ("fog of war" escuro)
COR_CHAO = (240, 240, 245)       # Chão limpo e claro
COR_LINHA = (200, 200, 215)      # Linhas da grade mais suaves
COR_PAREDE = (65, 75, 85)        # Paredes e obstáculos
COR_ROBO_CORPO = (45, 45, 45)    # Corpo principal do robô (Roomba)
COR_ROBO_DETALHE = (0, 255, 120) # Luz do robozinho (Verde neon)
COR_SUJEIRA = (120, 85, 60)      # Marrom realista para sujeira
COR_PAINEL = (40, 45, 55)        # Fundo do HUD lateral
COR_TEXTO = (240, 240, 240)      # Texto claro
COR_DESTAQUE = (100, 200, 255)   # Azul claro para títulos

# Fontes
fonte = pygame.font.SysFont("segoeui", 18, bold=True)
fonte_titulo = pygame.font.SysFont("segoeui", 24, bold=True)

# Gerar "partículas" de sujeira aleatórias para as células sujas
random.seed(42) # Consistência visual entre execuções
sujeiras_particulas = {}
for i in range(len(ambiente.map)):
    for j in range(len(ambiente.map[0])):
        if ambiente.map[i][j] == 1:
            particulas = []
            for _ in range(random.randint(4, 7)):
                ox = random.randint(-15, 15)
                oy = random.randint(-15, 15)
                r = random.randint(2, 5)
                particulas.append((ox, oy, r))
            sujeiras_particulas[(i, j)] = particulas

clock = pygame.time.Clock()

# Inicia a lógica básica
robozin.visao(ambiente)
robozin.aspirar(ambiente, metrica)

rodando = True
terminou = False
ultimo_movimento = pygame.time.get_ticks()

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Preenche o fundo não explorado
    tela.fill(COR_FUNDO)

    # Desenhar o mapa
    for i in range(len(ambiente.map)):
        for j in range(len(ambiente.map[0])):
            retangulo = pygame.Rect(j * TAMANHO_CELULA, i * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
            
            # Só revela o mapa onde o robô já observou
            if (i, j) in robozin.observados:
                valor = ambiente.map[i][j]
                
                # Fundo da célula
                if valor == 9:
                    # Desenha Obstáculo com uma bordinha 3D
                    pygame.draw.rect(tela, COR_PAREDE, retangulo)
                    pygame.draw.rect(tela, (85, 95, 105), retangulo, 2)
                else:
                    # Desenha o Chão
                    pygame.draw.rect(tela, COR_CHAO, retangulo)
                    pygame.draw.rect(tela, COR_LINHA, retangulo, 1)

                # Desenha partículas de sujeira (se a célula ainda for 1)
                if valor == 1 and (i, j) in sujeiras_particulas:
                    for ox, oy, raio in sujeiras_particulas[(i, j)]:
                        cx = retangulo.centerx + ox
                        cy = retangulo.centery + oy
                        pygame.draw.circle(tela, COR_SUJEIRA, (cx, cy), raio)

    # Desenhar o Robô (estilo Roomba)
    cx = int(robozin.y * TAMANHO_CELULA + TAMANHO_CELULA / 2)
    cy = int(robozin.x * TAMANHO_CELULA + TAMANHO_CELULA / 2)
    raio_robo = TAMANHO_CELULA // 2 - 6
    
    # Sombra do robô
    pygame.draw.circle(tela, (20, 20, 20), (cx + 3, cy + 3), raio_robo)
    # Corpo principal do aspirador
    pygame.draw.circle(tela, COR_ROBO_CORPO, (cx, cy), raio_robo)
    # Borda prata/cinza ao redor
    pygame.draw.circle(tela, (80, 80, 80), (cx, cy), raio_robo, 2)
    # Luz indicadora de energia no centro
    pygame.draw.circle(tela, COR_ROBO_DETALHE, (cx, cy), 5)

    # ==========================
    # Desenhar o Painel (HUD)
    # ==========================
    painel_rect = pygame.Rect(LARGURA, 0, PAINEL_LATERAL, ALTURA)
    pygame.draw.rect(tela, COR_PAINEL, painel_rect)
    pygame.draw.line(tela, COR_DESTAQUE, (LARGURA, 0), (LARGURA, ALTURA), 3)
    
    tela.blit(fonte_titulo.render("Estatísticas", True, COR_DESTAQUE), (LARGURA + 20, 30))
    
    efi = round((metrica.aspiracoes/max(1, metrica.movimentos))*100, 1)
    textos = [
        f"Movimentos: {metrica.movimentos}",
        f"Aspiradas: {metrica.aspiracoes}",
        f"Suj. Restante: {metrica.celulas_sujas_restantes}",
        f"Eficiência: {efi}%"
    ]
    
    y_texto = 80
    for t in textos:
        img_texto = fonte.render(t, True, COR_TEXTO)
        tela.blit(img_texto, (LARGURA + 20, y_texto))
        y_texto += 35

    if terminou:
        texto_fim = fonte_titulo.render("CONCLUÍDO!", True, (50, 255, 100))
        tela.blit(texto_fim, (LARGURA + 20, y_texto + 20))

    pygame.display.flip()

    # Lógica de atualização usando tempo para não travar a janela
    tempo_atual = pygame.time.get_ticks()
    if not terminou and (tempo_atual - ultimo_movimento) > 150: # Atualiza a cada 150ms
        if len(robozin.observados) < len(ambiente.map) * len(ambiente.map[0]):
            robozin.varredura(ambiente, metrica)
            ultimo_movimento = tempo_atual
        else:
            terminou = True

    clock.tick(60)

pygame.quit()
