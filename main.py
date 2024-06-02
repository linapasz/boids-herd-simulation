import sys
import pygame
from pygame.locals import *
from boid import Boid
from obstacle import Obstacle
import random
from food import Food
from predator import Predator
from sound import SoundManager
from logger import CustomLogger
import datetime
logger = CustomLogger()
sound_manager = SoundManager()
default_boids = 30
window_width, window_height = 800, 500
predator_created = False
frame_counter = 0
##boids
hunger_enabled = False
scattering_enabled = False
food_sound_played = False
mouse_activated = False
last_sound = None
def update(dt, boids, obstacles,food, predator, screen):
    global hunger_enabled
    global scattering_enabled
    global predator_created
    global frame_counter
    global food_sound_played
    global mouse_activated
    global last_sound
    sound_played_this_frame = False
    for event in pygame.event.get():
        if event.type == QUIT:
            logger.log_message("Simulation ended")
            pygame.quit()
            sys.exit(0)
        elif event.type == KEYDOWN:
            mods = pygame.key.get_mods()
            if event.key == pygame.K_q:
                # quits
                pygame.quit()
                sys.exit(0)
            elif event.key == pygame.K_UP:
                # add boids
                if mods & pygame.KMOD_SHIFT:
                    add_boids(boids, 100)
                else:
                    add_boids(boids, 10)
            elif event.key == pygame.K_DOWN:
                # remove boids
                if mods & pygame.KMOD_SHIFT:
                    boids.remove(boids.sprites()[:100])
                else:
                    boids.remove(boids.sprites()[:10])
            elif event.key == pygame.K_1:
                for boid in boids:
                    boid.max_force /= 2
                print("max force increasing")
            elif event.key == pygame.K_2:
                for boid in boids:
                    boid.max_force *= 2
                print("max force decreasing")
            elif event.key == pygame.K_3:
                for boid in boids:
                    boid.perception *= .5
                print("perception decreasing")
            elif event.key == pygame.K_4:
                for boid in boids:
                    boid.perception *= 1.2
                print("perception increasing")
            elif event.key == pygame.K_5:
                for boid in boids:
                    boid.crowding *= 0.5
                print("crowding {}".format(boids.sprites()[0].crowding))
            elif event.key == pygame.K_6:
                for boid in boids:
                    boid.crowding *= 2
                print("crowding {}".format(boids.sprites()[0].crowding))
            # BOID RESET
            elif event.key == pygame.K_r:
                num_boids = len(boids)
                boids.empty()
                add_boids(boids, num_boids)
            # HUNGER ENABLING
            elif event.key == pygame.K_f:
                hunger_enabled = True
                print("Hungry: ", hunger_enabled)
                for boid in boids:
                    boid.is_hungry = hunger_enabled
                logger.log_message("Hunger activated.")
                hunger_enabled = False
            # STARTING BOIDS
            elif event.key == pygame.K_x:
                for boid in boids:
                    boid.start(0.15)
                predator.start(0.05)
            elif event.key == pygame.K_z:
                for boid in boids:
                    boid.stop()
                predator.stop()
            elif event.key == pygame.K_a:
                predator.attack_mode = not predator.attack_mode
                logger.log_message("Attack mode:" + str(predator.attack_mode)) 
                sound_manager.play_sound('attack')
                logger.log_message("Attack!")
                logger.log_sound(sound_manager.get_last_sound_played())
                sound_played_this_frame = True
            elif event.key == pygame.K_p and not predator_created:
                predator = Predator()  # Tworzy drapieżnika
                predator.set_boundary(Predator.edge_buffor)
                predator_created = True
                logger.log_message("Predator created")
            elif event.key == pygame.K_m:
                mouse_activated = not mouse_activated
            elif event.key == pygame.K_i:
                print("max_force: {}".format(boids.sprites()[0].max_force))
                print("crowding: {}".format(boids.sprites()[0].crowding))
                print("perception: {}".format(boids.sprites()[0].perception))
                print("perception predator: {}".format(predator.perception))
            elif event.key == pygame.K_s:
                save_screen_to_file(screen, "snapshot.jpg")
    
    if predator_created:
        predator.update(dt, boids, obstacles, mouse_activated)

    for b in boids:
        b.update(dt, boids, obstacles, predator)
        if b.handle_sound(sound_manager, boids):
            sound_played_this_frame = True

    if not sound_played_this_frame and not predator.attacking and frame_counter >= 30:
        sound_manager.play_random_piano_sound()
        frame_counter = 0
        logger.log_sound(sound_manager.get_last_sound_played()) 
    frame_counter += 1

def draw(screen, boids, obstacles, food, background, predator, sound_manager, font):
    screen.blit(background, (0, 0)) 
    boids.clear(screen, background)
    draw_food(screen, food)
    draw_boids(screen, boids)
    draw_obstacles(screen, obstacles)
    predator.draw(screen)  

    last_sound = sound_manager.get_last_sound_played()
    if last_sound is not None:
        text = font.render(last_sound, True, (0, 0, 0))
        screen.blit(text, (10, window_height - 30))

    pygame.display.flip()


def main(window_width, window_height, default_boids):
    global predator_created
    pygame.init()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
    logger.log_message("##############################################")
    logger.log_message("################NEW SIMULATION################")
    logger.log_message("##############################################")
    # Set up the clock to maintain a relatively constant framerate.
    fps = 30.0
    fpsClock = pygame.time.Clock()

    pygame.display.set_caption("Boids Simulation")
    flags = DOUBLEBUF

    screen = pygame.display.set_mode((window_width, window_height), flags)
    screen.set_alpha(None)
    background = pygame.Surface(screen.get_size()).convert()
    background.fill(pygame.Color(250, 250, 250))

    font = pygame.font.SysFont(None, 24)

    boids = pygame.sprite.RenderUpdates()
    obstacles = pygame.sprite.Group()
    food = pygame.sprite.Group()
    predator = None
    add_boids(boids, default_boids)
    add_obstacles(obstacles, 0)
    add_food(food, 0, window_width, window_height)
    predator = Predator()
    dt = 1/fps

    predator = Predator()
    predator.set_boundary(Predator.edge_buffor)
    
    while True:
        update(dt, boids, obstacles, food, predator, screen)
        draw(screen, boids, obstacles, food, background, predator, sound_manager, font)
        dt = fpsClock.tick(fps)
    
def save_screen_to_file(screen, filename):
    """
    Zapisuje aktualny stan ekranu do pliku graficznego.

    :param screen: Obiekt ekranu Pygame.
    :param filename: Nazwa pliku do zapisu.
    """
    # Pobierz zawartość ekranu
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.jpg"
    screen_surface = pygame.display.get_surface()
    pygame.image.save(screen_surface, filename)
 

def add_obstacles(obstacles, num_obstacles):
    for _ in range(num_obstacles):
        x = random.randint(100, window_width-100)
        y = random.randint(100, window_height-100)
        obstacle = Obstacle(x, y)
        obstacles.add(obstacle)
        print(f"Added obstacle at ({x}, {y})")

def draw_obstacles(screen, obstacles):
    obstacles.draw(screen)

def add_food(food, num_food, window_width, window_height):
    for _ in range(num_food):
        x = 0
        y = 0
        food.add(Food(x, y, window_width, window_height))
        print(f"Added food at ({x}, {y})")

def draw_food(screen, food):
    food.draw(screen)

def add_boids(boids, num_boids):
    for _ in range(num_boids):
        boids.add(Boid())

def draw_boids(screen, boids):
    boids.draw(screen)

if __name__ == "__main__":
    main(window_width, window_height, default_boids)