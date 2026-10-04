class Robot:
    def __init__(self, start, sight_range):
        self.__x = start[0]
        self.__y = start[1]
        self.direction = None
        self.sight_range = sight_range
        self.observados = {}
        self.sujos = []
        self.limpar = False

    @property
    def x(self):
        return self.__x
        
    @x.setter
    def x(self, val):
        self.__x = val
        
    @property 
    def y(self):
        return self.__y
        
    @y.setter
    def y(self, val):
        self.__y = val

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
        if ambiente.map[self.x][self.y] == 1:
            print(f"Sujeira encontrada na posição ({self.x}, {self.y})")
            print("Aspirando...")
            ambiente.map[self.x][self.y] = 0
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



    def limpeza(self, ambiente, metrica,tipo):
        while len(self.observados) < len(ambiente.map)*len(ambiente.map[0]):
            self.varredura(ambiente,metrica)
        self.limpar = True
        self.visitar_celulas_sujas(ambiente, metrica, tipo)

        
    def movimento(self, ambiente, metrica):
        print(f"Posição atual: ({self.x}, {self.y})")
        self.visao(ambiente) if not self.limpar else None

    def varredura(self,ambiente,metrica):      
        if self.direction is None:
            self.direction = (1,1)
            self.movimento(ambiente,metrica)
            

        if self.ver_move((self.direction[0],0)) not in ambiente.parede:
            self.x += self.direction[0]
            metrica.movimentos += 1
            self.movimento(ambiente,metrica)
        else:
            for i in range(self.sight_range+1):
                if self.ver_move((0,self.direction[1])) not in ambiente.parede:
                    self.y += self.direction[1]
                elif self.ver_move((0,self.direction[1]*-1)) not in ambiente.parede:
                    self.y -= self.direction[1]
                    self.direction = (self.direction[0],self.direction[1]*-1)
                else:
                    break 
                metrica.movimentos += 1
                self.movimento(ambiente,metrica)
            self.direction = (self.direction[0]*-1,self.direction[1])

    def visitar_celulas_sujas(self,ambiente, metrica,tipo):
        if tipo == "ordem":
            print("LIMPANDO POR ORDEM")
            for i in self.sujos:
                x_destino, y_destino = i
                while (self.x, self.y) != (x_destino, y_destino):
                    if x_destino < self.x:
                        self.x -= 1
                        metrica.movimentos += 1
                    elif x_destino > self.x:
                        self.x += 1
                        metrica.movimentos += 1
                    elif y_destino < self.y:
                        self.y -= 1
                        metrica.movimentos += 1
                    elif y_destino > self.y:
                        self.y += 1 
                        metrica.movimentos += 1
                print(ambiente.map)
                self.aspirar(ambiente, metrica)
                print(ambiente.map)

        elif tipo == "proximidade":
            print("LIMPANDO POR PROXIMIDADE")
            lista_sujos = []
            i = 0
            while self.sujos:

                for x_destino, y_destino in self.sujos:
                    distancia_x, distancia_y = abs(x_destino - self.x), abs(y_destino - self.y)
                    lista_sujos.append((distancia_x + distancia_y, (x_destino, y_destino)))
                    lista_sujos_ordenada = sorted(lista_sujos, key=lambda x: x[0])
                    
                    sujeira = lista_sujos_ordenada[0]
                    sujeira_x, sujeira_y = sujeira[1]
                    self.sujos.remove((sujeira_x, sujeira_y))

                    while (self.x, self.y) != (sujeira_x, sujeira_y):
                            if x_destino < self.x:
                                self.x -= 1
                                metrica.movimentos += 1
                            elif x_destino > self.x:
                                self.x += 1
                                metrica.movimentos += 1
                            elif y_destino < self.y:
                                self.y -= 1
                                metrica.movimentos += 1
                            elif y_destino > self.y:
                                self.y += 1 
                                metrica.movimentos += 1
                    print(ambiente.map)
                    self.aspirar(ambiente, metrica)
                    print(ambiente.map)
                    lista_sujos = []
            
class Environment:
    def __init__(self, map):
        self.map = map
        self.__sujeiras_inicio = 0
        self.__parede = []
        for i in self.map:
            self.__sujeiras_inicio += i.count(1)

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
        return self.movimentos + self.aspiracoes
    
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

    