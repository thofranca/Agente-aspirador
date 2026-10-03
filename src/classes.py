class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = []

    @property
    def get_x(self):
        return self.x
    
    @property 
    def get_y(self):
        return self.y
    
    def move(self, direction):
        return (self.x+direction[0],self.y+direction[1])

    def varredura(self, ambiente):
        if self.move((1,0)) not in ambiente.parede and self.move((1,0)) not in self.visited:
            self.x += 1
            self.visited.append((self.x,self.y))
        elif self.move((-1,0)) not in ambiente.parede and self.move((-1,0)) not in self.visited:
            self.x -= 1
            self.visited.append((self.x,self.y))
        elif self.move((0,1)) not in ambiente.parede and self.move((0,1)) not in self.visited:
            self.y += 1
            self.visited.append((self.x,self.y))
        elif self.move((0,-1)) not in ambiente.parede and self.move((0,-1)) not in self.visited:
            self.y -= 1
            self.visited.append((self.x,self.y))
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
    
    

    