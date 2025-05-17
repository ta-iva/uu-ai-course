# -*- coding: utf-8 -*-


import pygame
import numpy as np
import random
import math
import os


from deap import base
from deap import creator
from deap import tools


pygame.font.init()

script_dir = os.path.dirname(os.path.abspath(__file__))


#-----------------------------------------------------------------------------
# Parametry hry 
#-----------------------------------------------------------------------------

WIDTH, HEIGHT = 900, 500

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)


TITLE = "Boom Master"
pygame.display.set_caption(TITLE)

FPS = 80
ME_VELOCITY = 5
MAX_MINE_VELOCITY = 3



BOOM_FONT = pygame.font.SysFont("comicsans", 100)   
LEVEL_FONT = pygame.font.SysFont("comicsans", 20)   



ENEMY_IMAGE  = pygame.image.load(os.path.join(script_dir, "mine.png"))
ME_IMAGE = pygame.image.load(os.path.join(script_dir, "me.png"))
SEA_IMAGE = pygame.image.load(os.path.join(script_dir, "sea.png"))
FLAG_IMAGE = pygame.image.load(os.path.join(script_dir, "flag.png"))


ENEMY_SIZE = 50
ME_SIZE = 50

ENEMY = pygame.transform.scale(ENEMY_IMAGE, (ENEMY_SIZE, ENEMY_SIZE))
ME = pygame.transform.scale(ME_IMAGE, (ME_SIZE, ME_SIZE))
SEA = pygame.transform.scale(SEA_IMAGE, (WIDTH, HEIGHT))
FLAG = pygame.transform.scale(FLAG_IMAGE, (ME_SIZE, ME_SIZE))






# ----------------------------------------------------------------------------
# třídy objektů 
# ----------------------------------------------------------------------------

# trida reprezentujici minu
class Mine:
    def __init__(self):

        # random x direction
        if random.random() > 0.5:
            self.dirx = 1
        else: 
            self.dirx = -1
            
        # random y direction    
        if random.random() > 0.5:
            self.diry = 1
        else: 
            self.diry = -1

        x = random.randint(200, WIDTH - ENEMY_SIZE) 
        y = random.randint(200, HEIGHT - ENEMY_SIZE) 
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        
        self.velocity = random.randint(1, MAX_MINE_VELOCITY)
        
  
    
  
# trida reprezentujici me, tedy meho agenta        
class Me:
    def __init__(self):
        self.rect = pygame.Rect(10, random.randint(1, 300), ME_SIZE, ME_SIZE)  
        self.alive = True
        self.won = False
        self.timealive = 0
        self.sequence = []
        self.fitness = 0
        self.dist = 0
    
    
# třída reprezentující cíl = praporek    
class Flag:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - ME_SIZE, HEIGHT - ME_SIZE - 10, ME_SIZE, ME_SIZE)
        

# třída reprezentující nejlepšího jedince - hall of fame   
class Hof:
    def __init__(self):
        self.sequence = []
        
    
    
# -----------------------------------------------------------------------------    
# nastavení herního plánu    
#-----------------------------------------------------------------------------
    

# rozestavi miny v danem poctu num
def set_mines(num):
    l = []
    for i in range(num):
        m = Mine()
        l.append(m)
        
    return l
    

# inicializuje me v poctu num na start 
def set_mes(num):
    l = []
    for i in range(num):
        m = Me()
        l.append(m)
        
    return l

# zresetuje vsechny mes zpatky na start
def reset_mes(mes, pop):
    for i in range(len(pop)):
        me = mes[i]
        me.rect.x = 10
        me.rect.y = 10
        me.alive = True
        me.dist = 0
        me.won = False
        me.timealive = 0
        me.sequence = pop[i]
        me.fitness = 0



    

# -----------------------------------------------------------------------------    
# senzorické funkce - DOPLNĚNO
# -----------------------------------------------------------------------------    

