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

robozin = Robot(config.start, config.sight_range, config.charge_per_movement, config.charge_per_vacuum, config.power_station_loc, max_steps=config.max_steps)
ambiente = Environment(config.map, cell_dirt_prob=config.cell_dirt_prob, semente=config.random_seed)
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

# Define a função de desenho que será chamada a cada passo
def atualizar_interface_sync(terminado=False):
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

    tela.fill(COR_FUNDO)

    for i in range(len(ambiente.map)):
        for j in range(len(ambiente.map[0])):
            retangulo = pygame.Rect(j * TAMANHO_CELULA, i * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
            
            # Só revela o mapa onde o robô já observou (ou revela tudo se for cego, pro usuário ver)
            if robozin.sight_range == 0 or (i, j) in robozin.observados:
                valor = ambiente.map[i][j]
                
                # Fundo da célula
                if valor == 9:
                    pygame.draw.rect(tela, COR_PAREDE, retangulo)
                    pygame.draw.rect(tela, (85, 95, 105), retangulo, 2)
                else:
                    pygame.draw.rect(tela, COR_CHAO, retangulo)
                    pygame.draw.rect(tela, COR_LINHA, retangulo, 1)

                # Desenha partículas de sujeira (se a célula ainda for 1)
                if valor == 1 and (i, j) in sujeiras_particulas:
                    for ox, oy, raio in sujeiras_particulas[(i, j)]:
                        cx = retangulo.centerx + ox
                        cy = retangulo.centery + oy
                        pygame.draw.circle(tela, COR_SUJEIRA, (cx, cy), raio)

    # Desenhar a Base de Carregamento
    ex, ey = robozin.estacao_loc
    cx_base = int(ey * TAMANHO_CELULA + TAMANHO_CELULA / 2)
    cy_base = int(ex * TAMANHO_CELULA + TAMANHO_CELULA / 2)
    rect_estacao = pygame.Rect(ey * TAMANHO_CELULA + 5, ex * TAMANHO_CELULA + 5, TAMANHO_CELULA - 10, TAMANHO_CELULA - 10)
    pygame.draw.rect(tela, (50, 100, 150), rect_estacao, border_radius=10)
    pygame.draw.rect(tela, (100, 200, 255), rect_estacao, 2, border_radius=10)
    # Símbolo de Raio na base
    raio_points = [
        (cx_base + 3, cy_base - 10),
        (cx_base - 7, cy_base + 2),
        (cx_base + 1, cy_base + 2),
        (cx_base - 3, cy_base + 12),
        (cx_base + 7, cy_base - 2),
        (cx_base - 1, cy_base - 2)
    ]
    pygame.draw.polygon(tela, (255, 215, 0), raio_points)

    # Cor da bateria do Robô
    bateria_perc = min(100, max(0, robozin.bateria))
    if bateria_perc > 50:
        cor_luz = (0, 255, 120)  # Verde neon
    elif bateria_perc > 20:
        cor_luz = (255, 200, 0)  # Amarelo
    else:
        cor_luz = (255, 50, 50)  # Vermelho

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
    pygame.draw.circle(tela, cor_luz, (cx, cy), 6)

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

    # Barra de Bateria no HUD
    y_bateria = y_texto + 10
    tela.blit(fonte.render("Bateria:", True, COR_TEXTO), (LARGURA + 20, y_bateria))
    
    bar_width = PAINEL_LATERAL - 40
    bar_height = 22
    rect_bar_bg = pygame.Rect(LARGURA + 20, y_bateria + 30, bar_width, bar_height)
    pygame.draw.rect(tela, (60, 60, 70), rect_bar_bg, border_radius=6)
    
    fill_width = int(bar_width * (bateria_perc / 100))
    if fill_width > 0:
        rect_bar_fg = pygame.Rect(LARGURA + 20, y_bateria + 30, fill_width, bar_height)
        pygame.draw.rect(tela, cor_luz, rect_bar_fg, border_radius=6)
        
    bat_texto = fonte.render(f"{int(bateria_perc)}%", True, (20, 20, 20) if bateria_perc > 20 else (255,255,255))
    tela.blit(bat_texto, (LARGURA + 20 + bar_width // 2 - bat_texto.get_width() // 2, y_bateria + 30))

    if terminado:
        texto_fim = fonte_titulo.render("CONCLUÍDO!", True, (50, 255, 100))
        tela.blit(texto_fim, (LARGURA + 20, y_bateria + 70))

    pygame.display.flip()
    
    # Pausa para animação
    if not terminado:
        time.sleep(0.25)

# --- INÍCIO DA MÁGICA: INTERCEPTANDO OS MOVIMENTOS ---
# Para que a interface rode mostrando cada passo de qualquer loop (seja
# o while da limpeza ou os passos de movimento) sem precisarmos alterar a 
# lógica lá no classes.py, nós interceptamos as propriedades do robô!

original_movimento = Robot.movimento
original_aspirar = Robot.aspirar
def novo_movimento(self, ambiente, metrica):
    resultado = original_movimento(self, ambiente, metrica)
    atualizar_interface_sync(False)
    return resultado
def novo_aspirar(self, ambiente, metrica):
    resultado = original_aspirar(self, ambiente, metrica)
    atualizar_interface_sync(False)
    return resultado
# Aplicando os interceptadores
Robot.movimento = novo_movimento
Robot.aspirar = novo_aspirar
# -----------------------------------------------------

# Mostra o estado inicial antes de começar
atualizar_interface_sync(False)

# Chama a função principal que faz o processo inteiro (mapeamento + limpeza)!
# A interface vai se atualizar sozinha graças à interceptação acima.
robozin.limpeza(ambiente, metrica, "proximidade")

# Quando terminar, fica num loop infinito para não fechar a janela direto
while True:
    atualizar_interface_sync(True)
    time.sleep(0.1)
