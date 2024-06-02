import pygame

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((width, 50), pygame.SRCALPHA)
        
        pygame.draw.rect(self.image, pygame.Color('green'), (0, 0, width, 50))
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