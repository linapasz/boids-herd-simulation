import pygame
from random import uniform
from shape import Shape 
from boid import Boid
from sound import SoundManager
sound_manager = SoundManager()
from logger import CustomLogger
logger = CustomLogger()

class Predator(Shape):
    ###############
    debug = False
    min_speed = 0.001
    max_speed = 0.05
    attack_speed = 0.12
    max_force = 1
    max_turn = 10
    perception = 100 # bigger than in Boid
    edge_buffor = 5
    radius = 7
    attack_mode = False
    ###############

    def __init__(self):
        Predator.set_boundary(Predator.edge_buffor)
        self.chase_timer = 0 
        self.chase_limit = 1000 
        self.attacking = False
        self.target_position = None
        self.sound_played_this_frame = False
        start_position = pygame.math.Vector2(400,600)
        start_velocity = pygame.math.Vector2(
            uniform(-1, 1) * Predator.max_speed,
            uniform(-1, 1) * Predator.max_speed)

        super().__init__(start_position, start_velocity,
                         Predator.min_speed, Predator.max_speed,
                         Predator.max_force, pygame.Color('blue'))

        self.rect = self.image.get_rect(center=self.position)

    def find_closest_point(self, points):
        closest_point = min(points, key=lambda p: self.position.distance_to(p))
        return closest_point
    
    def get_neighbors(self, boids):
        neighbors = []
        for boid in boids:
            if boid != self:
                dist = self.position.distance_to(boid.position)
                if dist < self.perception:
                    neighbors.append(boid)
        return neighbors
    
    def obstacle_avoidance(self, obstacles):
        steering = pygame.Vector2()

        for obstacle in obstacles:
            if isinstance(obstacle, Boid): 
                continue

            closest_point = self.find_closest_point(obstacle.points)
            dist = self.position.distance_to(closest_point) - self.radius

            if dist < self.perception:
                # closer is stronger
                repulsion_force = (self.position - closest_point).normalize()
                if dist > 0: 
                    repulsion_force /= dist
                steering += repulsion_force

        steering = self.clamp_force(steering)
        return steering
            
    def avoid_boids(self, boids):
        steering = pygame.Vector2()
        for boid in boids:
            dist = self.position.distance_to(boid.position)
            if dist < self.perception:
                repulsion_force = (self.position - boid.position).normalize()
                if dist > 0:
                    repulsion_force /= dist
                steering += repulsion_force
        return self.clamp_force(steering)
    
    def select_target(self, boids):
        min_speed = float('inf')
        min_distance = float('inf')
        target = None
        boids_distances = {}

        for boid in boids:
            distance = self.position.distance_to(boid.position)
            #is in the view range
            if distance <= self.perception:
                speed = boid.velocity.length()
                boids_distances[boid] = distance

                if speed < min_speed:
                    min_speed = speed
                if distance < min_distance:
                    min_distance = distance
        #is vulnerable? means is isolated
        for boid, distance in boids_distances.items():
            if self.is_boid_isolated(boid, boids, boid.crowding + 50):
                target = boid
                break
            if boid.velocity.length() <= min_speed and distance <= min_distance:
                target = boid
                break
        return target

    def is_boid_isolated(self, boid, boids, isolation_range):
        neighbors_count = 0  

        for other_boid in boids:
            if boid != other_boid and boid.position.distance_to(other_boid.position) < isolation_range:
                neighbors_count += 1
        return neighbors_count == 1 

    def chase_target(self, target, dt):
        if target is None:
            return
        self.chase_timer += dt
        if self.chase_timer > self.chase_limit:
            self.chase_timer = 0
            #self.attack_mode = False
            self.attacking = False
            self.attack_mode = False
            logger.log_message("Target lost!") 
            self.sound_played_this_frame = False
            return
        self.target_position = target.position
        direction = target.position - self.position
        direction.normalize_ip()
        self.velocity = direction * self.attack_speed

    def attack(self, dt, boids):
        target = self.select_target(boids)
        if target is not None:
            self.attacking = True
            self.chase_target(target, dt)
            #sound_manager.play_sound('attack')
            #logger.log_sound(sound_manager.get_last_sound_played())
            #logger.log_message("Attack!")
            self.sound_played_this_frame = True
            if self.position.distance_to(target.position) < self.radius:
                #logger.log_message("Catched and killed!")  
                boids.remove(target)
                sound_manager.play_sound('death')
                #logger.log_sound(sound_manager.get_last_sound_played())
                self.attacking = False
                self.attack_mode = False
                #logger.log_message("Attack mode:" + str(self.attack_mode))  

    def update(self, dt, boids, obstacles, mouse_activated):
        if mouse_activated:
            mouse_pos = pygame.mouse.get_pos()
            target = pygame.Vector2(mouse_pos)

            # Oblicz wektor kierunkowy do myszki
            direction = target - self.position
            distance = direction.length()
            if distance > 0:  # Aby uniknąć dzielenia przez zero
                direction.normalize_ip()

            # Ogranicz prędkość
            self.velocity = direction * self.max_speed

            # Aktualizuj pozycję
            self.position += self.velocity * dt
          
        steering = pygame.Vector2()
        steering += self.avoid_edge()
        obstacles_avoidance = self.obstacle_avoidance(obstacles)
        steering += obstacles_avoidance

        if self.attack_mode:
            self.attack(dt, boids)
        else:
            steering += self.avoid_boids(boids)

        self.position += self.velocity * dt
        super().update(dt, steering)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), self.position, self.radius)
        pygame.draw.circle(screen, (220, 220, 220), self.position, self.perception, 1)