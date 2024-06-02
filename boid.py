import pygame 
from random import uniform
from shape import Shape
import random
from sound import SoundManager
from logger import CustomLogger
logger = CustomLogger()
sound_manager = SoundManager()
channel1 = pygame.mixer.Channel(1)
channel2 = pygame.mixer.Channel(2)
class Boid(Shape):
    ###############
    food_found_position = None
    debug = False
    min_speed = 0.001
    max_speed = 0.15
    max_force = 1
    max_turn = 5
    perception = 100
    crowding = 15
    edge_buffor = 5
    ###############

    #  BEHAVIOURS  #
    is_hungry = False
    is_attacked = False
    is_collided = False
    is_dead = False
    is_eating = False
    ################
    is_found_food = False
    is_finished_eating = False
    def __init__(self):
        Boid.set_boundary(Boid.edge_buffor)
        #sound management
        self.sound_flag = None
        self.last_sound_flag = None
        self.frame_counter = 0
        self.cohesion_multiplier = 1
        self.eating = False
        self.eating_timer = 0
        self.avoidance_timer = 0
        self.collision_timer = 0 
        self.scatter_timer = 0
        start_position = pygame.math.Vector2(
            uniform(0, Boid.max_x),
            uniform(0, Boid.max_y))
        start_velocity = pygame.math.Vector2(
            uniform(-1, 1) * Boid.max_speed,
            uniform(-1, 1) * Boid.max_speed)

        super().__init__(start_position, start_velocity,
                         Boid.min_speed, Boid.max_speed,
                         Boid.max_force, pygame.Color('blue'))

        self.rect = self.image.get_rect(center=self.position)

    def separation(self, boids):
        steering = pygame.Vector2()
        for boid in boids:
            dist = self.position.distance_to(boid.position)
            if dist < self.crowding:
                steering -= boid.position - self.position
        steering = self.clamp_force(steering)
        return steering

    def alignment(self, boids):
        steering = pygame.Vector2()
        for boid in boids:
            steering += boid.velocity
        steering /= len(boids)
        steering -= self.velocity
        steering = self.clamp_force(steering)
        return steering / 8

    def cohesion(self, boids):
        steering = pygame.Vector2()
        for boid in boids:
            steering += boid.position
        steering /= len(boids)
        steering -= self.position
        steering = self.clamp_force(steering)
        return steering / 100
    


    def obstacle_avoidance(self, obstacles):
        steering = pygame.Vector2()

        for obstacle in obstacles:
            closest_point = self.find_closest_point(obstacle.points)
            dist = self.position.distance_to(closest_point)

            if dist < self.perception :
                repulsion_force = (self.position - closest_point)
                if dist > 0 and dist < 10:
                    repulsion_force /= dist
                steering += repulsion_force
                steering = self.clamp_force(steering)

                if dist < 10 and not self.is_collided:
                    self.is_collided = True
                    self.collision_timer = 1000.0 

        return steering

    def find_closest_point(self, points):
        closest_point = min(points, key=lambda p: self.position.distance_to(p))
        return closest_point

    def group(self):
        self.cohesion_multiplier = -1

    def ungroup(self):
        self.cohesion_multiplier = -1


    def find_food(self, dt, boids, FoodLevel=50):
        if self.is_hungry:

            level = random.randint(5, 50)
            if self.position.y <= level and not self.eating:
                self.eating = True
                self.eating_timer = random.randint(5000, 7000)
                self.is_hungry = False
                Boid.food_found_position = 50 
                self.is_found_food = True

    def eating_food(self, dt, boids, FoodLevel = 50):
        all_done_eating = all(not b.is_hungry for b in boids)
        if self.eating and all_done_eating:
            self.is_found_food = False
            Boid.food_found_position = None
            if self.eating_timer > 0:
                self.eating_timer -= dt
                if self.eating_timer <= 0:
                    self.eating = False
                    self.is_finished_eating = True
                    self.cohesion_multiplier = 1
                else:
                    return True  
                
    def move_towards_food(self):
        if Boid.food_found_position is not None:
            target_y = Boid.food_found_position
            direction = pygame.math.Vector2(0, target_y - self.position.y).normalize()
            desired_velocity = direction * self.max_speed
            steering = desired_velocity - self.velocity
            steering *= 0.1
            if steering.length() > self.max_force:
                steering.scale_to_length(self.max_force)
            self.velocity += steering
            self.position += self.velocity
                
    def update(self, dt, boids, obstacles, predator):
        if self.scatter_timer > 0:
            self.scatter_timer -= dt
            if self.scatter_timer <= 0:
                self.is_attacked = False

        if Boid.food_found_position is not None:
            self.move_towards_food()
                
        if self.collision_timer > 0:
            self.stop()
            self.is_collided = False
            self.collision_timer -= dt
            if self.collision_timer <= 0:
                self.start(0.15)
                self.avoidance_timer = 1000.0  
            else:
                return  
        steering = pygame.Vector2()

        escape_force = self.escape_predator(predator, boids)
        if escape_force.length() > 0:
            steering += escape_force

        # Logika szukania jedzenia
        if self.is_hungry:
            self.find_food(dt, boids)
            self.cohesion_multiplier = -1


        if self.eating and self.is_attacked is False:
            self.eating_food(dt, boids)
            return
        elif self.eating and self.is_attacked:
            self.eating = False
            self.is_hungry = False
            self.eating_timer = 0
            Boid.food_found_position = None
            self.start(0.15)
            return
        
        if self.is_attacked:
            self.crowding = 10
        else:
            self.crowding = 15
        steering += self.avoid_edge()

        if self.avoidance_timer <= 0:
            obstacles_avoidance = self.obstacle_avoidance(obstacles)
            steering += obstacles_avoidance
        else:
            self.avoidance_timer -= dt

        neighbors = self.get_neighbors(boids)
        if neighbors:
            separation = self.separation(neighbors)
            alignment = self.alignment(neighbors)
            cohesion = self.cohesion(neighbors) * self.cohesion_multiplier
            steering += separation + alignment + cohesion

        super().update(dt, steering)

    def handle_sound(self, sound_manager, boids):
        sound_played = False
        if self.is_collided and self.last_sound_flag != 'collision':
            sound_manager.play_sound('collision')
            self.last_sound_flag = 'collision'
            #logger.log_message("Collision")
            #logger.log_sound(sound_manager.get_last_sound_played()) 
            sound_played = True
        elif self.is_dead and self.last_sound_flag != 'death':
            sound_manager.play_death_on_channel2()
            self.last_sound_flag = 'death'
            sound_played = True
        elif (self.is_found_food and 
              self.last_sound_flag != 'found_food'):
            sound_manager.play_sound('found_food')
            self.last_sound_flag = 'found_food'
            #logger.log_message("Food found. Eating.")
            #logger.log_sound(sound_manager.get_last_sound_played())
            self.is_found_food = False 
            sound_played = True
        elif self.is_finished_eating and all(not b.is_hungry for b in boids) and self.last_sound_flag != "finished_eating":
            sound_manager.play_sound('finished_eating')
            self.last_sound_flag = 'finished_eating'  
            #logger.log_message("Finished eating. Going.")
            #logger.log_sound(sound_manager.get_last_sound_played())       
            self.is_finished_eating = False   
        elif self.is_attacked and self.last_sound_flag != 'danger':
            sound_manager.play_sound('danger')
            self.last_sound_flag = 'danger'
            #logger.log_message("Danger!")
            #logger.log_sound(sound_manager.get_last_sound_played())
            sound_played = False
        elif self.is_hungry and self.last_sound_flag != 'hungry':
            sound_manager.play_sound('hungry')
            self.last_sound_flag = 'hungry'
            #logger.log_sound(sound_manager.get_last_sound_played())
            sound_played = True
        self.frame_counter += 1

        if self.last_sound_flag in ['collision', 'danger', 'finished_eating']:
            self.last_sound_flag = None
        return sound_played
        

    def get_neighbors(self, boids):
        neighbors = []
        for boid in boids:
            if boid != self:
                dist = self.position.distance_to(boid.position)
                if dist < self.perception:
                    neighbors.append(boid)
        return neighbors
    
    def get_neighbor_predator(self, predator):
        dist = self.position.distance_to(predator.position)
        if dist < self.perception:
            return predator
        return None

    
    def escape_predator(self, predator, boids):
        nearby_predator = self.get_neighbor_predator(predator)
        if (nearby_predator is not None and 
            nearby_predator.attack_mode) == True:
            distance = self.position.distance_to(nearby_predator.position)
            if distance <= nearby_predator.radius and predator.attacking:
                self.is_dead = True
                return pygame.Vector2(0, 0)
            if distance < self.perception and predator.attacking:
                self.crowding = 30
                # Informuje sąsiednie boidy o zagrożeniu
                self.inform_about_danger(boids)
                direction = self.position - nearby_predator.position
                escape_force = direction.normalize() * self.max_speed
                # Dodatkowa siła odpychania od drapieżnika
                repulsion_force = direction.normalize() * (self.perception - distance) * 0.1
                total_force = escape_force + repulsion_force
                if total_force.length() > self.max_force:
                    total_force.scale_to_length(self.max_force)
                return total_force
        if (nearby_predator is None and 
            predator.attacking == True):
            distance = self.position.distance_to(predator.position)
            direction = self.position - predator.target_position
            escape_force = direction.normalize() * self.max_speed
            # Dodatkowa siła odpychania od źródła dźwięku
            repulsion_force = direction.normalize() * (self.perception - distance) * 0.1
            total_force = escape_force + repulsion_force
            if total_force.length() > self.max_force:
                total_force.scale_to_length(self.max_force)
            return escape_force
        return pygame.Vector2(0, 0)
        
    def inform_about_danger(self, boids):
        if self.get_neighbors(boids) is not None:
            for b in boids:
                b.is_attacked = True
                b.scatter_timer = 1000  # 5 sekund w milisekundach