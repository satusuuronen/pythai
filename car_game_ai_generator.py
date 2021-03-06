import gp
import math
import car
import getopt
import sys
import time
import curses
import game
import pygame
from pygame.locals import *
from os import path, access, R_OK  # W_OK for write permission.

#Enable for profiling...
#import cProfile

# Number of generations
number_of_generations = 10
# How many "codes" is generated during each generation
number_of_codes = 50
# How many game loops each generated code is executed
number_of_rounds = 500
# Show best code with graphics
show_best_graphics = True
# Loop best run over and over
loop_best_graphics = True
# Save and load the best code so far
save_load_best_code = True
# Show all generated codes
show_all_generated_code = False
# Set true/false whether to draw graphics or not
use_graphics = False
# Set true/false whether to simulate real time or not
use_realtime = False
# Should the code generation process stopped after current generation
stop_after_next_generation = False

print "Initializing game"
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Pythai!')
pygame.key.set_repeat(1, 50)
white = 255, 255, 255
clock = pygame.time.Clock()
FPS = 30
thegame = game.Game()


def intialize_code_generator():
    #setup GP process
    gp.settings.maximumCommandsPerBlock = 10
    gp.settings.maximumEquationsPerCondition = 3
    gp.settings.maximumCodeDepth = 3
    gp.settings.maximumBlocks = 5
    gp.settings.crossover_percentage = 85

    #game global variables
    gp.global_variable.register("thegame", game.Game, [None], False)
    gp.global_variable.register("thegame.get_car()", car.Car, [None], False)

    #equations for if clauses
    gp.equation.register("<", int)
    gp.equation.register(">", int)
    gp.equation.register("==", int)
    gp.equation.register("!=", int)

    #gp.literal. that code can use
    gp.literal.register(0)        
    gp.literal.register(-1)        
    gp.literal.register(1)        
    gp.literal.register(-10)        
    gp.literal.register(10)        
    gp.literal.register(-50)        
    gp.literal.register(50)        
    gp.literal.register(-90)        
    gp.literal.register(90)        

    gp.literal.register(0.0)
    gp.literal.register(-0.5)
    gp.literal.register(0.5)
    gp.literal.register(-1.0)
    gp.literal.register(1.0)
    gp.literal.register(-1.5)
    gp.literal.register(1.5)

    #game controls
    gp.command.register("accelerate", None, car.Car, [], False)
    gp.command.register("brake", None, car.Car, [], False)
    gp.command.register("steer_left", None, car.Car, [], False)
    gp.command.register("steer_right", None, car.Car, [], False)
    #game state
    gp.command.register("get_track_side", int, game.Game, [], True)
    gp.command.register("speed_kmh", int, car.Car, [], True)
    gp.command.register("get_steer", float, car.Car, [], True)
    
    gp.if_statement.register(int);
    

def generate_code():
    #print "Generating Controlling Code:"
    generator = gp.code()
    generator.generate()
    code = generator.to_s()
    if (show_all_generated_code):
        print "-" * 40
        print code 
        print "-" * 40
    return code


def main(): 
    intialize_code_generator() 


    generation = gp.generation()
    generation.clear_logs()
    
    """
    TODO: Loading of old best code should be made with serialize/unserialize methods
    
    if (save_load_best_code):
        old_best_file = "best_code.txt"
        if path.exists(old_best_file) and path.isfile(old_best_file) and access(old_best_file, R_OK):
            fileHandle = open (old_best_file, 'r' )
            old_best_code = fileHandle.read()
            fileHandle.close()
            #print "Loaded and executing previous King!"
            #best_score = do_simulation(old_best_code)
            #best_code = old_best_code
        else:
            print "Previous best code file could not be opened"
    """ 
    global stop_after_next_generation

    for i in range(number_of_generations):
        best_score = None
        best_code = None
        
        if (i == 0):      
            #create the first generation
            for h in range(number_of_codes): 
                generation.add_code(gp.code.generate())
        else:
            generation = generation.get_next_generation()
            """
            next_generation = list()
            next_generation.append(best_code)
            #create 50% new codes and rest of the codes with the king :)
            for h in range(number_of_codes / 2):
                next_generation.append(code_generator.generate())
            for h in range(number_of_codes / 2):
                next_generation.append(code_merger.merge(generation[i], best_code))
            generation = next_generation
            """


        #execute generation
        for code in generation.get_codes(): 
            #The game is always the same. Do not execute codes that were moved directly from the
            #previous generation
            if (code.get_moved_unchanged()):
                score = code.get_result()
                print "Directly moved code not executed, score: " + str(score)
            else:
                score = do_simulation(code.to_s())
                code.set_result(score)

            if (best_score == None or score > best_score):
                best_score = score
                best_code = code
        print "=" * 40
        print "Best score in generation " + str(i) + " was: " + str(best_score)
        #print "Best code was"
        print "=" * 40
        #print code.to_s()
        if (stop_after_next_generation):
            break

    
    """
    if (save_load_best_code):
        try:
            fileHandle = open ( 'best_code.txt', 'w' )
            fileHandle.write(best_code)
            fileHandle.close()
        except IOError as e:
            print 'Could not open previous best code file'
    """      
    print "=" * 40
    print "=" * 40
    print best_code.to_s()
    print "=" * 40

    if (show_best_graphics):
        print "showing best code graphically!"
        global use_graphics
        use_graphics = True
        do_simulation(best_code.to_s())
        while loop_best_graphics:
            do_simulation(best_code.to_s())

    
def draw_screen():
    screen.fill(white)
    thegame.draw(screen)
    pygame.display.flip()
    
def do_simulation(code):
    print "Starting simulation"
    global thegame
    thegame = game.Game()
    
    simulation_on = True
    thegame.set_car_throttle(10)
    simulation_rounds = 0

    while simulation_on and simulation_rounds < number_of_rounds:
        simulation_rounds += 1

        if use_realtime:
            clock.tick(FPS)

        thegame.advance()
         
        if use_graphics:
            draw_screen()

        exec code

        if (thegame.get_is_game_over()):
            simulation_on = False

        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            down = event.type == KEYDOWN     # key down or up?
            if (down):
                if event.key == K_SPACE:
                    global stop_after_next_generation
                    stop_after_next_generation = True
                    print "== Requested stop after next generation end"
                if event.key == K_ESCAPE:
                    sys.exit(0)
                    
        
    total_score = thegame.get_total_score()
    print "Resulting score: " + str(total_score)
    return total_score
            

if __name__ == "__main__":
    main()

    #enable for profiling
    #cProfile.run('main()', 'prof')

