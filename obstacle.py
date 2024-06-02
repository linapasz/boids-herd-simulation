import pygame

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color('black'), (0, 0, 20, 20))

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.position = pygame.math.Vector2(self.rect.x, self.rect.y)

        self.points = [
            pygame.math.Vector2(self.rect.topleft),
            pygame.math.Vector2(self.rect.topright),
            pygame.math.Vector2(self.rect.bottomleft),
            pygame.math.Vector2(self.rect.bottomright)
        ]
