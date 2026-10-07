import random
from collections import deque
class Robot:
    def __init__(self, start, sight_range, cons_mov, cons_asp, estacao_loc=(0,0), max_steps=None):
        """Inicializa as variáveis de estado do robô, sensores e restrições operacionais."""
        self.__x = start[0]
        self.__y = start[1]
        self.direction = None
        self.sight_range = sight_range
        self.observados = {}
        self.sujos = []
        self.reexplorar = set()
        self.limpar = False
        self.bateria = 100
        self.consumo_mov = cons_mov
        self.consumo_asp = cons_asp
        self.estacao_loc = estacao_loc
        self.maximo_movimentos = max_steps
    @property
    def x(self):
        """Retorna a linha atual do robô."""
        return self.__x
        
    @x.setter
    def x(self, val):
        """Define a linha e consome bateria relativa ao movimento."""
        self.__x = val
        self.bateria -= self.consumo_mov
        
    @property 
    def y(self):
        """Retorna a coluna atual do robô."""
        return self.__y
        
    @y.setter
    def y(self, val):
        """Define a coluna e consome bateria relativa ao movimento."""
        self.__y = val
        self.bateria -= self.consumo_mov

    def ver_move(self, direction):
        """Retorna as coordenadas resultantes caso o robô ande na direção informada."""
        return (self.x+direction[0],self.y+direction[1])
    
    def qttsujos(self):
        """Retorna a quantidade de células sujas armazenadas na memória do robô."""
        return len(self.sujos)
    
    # def pos_aleat(self,ambiente):
    #     while True:
    #         if self.x != 0:
    #             self.x -= 1
    #         elif self.y != 0:
    #             self.y -= 1
    #         if (self.x,self.y) not in self.visited and (self.x,self.y) not in ambiente.parede:
    #             break
            
    def aspirar(self, ambiente, metrica):
        """Executa a ação de aspirar a célula atual, limpando a sujeira e consumindo bateria."""
        if self.maximo_steps(metrica):
            return False
        
        if ambiente.map[self.x][self.y] == 1:
            print(f"Sujeira encontrada na posição ({self.x}, {self.y})")
            print("Aspirando...")
            
            ambiente.map[self.x][self.y] = 0
            self.bateria -= self.consumo_asp
            metrica.aspiracoes += 1
            metrica.celulas_limpas += 1

            if (self.x, self.y) in self.sujos:
                self.sujos.remove((self.x, self.y))
            self.observados[(self.x, self.y)] = 0

            return True

    def visao(self, ambiente):
        for i in range(-self.sight_range,self.sight_range+1):
            for j in range(-self.sight_range,self.sight_range+1):
                n_x = self.x+i
                n_y = self.y+j
                if 0 <= n_x < len(ambiente.map) and 0 <= n_y < len(ambiente.map[0]):
                    if (n_x, n_y) in self.reexplorar:
                        self.reexplorar.remove((n_x, n_y))
                    valor = ambiente.map[n_x][n_y]
                    self.observados[(n_x, n_y)] = valor
                    if valor == 1:
                        if (n_x,n_y) not in self.sujos:
                            self.sujos.append((n_x, n_y))
                    elif valor == 9:
                        if (n_x,n_y) not in ambiente.parede:
                            ambiente.parede.append((n_x,n_y))
                        
    def limpeza_cega(self, ambiente, metrica, tipo="cima-baixo"):
        """Estratégia de limpeza com sight range = 0, ou seja, sem campo de visão, explorando o ambiente em ziguezague."""
        print(f"LIMPANDO ÀS CEGAS EM: {tipo.upper()}")
        if self.direction is None:
            self.direction = (1, 1)
            
        self.visao(ambiente,metrica)
        
        while True:
            if self.maximo_steps(metrica):
                return False
                
            if not self.tem_bateria_suf(aspirar=True):
                self.ir_carregar(ambiente, metrica)
                
            if ambiente.map[self.x][self.y] == 1:
                self.aspirar(ambiente, metrica)
                    
            dx, dy = self.direction
            
            if tipo == "cima-baixo":
                nx = self.x + dx
                ny = self.y
                if 0 <= nx < len(ambiente.map) and ambiente.map[nx][ny] != 9:
                    self.x = nx
                    self.movimento(ambiente, metrica)
                else:
                    dx *= -1
                    nx = self.x
                    ny = self.y + dy
                    if 0 <= ny < len(ambiente.map[0]) and ambiente.map[nx][ny] != 9:
                        self.y = ny
                        self.direction = (dx, dy)
                        self.movimento(ambiente, metrica)
                    else:
                        print("Fim do mapa alcançado na limpeza cega!")
                        break
            else:
                nx = self.x
                ny = self.y + dy
                if 0 <= ny < len(ambiente.map[0]) and ambiente.map[nx][ny] != 9:
                    self.y = ny
                    self.movimento(ambiente, metrica)
                else:
                    dy *= -1
                    nx = self.x + dx
                    ny = self.y
                    if 0 <= nx < len(ambiente.map) and ambiente.map[nx][ny] != 9:
                        self.x = nx
                        self.direction = (dx, dy)
                        self.movimento(ambiente, metrica)
                    else:
                        print("Fim do mapa alcançado na limpeza cega!")
                        break
                        
        return True

    def limpeza(self, ambiente, metrica,tipo):
        """Fluxo principal do robô: coordena a exploração completa do mapa seguida da limpeza das sujeiras encontradas."""
        if self.sight_range == 0:
            return self.limpeza_cega(ambiente, metrica, tipo)
            
        metrica.celulas_visitadas_exploracao.add((self.x, self.y))
        
        while True:
            while len(self.observados) < len(ambiente.map)*len(ambiente.map[0]) or len(self.reexplorar) > 0:
                if self.maximo_steps(metrica):
                    return False
                if self.tem_bateria_suf():  
                    self.varredura(ambiente,metrica)
                else:
                    self.ir_carregar(ambiente,metrica)
            
            self.limpar = True
            if not self.visitar_celulas_sujas(ambiente, metrica, tipo):
                return False
                
            if ambiente.esta_limpo:
                break
            else:
                self.limpar = False
                for pos, val in self.observados.items():
                    if val != 9:
                        self.reexplorar.add(pos)
                            
        return True

        
    def movimento(self, ambiente, metrica):
        """Processa a ação de mover para a célula atual, contabilizando as métricas e atualizando a visão."""
        if self.maximo_steps(metrica):
             return False
        metrica.movimentos += 1
        print(f"Posição atual: ({self.x}, {self.y})")
        
        if not self.limpar:
            metrica.celulas_visitadas_exploracao.add((self.x, self.y))
            
        ambiente.nova_sujeira()
        self.visao(ambiente,metrica)
        return True
    # def varredura(self,ambiente,metrica):      
    #     if self.direction is None:
    #         self.direction = (1,1)
    #         print(f"Posição atual: ({self.x}, {self.y})")
    #         self.visao(ambiente)
    
    #     viu_parede_no_raio = False
    #     for i in range(1, self.sight_range + 1):
    #         if self.ver_move((self.direction[0] * i, 0)) in ambiente.parede:
    #             viu_parede_no_raio = True
    #             break

    #     if not viu_parede_no_raio:
    #         if not self.tem_bateria_suf():
    #             self.ir_carregar(ambiente, metrica)
    #         self.x += self.direction[0]
    #         self.movimento(ambiente,metrica)
    #     else:
    #         for i in range(self.sight_range+1):
    #             if not self.tem_bateria_suf():
    #                 self.ir_carregar(ambiente, metrica)
    #             if self.ver_move((0,self.direction[1])) not in ambiente.parede:
    #                 self.y += self.direction[1]
    #             elif self.ver_move((0,self.direction[1]*-1)) not in ambiente.parede:
    #                 self.y -= self.direction[1]
    #                 self.direction = (self.direction[0],self.direction[1]*-1)
    #             else:
    #                 break 
    #             self.movimento(ambiente,metrica)
    #         self.direction = (self.direction[0]*-1,self.direction[1])

    def varredura(self, ambiente, metrica):
        self.visao(ambiente)
        melhor_caminho = None
        for posicao,valor in self.observados.items():
            if valor ==9:
                continue
            if not self.revela_nova_area(posicao, ambiente):
                continue
            caminho = self.bfs(ambiente, posicao)
            if caminho is None:
                continue
            if len(caminho) == 0:
                continue
            if melhor_caminho is None or len(caminho) < len(melhor_caminho):
                melhor_caminho = caminho
        if melhor_caminho is None:
            print("Não tem mais caminho para outros lugares")
            return False
        proxima_posicao = melhor_caminho[0]
        novo_x, novo_y = proxima_posicao
        if novo_x != self.x:
            self.x = novo_x
        elif novo_y != self.y:
            self.y = novo_y
        return self.movimento(ambiente, metrica)
    
    def menor_distancia(self, x_destino, y_destino):
        """Calcula a Distância de Manhattan entre a posição atual do robô e o destino."""
        return abs(x_destino - self.x) + abs(y_destino - self.y)

    def tem_bateria_suf(self, aspirar=False):
        """Verifica se o robô possui bateria suficiente para continuar operando e voltar à estação. 
        Se estiver em posição de aspiração, contará também o custo para realiza-lá."""
        custo_retorno = self.menor_distancia(self.estacao_loc[0], self.estacao_loc[1]) * self.consumo_mov
        custo_extra = self.consumo_asp if aspirar else 0
        if self.bateria >= (custo_retorno + custo_extra + 2 * self.consumo_mov):
            return True
        return False

    def ir_carregar(self,ambiente,metrica):
        """Comanda o robô a retornar à estação base para recarregar sua bateria completamente."""
        x_destino, y_destino = self.estacao_loc
        self.walk_to(x_destino,y_destino,ambiente,metrica, indo_carregar=True)
        self.bateria = 100
        metrica.recargas += 1
    
    def walk_to(self,x_destino,y_destino,ambiente,metrica, indo_carregar=False, tipo="ordem"):
        """Navega de forma autônoma até as coordenadas de destino passo a passo utilizando Busca em Largura (BFS). 
        indo_carregar serve para evitar que o robô volte para carregar quando já está indo para a estação."""
        while (self.x, self.y) != (x_destino, y_destino):
            if self.maximo_steps(metrica):
                return False
            if not indo_carregar and not self.tem_bateria_suf():
                    self.ir_carregar(ambiente, metrica)
                    if tipo == "proximidade":
                        return False
            caminho = self.bfs(ambiente, (x_destino, y_destino))
            if caminho is None:
                print("Não há caminho para o destino")
                return False
            if len(caminho) == 0:
                print("Já está no destino")
                return True
            novo_x, novo_y = caminho[0]
            if novo_x != self.x:
                self.x = novo_x
            if novo_y != self.y:
                self.y = novo_y 
            if not self.movimento(ambiente, metrica):
                return False
        return True
        # if x_destino < self.x:
        #         if self.pode_andar(ambiente, (self.x - 1, self.y)):
        #             self.x -= 1
        #         else:
        #             self.desviar(ambiente, (-1, 0))
        #     elif x_destino > self.x:
        #         if self.pode_andar(ambiente, (self.x + 1, self.y)):
        #             self.x += 1
        #         else:
        #             self.desviar(ambiente, (1, 0))
        #     elif y_destino < self.y:
        #         if self.pode_andar(ambiente, (self.x, self.y - 1)):
        #             self.y -= 1
        #         else:
        #             self.desviar(ambiente, (0, -1))
        #     elif y_destino > self.y:
        #         if self.pode_andar(ambiente, (self.x, self.y + 1)):
        #             self.y += 1
        #         else:
        #             self.desviar(ambiente, (0, 1))
        #     if not self.movimento(ambiente, metrica):
        #         return False
        # return True

    def visitar_celulas_sujas(self,ambiente, metrica,tipo):
        """Coordena a limpeza das sujeiras mapeadas usando a estratégia selecionada ('ordem' ou 'proximidade')."""
        if tipo == "ordem":
            print("LIMPANDO POR ORDEM")
            while self.sujos:
                if self.maximo_steps(metrica):
                    return False
                x_destino, y_destino = self.sujos[0]
                if ambiente.map[x_destino][y_destino] != 1:
                    self.sujos.remove((x_destino, y_destino))
                    continue
                if not self.tem_bateria_suf(aspirar=True):
                    self.ir_carregar(ambiente, metrica)
                
              
                if not self.walk_to(x_destino,y_destino,ambiente,metrica):
                    print("Não foi possível chegar à sujeira")
                    if (x_destino, y_destino) in self.sujos:
                        self.sujos.remove((x_destino, y_destino))
                    continue
                if not self.tem_bateria_suf(aspirar=True):
                    self.ir_carregar(ambiente, metrica)
         
                    chegou = self.walk_to(x_destino,y_destino,ambiente,metrica)
                    if not chegou:
                        if(x_destino, y_destino) in self.sujos:
                            self.sujos.remove((x_destino, y_destino))
                self.aspirar(ambiente, metrica)
            return True

        elif tipo == "proximidade":
            print("LIMPANDO POR PROXIMIDADE")
            while self.sujos:

                if self.maximo_steps(metrica):
                    return False

                lista_sujos = []
                
                for x_destino, y_destino in self.sujos:
                    distancia = self.menor_distancia(x_destino, y_destino)
                    lista_sujos.append((distancia, (x_destino, y_destino)))
                
                lista_sujos_ordenada = sorted(lista_sujos, key=lambda x: x[0])
                sujeira_mais_proxima = lista_sujos_ordenada[0]
                sujeira_x, sujeira_y = sujeira_mais_proxima[1]
                if ambiente.map[sujeira_x][sujeira_y] != 1:
                    self.sujos.remove((sujeira_x, sujeira_y))
                    continue
                if not self.tem_bateria_suf(aspirar=True):
                    self.ir_carregar(ambiente, metrica)

                if not self.walk_to(sujeira_x,sujeira_y,ambiente,metrica,tipo=tipo):
                    print("Não foi possível chegar à sujeira")
                    if (sujeira_x, sujeira_y) in self.sujos:
                        self.sujos.remove((sujeira_x, sujeira_y))
                    continue

                if not self.tem_bateria_suf(aspirar=True):
                    self.ir_carregar(ambiente, metrica)
                    continue
                self.aspirar(ambiente, metrica)
            return True
    def pode_andar(self, ambiente, destino):
        """Verifica se as coordenadas de destino não contêm uma parede."""
        x, y = destino
        if destino in ambiente.parede:
            print(f"Parede na frente!")
            return False
        
        return True

    def desviar(self, ambiente,direcao):
        direcao_x, direcao_y = direcao
        if direcao_x != 0:
            if self.pode_andar(ambiente, (self.x, self.y + 1)):
                self.y += 1
                print("parede desviada")
                return True
            elif self.pode_andar(ambiente, (self.x, self.y - 1)):
                self.y -= 1
                print("parede desviada")
                return True
        elif direcao_y != 0:
            if self.pode_andar(ambiente, (self.x + 1, self.y)):
                self.x += 1
                print("parede desviada")
                return True
            elif self.pode_andar(ambiente, (self.x - 1, self.y)):
                self.x -= 1
                print("parede desviada")
                return True
        return False

    def maximo_steps(self,metrica):
        """Verifica se o limite máximo de ações definido para a execução foi atingido."""
        if self.maximo_movimentos is not None and metrica.total_acoes >= self.maximo_movimentos:
            print("maximo de movimentos atingido")
            return True
        return False

    def bfs(self,ambiente, destino):
        """Implementação do algoritmo Busca em Largura (BFS) para encontrar o caminho mais curto até o destino."""
        origem = (self.x, self.y)
        if origem == destino:
            return[]
        fila = deque([origem])
        visitados = {origem: None}

        movimentos = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        while fila:
            atual_x,atual_y = fila.popleft()
            for mov_x, mov_y in movimentos:
                novo_x = atual_x + mov_x
                novo_y = atual_y + mov_y
                novo_destino = (novo_x, novo_y)

                if not (0<= novo_x < len(ambiente.map) and 0 <= novo_y < len(ambiente.map[0])):
                    continue
                if novo_destino in visitados:
                    continue
                if novo_destino not in self.observados:
                    continue
                if self.observados[novo_destino] == 9:
                    continue
                visitados[novo_destino] = (atual_x, atual_y)
                if novo_destino == destino:
                    caminho = []
                    atual = novo_destino
                    while atual!= origem:
                        caminho.append(atual)
                        atual = visitados[atual]
                    caminho.reverse()
                    return caminho
                fila.append(novo_destino)
        return None
    def revela_nova_area(self, posicao, ambiente):
        """Avalia se olhar a partir de uma posição revelará células desconhecidas ou pendentes de re-exploração."""
        x, y = posicao
        for i in range(-self.sight_range, self.sight_range + 1):
            for j in range(-self.sight_range, self.sight_range + 1):
                n_x = x + i
                n_y = y + j

                if (0 <= n_x < len(ambiente.map) and 0 <= n_y < len(ambiente.map[0])):
                    if (n_x, n_y) not in self.observados or (n_x, n_y) in self.reexplorar:
                        return True

        return False        