# detekce vzdálenosti k nejbližší mině
def nearest_mine_distance(me, mines):
    if not mines:
        return 1.0  # Maximální hodnota, žádná mina ve hře
    
    min_dist = float('inf')
    for mine in mines:
        dist = math.sqrt((me.rect.x - mine.rect.x)**2 + (me.rect.y - mine.rect.y)**2)
        if dist < min_dist:
            min_dist = dist
    
    # normalizace vzdálenosti na rozsah 0-1
    max_possible_dist = math.sqrt(WIDTH**2 + HEIGHT**2)
    normalized_dist = min_dist / max_possible_dist
    
    return normalized_dist

# detekce vzdálenosti k cíli (praporku)
def flag_distance(me, flag):
    dist = math.sqrt((me.rect.x - flag.rect.x)**2 + (me.rect.y - flag.rect.y)**2)
    
    # Normalizace vzdálenosti na rozsah 0-1
    max_possible_dist = math.sqrt(WIDTH**2 + HEIGHT**2)
    normalized_dist = dist / max_possible_dist
    
    return normalized_dist

# detekce nebezpečí shora
def danger_up(me, mines, distance=100):
    for mine in mines:
        if (abs(me.rect.x - mine.rect.x) < ENEMY_SIZE and 
            mine.rect.y < me.rect.y and 
            me.rect.y - mine.rect.y < distance):
            return 1.0  # Nebezpečí detekováno
    return 0.0  # Bezpečno

# detekce nebezpečí zdola
def danger_down(me, mines, distance=100):
    for mine in mines:
        if (abs(me.rect.x - mine.rect.x) < ENEMY_SIZE and 
            mine.rect.y > me.rect.y and 
            mine.rect.y - me.rect.y < distance):
            return 1.0
    return 0.0

# detekce nebezpečí zleva
def danger_left(me, mines, distance=100):
    for mine in mines:
        if (abs(me.rect.y - mine.rect.y) < ENEMY_SIZE and 
            mine.rect.x < me.rect.x and 
            me.rect.x - mine.rect.x < distance):
            return 1.0
    return 0.0

# detekce nebezpečí zprava
def danger_right(me, mines, distance=100):
    for mine in mines:
        if (abs(me.rect.y - mine.rect.y) < ENEMY_SIZE and 
            mine.rect.x > me.rect.x and 
            mine.rect.x - me.rect.x < distance):
            return 1.0
    return 0.0

# normalizovaná pozice X
def position_x(me):
    return me.rect.x / WIDTH

# normalizovaná pozice Y
def position_y(me):
    return me.rect.y / HEIGHT

# původní senzor
def my_senzor(me):
    return 1





# ---------------------------------------------------------------------------
# funkce řešící pohyb agentů
# ----------------------------------------------------------------------------


# kontroluje kolizi 1 agenta s minama, pokud je kolize, vraci True
def me_collision(me, mines):    
    for mine in mines:
        if me.rect.colliderect(mine.rect):
            #pygame.event.post(pygame.event.Event(ME_HIT))
            return True
    return False
            
            
# kolidujici agenti jsou zabiti, a jiz se nebudou vykreslovat
def mes_collision(mes, mines):
    for me in mes: 
        if me.alive and not me.won:
            if me_collision(me, mines):
                me.alive = False
            
            
# vraci True, pokud jsou vsichni mrtvi, Dave :-))          
def all_dead(mes):    
    for me in mes: 
        if me.alive:
            return False
    
    return True


# vrací True, pokud již nikdo nehraje - mes jsou mrtví nebo v cíli
def nobodys_playing(mes):
    for me in mes: 
        if me.alive and not me.won:
            return False
    
    return True


# rika, zda agent dosel do cile
def me_won(me, flag):
    if me.rect.colliderect(flag.rect):
        return True
    
    return False


# vrací počet živých mes
def alive_mes_num(mes):
    c = 0
    for me in mes:
        if me.alive:
            c += 1
    return c


# vrací počet mes co vyhráli
def won_mes_num(mes):
    c = 0
    for me in mes: 
        if me.won:
            c += 1
    return c

          
