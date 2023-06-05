# asterion.rect.centerx <= platform.rect.left or asterion.rect.centerx >= platform.rect.right

# # # walls.add(Wall(206, 0, 10, SCREEN_HEIGHT, BLACK, screen, False))
# # walls.add(Wall(0, 319, SCREEN_WIDTH, 10, BLACK, screen, True))

# pygame.sprite.spritecollideany(asterion, walls) == None
# collided = pygame.sprite.spritecollide(asterion, walls, False)
# platform = Asterion.get_platform(collided)

# def get_platform(collidelist):
#         for wall in collidelist:
#             if wall.platform:
#                 return wall
            

# c = pygame.sprite.spritecollide(asterion, walls, False)
# c
# print(c)

# for x in range(0,1440,360):
#     walls.add(Wall(x, 500, 100, 10, BLACK, screen))

# for x in range(180,1440,360):
#     walls.add(Wall(x, 600, 100, 10, BLACK, screen))

# walls.add(Wall(1000, 0, 10, SCREEN_HEIGHT, BLACK, screen))
# #walls.add(Wall(0, 0, SCREEN_WIDTH, 20, BLACK, screen))
# walls.add(Wall(0, 0, 20, SCREEN_HEIGHT, BLACK, screen))
# walls.add(Wall(0, 800, SCREEN_WIDTH, 20, BLACK, screen))