class Environment:
    def __init__(self, map, cell_dirt_prob = None, semente = None):
        """Inicializa o mapa, contabiliza sujeiras iniciais e configura a semente do gerador aleatório."""
        self.map = map
        self.__sujeiras_inicio = 0
        self.__parede = []
        self.probabilidade_sujeira = cell_dirt_prob

        for i in self.map:
            self.__sujeiras_inicio += i.count(1)
        if semente is not None: 
            random.seed(semente)

    @property 
    def parede(self):
        """Retorna uma lista contendo as bordas (paredes invisíveis) que limitam a grade do mapa."""
        if not self.__parede:
            map = self.map
            for i in range(len(map)):
                self.__parede.append((i,-1))
                self.__parede.append((i,len(map[0])))
            for i in range(len(map[0])):
                self.__parede.append((-1,i))
                self.__parede.append((len(map),i))
        return self.__parede

    @property
    def sujeira(self):
        """Retorna a contagem exata de sujeiras presentes no mapa no momento de sua criação."""
        return self.__sujeiras_inicio
    
    def nova_sujeira(self):
        """Gera aleatoriamente uma nova sujeira em uma célula vazia do mapa baseada na probabilidade."""
        if self.probabilidade_sujeira is not None:
            if random.random() < self.probabilidade_sujeira:    
                while True:
                    x = random.randint(0, len(self.map) - 1)
                    y = random.randint(0, len(self.map[0]) - 1)
                    if self.map[x][y] == 0:
                        self.map[x][y] = 1
                        print(f"Nova sujeira gerada na posição ({x}, {y})")
                        break

    @property
    def esta_limpo(self):
        """Avalia o mapa inteiro e retorna True se todas as sujeiras (células iguais a 1) foram removidas.
        Serve para garantir que o programa continuará enquanto houver movimentos disponíveis."""
        return sum(linha.count(1) for linha in self.map) == 0