# resi pohyb miny        
def handle_mine_movement(mine):
        
    if mine.dirx == -1 and mine.rect.x - mine.velocity < 0:
        mine.dirx = 1
       
    if mine.dirx == 1  and mine.rect.x + mine.rect.width + mine.velocity > WIDTH:
        mine.dirx = -1

    if mine.diry == -1 and mine.rect.y - mine.velocity < 0:
        mine.diry = 1
    
    if mine.diry == 1  and mine.rect.y + mine.rect.height + mine.velocity > HEIGHT:
        mine.diry = -1
         
    mine.rect.x += mine.dirx * mine.velocity
    mine.rect.y += mine.diry * mine.velocity


# resi pohyb min
def handle_mines_movement(mines):
    for mine in mines:
        handle_mine_movement(mine)


#----------------------------------------------------------------------------
# vykreslovací funkce 
#----------------------------------------------------------------------------


# vykresleni okna
def draw_window(mes, mines, flag, level, generation, timer):
    WIN.blit(SEA, (0, 0))   
    
    t = LEVEL_FONT.render("level: " + str(level), 1, WHITE)   
    WIN.blit(t, (10  , HEIGHT - 30))
    
    t = LEVEL_FONT.render("generation: " + str(generation), 1, WHITE)   
    WIN.blit(t, (150  , HEIGHT - 30))
    
    t = LEVEL_FONT.render("alive: " + str(alive_mes_num(mes)), 1, WHITE)   
    WIN.blit(t, (350  , HEIGHT - 30))
    
    t = LEVEL_FONT.render("won: " + str(won_mes_num(mes)), 1, WHITE)   
    WIN.blit(t, (500  , HEIGHT - 30))
    
    t = LEVEL_FONT.render("timer: " + str(timer), 1, WHITE)   
    WIN.blit(t, (650  , HEIGHT - 30))
    
    

    WIN.blit(FLAG, (flag.rect.x, flag.rect.y))    
         
    # vykresleni min
    for mine in mines:
        WIN.blit(ENEMY, (mine.rect.x, mine.rect.y))
        
    # vykresleni me
    for me in mes: 
        if me.alive:
            WIN.blit(ME, (me.rect.x, me.rect.y))
        
    pygame.display.update()



