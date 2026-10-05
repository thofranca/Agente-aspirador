import random
class Robot:
    def __init__(self, start, sight_range, cons_mov, cons_asp, estacao_loc=(0,0), max_steps=None):
        self.__x = start[0]
        self.__y = start[1]
        self.direction = None
        self.sight_range = sight_range
        self.observados = {}
        self.sujos = []
        self.limpar = False
        self.bateria = 100
        self.consumo_mov = cons_mov
        self.consumo_asp = cons_asp
        self.estacao_loc = estacao_loc
        self.maximo_movimentos = max_steps
    @property
    def x(self):
        return self.__x
        
    @x.setter
    def x(self, val):
        self.__x = val
        self.bateria -= self.consumo_mov
        
    @property 
    def y(self):
        return self.__y
        
    @y.setter
    def y(self, val):
        self.__y = val
        self.bateria -= self.consumo_mov

    def ver_move(self, direction):
        return (self.x+direction[0],self.y+direction[1])

    # def pos_aleat(self,ambiente):
    #     while True:
    #         if self.x != 0:
    #             self.x -= 1
    #         elif self.y != 0:
    #             self.y -= 1
    #         if (self.x,self.y) not in self.visited and (self.x,self.y) not in ambiente.parede:
    #             break
            
    def aspirar(self, ambiente, metrica):
        if self.maximo_steps(metrica):
            return False
        if ambiente.map[self.x][self.y] == 1:
            print(f"Sujeira encontrada na posição ({self.x}, {self.y})")
            print("Aspirando...")
            ambiente.map[self.x][self.y] = 0
            self.bateria -= self.consumo_asp
            metrica.aspiracoes += 1
            metrica.celulas_limpas += 1

    def visao(self, ambiente):
        for i in range(-self.sight_range,self.sight_range+1):
            for j in range(-self.sight_range,self.sight_range+1):
                n_x = self.x+i
                n_y = self.y+j
                if 0 <= n_x < len(ambiente.map) and 0 <= n_y < len(ambiente.map[0]):
                    if (n_x,n_y) not in self.observados:
                        self.observados[(n_x, n_y)] = ambiente.map[n_x][n_y]
                        if ambiente.map[n_x][n_y] == 1:
                            self.sujos.append((n_x, n_y))
                        if ambiente.map[n_x][n_y] == 9:
                            if(n_x,n_y) not in ambiente.parede:
                                ambiente.parede.append((n_x,n_y))
                     
    def limpeza(self, ambiente, metrica,tipo):
        while len(self.observados) < len(ambiente.map)*len(ambiente.map[0]):
            if self.maximo_steps(metrica):
                return False
            if self.tem_bateria_suf():  
                self.varredura(ambiente,metrica)
            else:
                self.ir_carregar(ambiente,metrica)
        self.limpar = True
        self.visitar_celulas_sujas(ambiente, metrica, tipo)

        
    def movimento(self, ambiente, metrica):
        if self.maximo_steps(metrica):
             return False
        metrica.movimentos += 1
        print(f"Posição atual: ({self.x}, {self.y})")
        self.visao(ambiente) if not self.limpar else None
        ambiente.nova_sujeira()
        return True
    def varredura(self,ambiente,metrica):      
        if self.direction is None:
            self.direction = (1,1)
            print(f"Posição atual: ({self.x}, {self.y})")
            self.visao(ambiente)
    
        viu_parede_no_raio = False
        for i in range(1, self.sight_range + 1):
            if self.ver_move((self.direction[0] * i, 0)) in ambiente.parede:
                viu_parede_no_raio = True
                break

        if not viu_parede_no_raio:
            if not self.tem_bateria_suf():
                self.ir_carregar(ambiente, metrica)
            self.x += self.direction[0]
            self.movimento(ambiente,metrica)
        else:
            for i in range(self.sight_range+1):
                if not self.tem_bateria_suf():
                    self.ir_carregar(ambiente, metrica)
                if self.ver_move((0,self.direction[1])) not in ambiente.parede:
                    self.y += self.direction[1]
                elif self.ver_move((0,self.direction[1]*-1)) not in ambiente.parede:
                    self.y -= self.direction[1]
                    self.direction = (self.direction[0],self.direction[1]*-1)
                else:
                    break 
                self.movimento(ambiente,metrica)
            self.direction = (self.direction[0]*-1,self.direction[1])

    def menor_distancia(self, x_destino, y_destino):
        return abs(x_destino - self.x) + abs(y_destino - self.y)

    def tem_bateria_suf(self, aspirar=False):
        custo_retorno = self.menor_distancia(self.estacao_loc[0], self.estacao_loc[1]) * self.consumo_mov
        custo_extra = self.consumo_asp if aspirar else 0
        if self.bateria >= (custo_retorno + custo_extra + 2 * self.consumo_mov):
            return True
        return False

    def ir_carregar(self,ambiente,metrica):
        x_destino, y_destino = self.estacao_loc
        self.walk_to(x_destino,y_destino,ambiente,metrica, indo_carregar=True)
        self.bateria = 100
    
    def walk_to(self,x_destino,y_destino,ambiente,metrica, indo_carregar=False, tipo="ordem"):
        while (self.x, self.y) != (x_destino, y_destino):
            if not indo_carregar and not self.tem_bateria_suf():
                self.ir_carregar(ambiente, metrica)
                if tipo == "proximidade":
                    return False
            if x_destino < self.x:
                if self.pode_andar(ambiente, (self.x - 1, self.y)):
                    self.x -= 1
                else:
                    self.desviar(ambiente, (-1, 0))
            elif x_destino > self.x:
                if self.pode_andar(ambiente, (self.x + 1, self.y)):
                    self.x += 1
                else:
                    self.desviar(ambiente, (1, 0))
            elif y_destino < self.y:
                if self.pode_andar(ambiente, (self.x, self.y - 1)):
                    self.y -= 1
                else:
                    self.desviar(ambiente, (0, -1))
            elif y_destino > self.y:
                if self.pode_andar(ambiente, (self.x, self.y + 1)):
                    self.y += 1
                else:
                    self.desviar(ambiente, (0, 1))
            if not self.movimento(ambiente, metrica):
                return False
        return True

    def visitar_celulas_sujas(self,ambiente, metrica,tipo):
        if tipo == "ordem":
            print("LIMPANDO POR ORDEM")
            for i in self.sujos:
                x_destino, y_destino = i
                self.walk_to(x_destino,y_destino,ambiente,metrica)
                if not self.tem_bateria_suf(aspirar=True):
                    self.ir_carregar(ambiente, metrica)
                    self.walk_to(x_destino,y_destino,ambiente,metrica)
                self.aspirar(ambiente, metrica)

        elif tipo == "proximidade":
            print("LIMPANDO POR PROXIMIDADE")
            while self.sujos:
                lista_sujos = []
                
                for x_destino, y_destino in self.sujos:
                    distancia = self.menor_distancia(x_destino, y_destino)
                    lista_sujos.append((distancia, (x_destino, y_destino)))
                
                lista_sujos_ordenada = sorted(lista_sujos, key=lambda x: x[0])
                sujeira_mais_proxima = lista_sujos_ordenada[0]
                
                sujeira_x, sujeira_y = sujeira_mais_proxima[1]
                chegou = self.walk_to(sujeira_x,sujeira_y,ambiente,metrica,tipo=tipo)
                if not chegou:
                    continue
                if not self.tem_bateria_suf(aspirar=True):
                    self.ir_carregar(ambiente, metrica)
                    continue
                self.aspirar(ambiente, metrica)
                self.sujos.remove((sujeira_x, sujeira_y))
    def pode_andar(self, ambiente, destino):
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
        if metrica.total_acoes >= self.maximo_movimentos:
            print("maximo de movimentos atingido")
            return True
        return False
    
class Environment:
    def __init__(self, map, cell_dirt_prob = None, semente = None):
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
        return self.__sujeiras_inicio
    
    def nova_sujeira(self):
        if self.probabilidade_sujeira is not None:
            if random.random() < self.probabilidade_sujeira:    
                while True:
                    x = random.randint(0, len(self.map) - 1)
                    y = random.randint(0, len(self.map[0]) - 1)
                    if self.map[x][y] == 0:
                        self.map[x][y] = 1
                        print(f"Nova sujeira gerada na posição ({x}, {y})")
                        break

            
class Metrics:
    def __init__(self):
        self.__movimentos = 0
        self.__aspiracoes = 0
        self.__total_acoes = 0
        self.__celulas_sujas_iniciais = 0
        self.__celulas_limpas = 0
        self.__celulas_sujas_restantes = 0

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
    def celulas_sujas_restantes(self):
        return self.celulas_sujas_iniciais - self.celulas_limpas

    