# -*- coding: utf-8 -*-


import pygame
import random
import heapq
import numpy as np
from collections import deque
import os

script_dir = os.path.dirname(os.path.abspath(__file__))


BLOCKTYPES = 5


# třída reprezentující prostředí
class Env:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.arr = np.zeros((height, width), dtype=int)
        self.startx = 0
        self.starty = 0
        self.goalx = width-1
        self.goaly = height-1
        
    def is_valid_xy(self, x, y):      
        if x >= 0 and x < self.width and y >= 0 and y < self.height and self.arr[y, x] == 0:
            return True
        return False 
        
    def set_start(self, x, y):
        if self.is_valid_xy(x, y):
            self.startx = x
            self.starty = y
            
    def set_goal(self, x, y):
        if self.is_valid_xy(x, y):
            self.goalx = x
            self.goaly = y
               
        
    def is_empty(self, x, y):
        if self.arr[y, x] == 0:
            return True
        return False
    
        
    def add_block(self, x, y):
        if self.arr[y, x] == 0:
            r = random.randint(1, BLOCKTYPES)
            self.arr[y, x] = r
                
    def get_neighbors(self, x, y):
        l = []
        if x-1 >= 0 and self.arr[y, x-1] == 0:
            l.append((x-1, y))
        
        if x+1 < self.width and self.arr[y, x+1] == 0:
            l.append((x+1, y))
            
        if y-1 >= 0 and self.arr[y-1, x] == 0:
            l.append((x, y-1))
        
        if y+1 < self.height and self.arr[y+1, x] == 0:
            l.append((x, y+1))
        
        return l
        
     
    def get_tile_type(self, x, y):
        return self.arr[y, x]
    
    def manhattan_distance(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    
    def reconstruct_path(self, came_from, current):
        path = deque()
        while current is not None:
            path.appendleft(current)
            current = came_from.get(current)
        return path
    
    # vrací trojici: 1. frontu dvojic ze startu do cíle, 2. seznam expandovaných uzlů, 3. seznam uzlů finální cesty
    # start a cíl se nastaví pomocí set_start a set_goal
    def path_planner(self):
        start = (self.startx, self.starty)
        goal = (self.goalx, self.goaly)
        
        # VÝBĚR AKTIVNÍHO ALGORITMU
        # zbývající dva zůstávají zakomentované
        #---------------------------------------------------
        return self.greedy_best_first_search(start, goal)
        # return self.dijkstra(start, goal)
        # return self.a_star(start, goal)
    
    # algoritmus Greedy BFS - používá jen heuristiku
    def greedy_best_first_search(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        expanded_nodes = []
        
        while frontier:
            current_priority, current = heapq.heappop(frontier)
            expanded_nodes.append(current)
            
            if current == goal:
                path = self.reconstruct_path(came_from, current)
                path_list = list(path)
                return path, expanded_nodes, path_list
            
            for neighbor in self.get_neighbors(current[0], current[1]):
                if neighbor not in came_from:
                    priority = self.manhattan_distance(neighbor[0], neighbor[1], goal[0], goal[1])
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current
        
        return deque(), expanded_nodes, []
    
    # algoritmus Dijkstra - používá skutečnou vzdálenost od startu
    def dijkstra(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        expanded_nodes = []
        
        while frontier:
            current_cost, current = heapq.heappop(frontier)
            expanded_nodes.append(current)
            
            if current == goal:
                path = self.reconstruct_path(came_from, current)
                path_list = list(path)
                return path, expanded_nodes, path_list
            
            for neighbor in self.get_neighbors(current[0], current[1]):
                new_cost = cost_so_far[current] + 1  # každý krok má cenu 1
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current
        
        return deque(), expanded_nodes, []
    
    # algoritmus A* - kombinuje skutečnou vzdálenost a heuristiku
    def a_star(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        expanded_nodes = []
        
        while frontier:
            current_priority, current = heapq.heappop(frontier)
            expanded_nodes.append(current)
            
            if current == goal:
                path = self.reconstruct_path(came_from, current)
                path_list = list(path)
                return path, expanded_nodes, path_list
            
            for neighbor in self.get_neighbors(current[0], current[1]):
                new_cost = cost_so_far[current] + 1  # každý krok má cenu 1
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heuristic = self.manhattan_distance(neighbor[0], neighbor[1], goal[0], goal[1])
                    priority = new_cost + heuristic  # f(n) = g(n) + h(n)
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current
        
        return deque(), expanded_nodes, []
    
       
        
# třída reprezentující ufo        
class Ufo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.path = deque()
        self.expanded_tiles = []
        self.path_tiles = []
    
   
    # přemístí ufo na danou pozici - nejprve je dobré zkontrolovat u prostředí, 
    # zda je pozice validní
    def move(self, x, y):
        self.x = x
        self.y = y

   
    
    # reaktivní navigace
    def reactive_go(self, env):
        r = random.random()
        
        dx = 0
        dy = 0
        
        if r > 0.5: 
            r = random.random()
            if r < 0.5:
                dx = -1
            else:
                dx = 1
            
        else:
            r = random.random()
            if r < 0.5:
                dy = -1
            else:
                dy = 1
        
        return (self.x + dx, self.y + dy)
        
    
    # nastaví cestu k vykonání 
    def set_path(self, p, expanded=[], path_nodes=[]):
        self.path = p
        self.expanded_tiles = expanded
        self.path_tiles = path_nodes
   
    
    # vykoná naplánovanou cestu, v každém okamžiku na vyzvání vydá další
    # way point 
    def execute_path(self):
        if self.path:
            return self.path.popleft()
        return (-1, -1)
       




# definice prostředí -----------------------------------

TILESIZE = 50



#<------    definice prostředí a překážek !!!!!!

WIDTH = 12
HEIGHT = 9

env = Env(WIDTH, HEIGHT)

env.add_block(1, 1)
env.add_block(2, 2)
env.add_block(3, 3)
env.add_block(4, 4)
env.add_block(5, 5)
env.add_block(6, 6)
env.add_block(7, 7)
env.add_block(8, 8)
env.add_block(0, 8)

env.add_block(11, 1)
env.add_block(11, 6)
env.add_block(1, 3)
env.add_block(2, 4)
env.add_block(4, 5)
env.add_block(2, 6)
env.add_block(3, 7)
env.add_block(4, 8)
env.add_block(0, 8)


env.add_block(1, 8)
env.add_block(2, 8)
env.add_block(3, 5)
env.add_block(4, 8)
env.add_block(5, 6)
env.add_block(6, 4)
env.add_block(7, 2)
env.add_block(8, 1)


# pozice ufo <--------------------------
ufo = Ufo(env.startx, env.starty)

WIN = pygame.display.set_mode((env.width * TILESIZE, env.height * TILESIZE))

pygame.display.set_caption("Block world")

pygame.font.init()

WHITE = (255, 255, 255)



FPS = 2



# pond, tree, house, car

BOOM_FONT = pygame.font.SysFont("comicsans", 100)   
LEVEL_FONT = pygame.font.SysFont("comicsans", 20)   


TILE_IMAGE = pygame.image.load(os.path.join(script_dir, "tile.jpg"))
MTILE_IMAGE = pygame.image.load(os.path.join(script_dir, "markedtile.jpg"))
ETILE_IMAGE = pygame.image.load(os.path.join(script_dir, "markedtile2.jpg"))  # expanded-tile pro expandované uzly
HOUSE1_IMAGE = pygame.image.load(os.path.join(script_dir, "house1.jpg"))
HOUSE2_IMAGE = pygame.image.load(os.path.join(script_dir, "house2.jpg"))
HOUSE3_IMAGE = pygame.image.load(os.path.join(script_dir, "house3.jpg"))
TREE1_IMAGE  = pygame.image.load(os.path.join(script_dir, "tree1.jpg"))
TREE2_IMAGE  = pygame.image.load(os.path.join(script_dir, "tree2.jpg"))
UFO_IMAGE = pygame.image.load(os.path.join(script_dir, "ufo.jpg"))
FLAG_IMAGE = pygame.image.load(os.path.join(script_dir, "flag.jpg"))


TILE = pygame.transform.scale(TILE_IMAGE, (TILESIZE, TILESIZE))
MTILE = pygame.transform.scale(MTILE_IMAGE, (TILESIZE, TILESIZE))
EXPANDED_TILE = pygame.transform.scale(ETILE_IMAGE, (TILESIZE, TILESIZE))
HOUSE1 = pygame.transform.scale(HOUSE1_IMAGE, (TILESIZE, TILESIZE))
HOUSE2 = pygame.transform.scale(HOUSE2_IMAGE, (TILESIZE, TILESIZE))
HOUSE3 = pygame.transform.scale(HOUSE3_IMAGE, (TILESIZE, TILESIZE))
TREE1 = pygame.transform.scale(TREE1_IMAGE, (TILESIZE, TILESIZE))
TREE2 = pygame.transform.scale(TREE2_IMAGE, (TILESIZE, TILESIZE))
UFO = pygame.transform.scale(UFO_IMAGE, (TILESIZE, TILESIZE))
FLAG = pygame.transform.scale(FLAG_IMAGE, (TILESIZE, TILESIZE))




        
        
        

def draw_window(ufo, env):

    for i in range(env.width):
        for j in range(env.height):
            t = env.get_tile_type(i, j)
            if t == 1:
                WIN.blit(TREE1, (i*TILESIZE, j*TILESIZE))
            elif t == 2:
                WIN.blit(HOUSE1, (i*TILESIZE, j*TILESIZE))
            elif t == 3:
                WIN.blit(HOUSE2, (i*TILESIZE, j*TILESIZE))
            elif t == 4:
                WIN.blit(HOUSE3, (i*TILESIZE, j*TILESIZE))  
            elif t == 5:
                WIN.blit(TREE2, (i*TILESIZE, j*TILESIZE))     
            else:
                WIN.blit(TILE, (i*TILESIZE, j*TILESIZE))
    
    # vykreslení expandovaných uzlů (světle modrá)
    for (x, y) in ufo.expanded_tiles:
        if (x, y) not in ufo.path_tiles:  # kromě těch, které jsou součástí finální cesty
            WIN.blit(EXPANDED_TILE, (x*TILESIZE, y*TILESIZE))
    
    # vykreslení finální cesty (žlutá)
    for (x, y) in ufo.path_tiles:
        WIN.blit(MTILE, (x*TILESIZE, y*TILESIZE))
        
    
    WIN.blit(FLAG, (env.goalx * TILESIZE, env.goaly * TILESIZE))        
    WIN.blit(UFO, (ufo.x * TILESIZE, ufo.y * TILESIZE))
        
    pygame.display.update()
    
    
    

def main():
    
    
    #  <------------   nastavení startu a cíle prohledávání !!!!!!!!!!
    env.set_start(0, 0)
    env.set_goal(9, 7)
    
    
    p, expanded, path_nodes = env.path_planner()   # cesta pomocí path_planneru prostředí
    ufo.set_path(p, expanded, path_nodes)
    
    print(f"Nalezena cesta s délkou: {len(p)} kroků")
    print(f"Počet expandovaných uzlů: {len(expanded)}")
    print(f"Výčet uzlů nalezené cesty:")
    # ---------------------------------------------------
    
    
    clock = pygame.time.Clock()
    
    run = True
    go = False    
    
    while run:  
        
        clock.tick(FPS)
        

        # <---- reaktivní pohyb dokud nedojde do cíle 
        if (ufo.x != env.goalx) or (ufo.y != env.goaly):        
            #x, y = ufo.reactive_go(env)
            
            x, y = ufo.execute_path()  # už ne reaktivní, použijeme path_planner
            
            print('[', x, ',', y, ']')
            
            if env.is_valid_xy(x, y):
                ufo.move(x, y)
            else:
                print('[', x, ',', y, ']', "wrong coordinate !")
        

                        
        draw_window(ufo, env)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    
    pygame.quit()    


if __name__ == "__main__":
    main()