class Metrics:
    def __init__(self):
        """Inicializa os contadores para movimentos, aspirações, recargas e células visitadas/sujas."""
        self.__movimentos = 0
        self.__aspiracoes = 0
        self.__total_acoes = 0
        self.__celulas_sujas_iniciais = 0
        self.__celulas_limpas = 0
        self.__recargas = 0
        self.celulas_visitadas_exploracao = set()

    @property
    def movimentos(self):
        return self.__movimentos
    
    @movimentos.setter
    def movimentos(self, val):
        self.__movimentos = val
    
    @property
    def aspiracoes(self):
        return self.__aspiracoes
    
    @aspiracoes.setter
    def aspiracoes(self, val):
        self.__aspiracoes = val
    
    @property
    def total_acoes(self):
        self.__total_acoes = self.movimentos + self.aspiracoes
        return self.__total_acoes

    @property
    def celulas_sujas_iniciais(self):
        return self.__celulas_sujas_iniciais
    
    @celulas_sujas_iniciais.setter
    def celulas_sujas_iniciais(self, val):
        self.__celulas_sujas_iniciais = val
    
    @property
    def celulas_limpas(self):
        return self.__celulas_limpas
    
    @celulas_limpas.setter
    def celulas_limpas(self, val):
        self.__celulas_limpas = val
    
    @property
    def recargas(self):
        return self.__recargas
        
    @recargas.setter
    def recargas(self, val):
        self.__recargas = val
        
    def celulas_sujas_restantes(self,robozin):
        """Retorna quantas sujeiras o robô ainda sabe que precisam ser limpas em sua memória."""
        return robozin.qttsujos()

    