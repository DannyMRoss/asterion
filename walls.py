import pygame

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color, screen):

        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.color = color
        self.screen = screen
        self.image = pygame.Surface([w, h])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)