def draw_text(text):
    t = BOOM_FONT.render(text, 1, WHITE)   
    WIN.blit(t, (WIDTH // 2  , HEIGHT // 2))     
    
    pygame.display.update()
    pygame.time.delay(1000)





#-----------------------------------------------------------------------------
# funkce reprezentující neuronovou síť, pro inp vstup a zadané váhy wei, vydá
# čtveřici výstupů pro nahoru, dolu, doleva, doprava    
#----------------------------------------------------------------------------

# DOPLNĚNO
def nn_function(inp, wei):
    
    input_size = len(inp)
    hidden_size = 5
    output_size = 4  # nahoru, dolů, doleva, doprava
    
    # rozdělení vektoru vah
    weights_hidden_start = 0
    weights_hidden_end = (input_size + 1) * hidden_size
    weights_output_start = weights_hidden_end
    weights_output_end = weights_output_start + (hidden_size + 1) * output_size
    
    if len(wei) < weights_output_end:
        return [random.randint(0, 3)]  # Pokud nemáme dostatek vah, vrátíme náhodný směr
    
    # extrakce vah pro jednotlivé vrstvy
    weights_hidden = np.array(wei[weights_hidden_start:weights_hidden_end]).reshape(hidden_size, input_size + 1)
    weights_output = np.array(wei[weights_output_start:weights_output_end]).reshape(output_size, hidden_size + 1)
    
    inp_with_bias = np.append(inp, 1.0)
    
    hidden_layer = np.dot(weights_hidden, inp_with_bias)
    hidden_layer = np.maximum(0, hidden_layer)
    hidden_with_bias = np.append(hidden_layer, 1.0)

    output_layer = np.dot(weights_output, hidden_with_bias)
    
    # aktivační funkce softmax pro normalizaci výstupů
    exp_output = np.exp(output_layer - np.max(output_layer))  # odečtení maxima pro numerickou stabilitu
    softmax_output = exp_output / np.sum(exp_output)
    
    direction = np.argmax(softmax_output)
    
    return [direction]




# naviguje jedince pomocí neuronové sítě a jeho vlastní sekvence v něm schované
def nn_navigate_me(me, inp, mines, flag):
    
    # DOPLNĚNO
    # rozšíření vstupních senzorů
    extended_inp = inp.copy()
    
    extended_inp.append(position_x(me))
    extended_inp.append(position_y(me))
    extended_inp.append(flag_distance(me, flag))
    extended_inp.append(nearest_mine_distance(me, mines))
    extended_inp.append(danger_up(me, mines))
    extended_inp.append(danger_down(me, mines))
    extended_inp.append(danger_left(me, mines))
    extended_inp.append(danger_right(me, mines))
    
    # získání směru pohybu z NN
    out = np.array(nn_function(extended_inp, me.sequence))
    ind = out[0]
    
    # nahoru, pokud není zeď
    if ind == 0 and me.rect.y - ME_VELOCITY > 0:
        me.rect.y -= ME_VELOCITY
        me.dist += ME_VELOCITY
    
    # dolu, pokud není zeď
    if ind == 1 and me.rect.y + me.rect.height + ME_VELOCITY < HEIGHT:
        me.rect.y += ME_VELOCITY  
        me.dist += ME_VELOCITY
    
    # doleva, pokud není zeď
    if ind == 2 and me.rect.x - ME_VELOCITY > 0:
        me.rect.x -= ME_VELOCITY
        me.dist += ME_VELOCITY
        
    # doprava, pokud není zeď    
    if ind == 3 and me.rect.x + me.rect.width + ME_VELOCITY < WIDTH:
        me.rect.x += ME_VELOCITY
        me.dist += ME_VELOCITY
    
    

# updatuje, zda me vyhrali 
def check_mes_won(mes, flag):
    for me in mes: 
        if me.alive and not me.won:
            if me_won(me, flag):
                me.won = True
    


# resi pohyb mes
def handle_mes_movement(mes, mines, flag):
    
    for me in mes:

        if me.alive and not me.won:
            
            # Sbírání vstupů ze senzorů
            inp = []
            
            # Základní senzor
            inp.append(my_senzor(me))
            
            # Navigace agenta pomocí neuronové sítě s rozšířenými vstupy
            nn_navigate_me(me, inp, mines, flag)



# updatuje timery jedinců
def update_mes_timers(mes, timer):
    for me in mes:
        if me.alive and not me.won:
            me.timealive = timer



# ---------------------------------------------------------------------------
# fitness funkce výpočty jednotlivců
#----------------------------------------------------------------------------



# funkce pro výpočet fitness všech jedinců
def handle_mes_fitnesses(mes):    
    # Výpočet fitness pro každého jedince
    for me in mes:
        # Základní fitness je čas přežití
        base_fitness = me.timealive
        
        # Bonus za překonanou vzdálenost
        distance_bonus = me.dist * 0.1
        
        # Velký bonus za dosažení cíle
        win_bonus = 1000 if me.won else 0
        
        # Celková fitness
        me.fitness = base_fitness + distance_bonus + win_bonus
    
    

# uloží do hof jedince s nejlepší fitness
def update_hof(hof, mes):
    l = [me.fitness for me in mes]
    ind = np.argmax(l)
    hof.sequence = mes[ind].sequence.copy()
    

# ----------------------------------------------------------------------------
# main loop 
# ----------------------------------------------------------------------------

def main():
    
    
    # =====================================================================
    # Parametry nastavení evoluce (DOPLNĚNO)
    # =====================================================================
    
    VELIKOST_POPULACE = 10  # při pokusném navýšení bez změny dalších parametrů tendence uvíznout v levém dolním rohu
    EVO_STEPS = 5  # pocet kroku evoluce
    
    INPUT_SIZE = 9  # 1+2+1+1+4
    HIDDEN_SIZE = 5
    OUTPUT_SIZE = 4
    
    DELKA_JEDINCE = (INPUT_SIZE + 1) * HIDDEN_SIZE + (HIDDEN_SIZE + 1) * OUTPUT_SIZE
    
    NGEN = 30        # počet generací
    CXPB = 0.7       # pravděpodobnost crossoveru (lehce navýšeno)
    MUTPB = 0.3      # pravděpodobnost mutace (lehce navýšeno)
    
    SIMSTEPS = 1000  # počet kroků simulace
    
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    
    toolbox = base.Toolbox()

    toolbox.register("attr_rand", lambda: random.uniform(-1, 1))  # inicializace genů v rozsahu -1 až 1 pro lepší chování NN (DOPLNĚNO)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_rand, DELKA_JEDINCE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # DOPLNĚNO
    # vlastní mutace - gaussovská
    def mutGaussian(individual, mu, sigma, indpb):
        for i in range(len(individual)):
            if random.random() < indpb:
                individual[i] += random.gauss(mu, sigma)
                individual[i] = max(min(individual[i], 1), -1)  # omezení hodnot mezi -1 a 1
        return individual,

    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutGaussian, mu=0, sigma=0.2, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)  # turnajová selekce (DOPLNĚNO)
    toolbox.register("selectbest", tools.selBest)
    
    pop = toolbox.population(n=VELIKOST_POPULACE)
        
    # =====================================================================
    
    clock = pygame.time.Clock()

    
    
    # =====================================================================
    # testování hraním a z toho odvození fitness 
   
    
    mines = []
    mes = set_mes(VELIKOST_POPULACE)    
    flag = Flag()
    
    hof = Hof()
    
    
    run = True

    level = 3   # Nastavení obtížnosti počtu min
    generation = 0
    
    evolving = True
    timer = 0
    
    while run:  
        
        clock.tick(FPS)
        
               
        # pokud evolvujeme pripravime na dalsi sadu testovani - zrestartujeme scenu
        if evolving:           
            timer = 0
            generation += 1
            reset_mes(mes, pop) # přiřadí sekvence z populace jedincům a dá je na start
            mines = set_mines(level) 
            evolving = False
            
        timer += 1    
            
        check_mes_won(mes, flag)
        handle_mes_movement(mes, mines, flag)
        
        
        handle_mines_movement(mines)
        
        mes_collision(mes, mines)
        
        if all_dead(mes):
            evolving = True
            #draw_text("Boom !!!")"""

            
        update_mes_timers(mes, timer)        
        draw_window(mes, mines, flag, level, generation, timer)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    

        

        
        # ---------------------------------------------------------------------
        # Druhá část evoluce po simulaci
        # ---------------------------------------------------------------------
        
        if timer >= SIMSTEPS or nobodys_playing(mes): 
            
            # přepočítání fitness funkcí, dle dat uložených v jedinci
            handle_mes_fitnesses(mes)
            
            update_hof(hof, mes)
            
            # přiřazení fitnessů z jedinců do populace
            for i in range(len(pop)):
                ind = pop[i]
                me = mes[i]
                ind.fitness.values = (me.fitness, )
            
            
            # selekce a genetické operace
            offspring = toolbox.select(pop, len(pop))
            offspring = list(map(toolbox.clone, offspring))
            
            # DOPLNĚNO
            # zachování nejlepších jedinců
            best_individuals = toolbox.selectbest(pop, 2)
            offspring[0] = toolbox.clone(best_individuals[0])
            offspring[1] = toolbox.clone(best_individuals[1])
            
            
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < CXPB:
                    toolbox.mate(child1, child2)

            for mutant in offspring:
                if random.random() < MUTPB:
                    toolbox.mutate(mutant)  
            
            pop[:] = offspring
            
            
            evolving = True
                   
        
    # po vyskočení z cyklu aplikace vytiskne DNA sekvecni jedince s nejlepší fitness
    # a ukončí se
    
    pygame.quit()    


if __name__ == "__main__":
    main()