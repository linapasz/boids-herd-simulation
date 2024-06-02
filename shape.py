import pygame as pg


class Shape(pg.sprite.Sprite):
    image = pg.Surface((10, 10), pg.SRCALPHA)
    def __init__(self, position, velocity, min_speed, max_speed,max_force, color):

        super().__init__()
        pg.draw.polygon(self.image, color,[(15, 5), (0, 2), (0, 8)])
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.max_force = max_force

        self.position = pg.Vector2(position)
        self.acceleration = pg.Vector2(0, 0)
        self.velocity = pg.Vector2(velocity)
        self.heading = 0.0

        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt, steering):
        self.acceleration = steering * dt

        # enforce turn limit
        _, old_heading = self.velocity.as_polar()
        new_velocity = self.velocity + self.acceleration * dt
        speed, new_heading = new_velocity.as_polar()

        heading_diff = 180 - (180 - new_heading + old_heading) % 360
        if abs(heading_diff) > self.max_turn:
            if heading_diff > self.max_turn:
                new_heading = old_heading + self.max_turn
            else:
                new_heading = old_heading - self.max_turn

        self.velocity.from_polar((speed, new_heading))

        # enforce speed limit
        speed, self.heading = self.velocity.as_polar()
        if speed < self.min_speed:
            self.velocity.scale_to_length(self.min_speed)

        if speed > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        # move
        self.position += self.velocity * dt

        # draw
        self.image = pg.transform.rotate(Shape.image, -self.heading)

        if self.debug:
            center = pg.Vector2((50, 50))

            velocity = pg.Vector2(self.velocity)
            speed = velocity.length()
            velocity += center

            acceleration = pg.Vector2(self.acceleration)
            acceleration += center

            steering = pg.Vector2(steering)
            steering += center

            overlay = pg.Surface((100, 100), pg.SRCALPHA)
            overlay.blit(self.image, center - (10, 10))

            pg.draw.line(overlay, pg.Color('green'), center, velocity, 3)
            pg.draw.line(overlay, pg.Color('red'), center + (5, 0),
                         acceleration + (5, 0), 3)
            pg.draw.line(overlay, pg.Color('blue'), center - (5, 0),
                         steering - (5, 0), 3)

            self.image = overlay
            self.rect = overlay.get_rect(center=self.position)
        else:
            self.rect = self.image.get_rect(center=self.position)

    def start(self, max_speed):
        self.max_speed = max_speed
        self.velocity += pg.Vector2(0.01, 0.01)
        if self.velocity.length() < self.max_speed:
            self.velocity += self.velocity.normalize() * 0.01 
    

    def stop(self):
        self.max_speed = 0.001
        self.velocity *= 0.01
        self.acceleration *= 0.01

    def avoid_edge(self):
        left = self.edges[0] - self.position.x
        up = self.edges[1] - self.position.y
        right = self.position.x - self.edges[2]
        down = self.position.y - self.edges[3]

        scale = max(left, up, right, down)

        if scale > 0:
            center = (Shape.max_x / 2, Shape.max_y / 2)
            steering = pg.Vector2(center)
            steering -= self.position
        else:
            steering = pg.Vector2()

        return steering
    
    @staticmethod
    def set_boundary(edge_distance_pct):
        info = pg.display.Info()
        Shape.max_x = info.current_w
        Shape.max_y = info.current_h
        margin_w = Shape.max_x * edge_distance_pct / 100
        margin_h = Shape.max_y * edge_distance_pct / 100
        Shape.edges = [margin_w, margin_h, Shape.max_x - margin_w,
                         Shape.max_y - margin_h]

    def clamp_force(self, force):
        if 0 < force.magnitude() > self.max_force:
            force.scale_to_length(self.max_force)

        return force
