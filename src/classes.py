import select
class Robot:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.direction = None
        self.visited = []

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

    def move(self, direction):
        return (self.x+direction[0],self.y+direction[1])

    # def pos_aleat(self,ambiente):
    #     while True:
    #         if self.x != 0:
    #             self.x -= 1
    #         elif self.y != 0:
    #             self.y -= 1
    #         if (self.x,self.y) not in self.visited and (self.x,self.y) not in ambiente.parede:
    #             break
            

    def varredura(self, ambiente):
        if self.direction is None:
            self.visited.append((self.x,self.y))
            print(f"Posição atual: ({self.x}, {self.y})")
            self.ver_sujeira(ambiente)
            self.x += 1
            self.direction = (1,1)
            self.visited.append((self.x,self.y))
            
        elif self.move((self.direction[0],0)) not in ambiente.parede:
            self.x += self.direction[0]
            self.visited.append((self.x,self.y)) if (self.x,self.y) not in self.visited else None
        else:
            if self.move((0,self.direction[1])) not in ambiente.parede:
                self.y += self.direction[1]
                self.direction = (self.direction[0]*-1,self.direction[1])
                self.visited.append((self.x,self.y)) if (self.x,self.y) not in self.visited else None
            elif self.move((0,self.direction[1]*-1)) not in ambiente.parede:
                self.y -= self.direction[1]
                self.direction = (self.direction[0]*-1,self.direction[1]*-1)
                self.visited.append((self.x,self.y)) if (self.x,self.y) not in self.visited else None

        print(f"Posição atual: ({self.x}, {self.y})")
        self.ver_sujeira(ambiente)

    def ver_sujeira(self, ambiente):
        if ambiente.map[self.x][self.y] == 1:
            print(f"Sujeira encontrada na posição ({self.x}, {self.y})")
            print("Aspirando...")
            ambiente.map[self.x][self.y] = 0
    
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
    
    

    