import pygame
from pygame.math import Vector2
import numpy as np
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
MAROON = (128, 0, 0)
BRIGHT_YELLOW = (255, 255, 0)
BRIGHT_ORANGE = (255, 165, 0)
ORANGE_RED = (255, 69, 0)
GOLD = (255, 215, 0)

ASSETS_DIR = "../assets/"
BACKGROUND_IMG_PATH = ASSETS_DIR + "background.png"
SPACESHIP_IMG_PATH = ASSETS_DIR + "spaceship.png"
ASTEROID_IMG_PATH = ASSETS_DIR + "asteroid.png"
BULLET_IMG_PATH = ASSETS_DIR + "bullet.png"
EXPLOSION_IMG_PATHS = [ASSETS_DIR+"explosions/regularExplosion0%d.png" % i for i in range(9)]


pygame.init()
# infoObject = pygame.display.Info()
# screen_width = infoObject.current_w
# screen_height = infoObject.current_h
screen_width = 500
screen_height = 300
screen = pygame.display.set_mode([screen_width, screen_height], pygame.RESIZABLE)
pygame.display.set_caption("Spaceship Game")
background = pygame.image.load(BACKGROUND_IMG_PATH)
interval = 3000


def text_objects(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def draw_button(message, x, y, width, height, inactive_color, active_color):

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height))

        if click[0] == 1:
            return True

    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    small_text = pygame.font.SysFont("serif", height//3 * 2)
    text_surf, text_rect = text_objects(message, small_text, WHITE)
    text_rect.center = ((x + (width / 2)), (y + (height / 2)))
    screen.blit(text_surf, text_rect)

    return False


def quit_game():
    pygame.quit()
    quit()


def menu():
        while True:
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            large_text = pygame.font.SysFont("serif", screen_width // 10)
            text_surf, text_rect = text_objects("Spaceship Shooter", large_text, BLACK)
            text_rect.center = ((screen_width / 2), (screen_height / 2))
            screen.blit(text_surf, text_rect)

            button_play = draw_button("Go!", screen_width / 7 * 2, screen_height / 3 * 2, screen_width // 7,
                                      screen_height // 20, GREEN, BRIGHT_GREEN)
            button_quit = draw_button("Quit :(", screen_width / 7 * 4, screen_height / 3 * 2, screen_width // 7,
                                      screen_height // 20, MAROON, BRIGHT_RED)

            pygame.display.update()

            if button_play or button_quit:
                if button_play:
                    return True
                else:
                    return False


class Player(pygame.sprite.Sprite):

    def __init__(self, position):
        super().__init__()

        self.image = pygame.image.load(SPACESHIP_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (screen_width // 20, screen_width // 20 * 7 // 4))
        self.rect = self.image.get_rect()

        self.rect.center = position
        self.original_image = self.image
        self.angle = 90
        self.angle_speed = 0

    def update(self):

        if self.angle_speed:

            self.angle += self.angle_speed
            self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
            self.rect = self.image.get_rect(center=self.rect.center)


asteroid_image = pygame.image.load(ASTEROID_IMG_PATH).convert_alpha()
asteroid_image = pygame.transform.scale(asteroid_image, (screen_width // 25, screen_width // 25))


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, x, y, angle):
        super().__init__()

        self.image = asteroid_image.copy()
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.vel = Vector2(0, -max(np.random.normal(size=1, loc=3, scale=1), 1))
        self.rect.x = x
        self.rect.y = y
        self.vel.rotate_ip(-angle + 270)

    def update(self):
        self.rect = self.rect.move(self.vel)

        if self.rect.x > screen_width or self.rect.x < 0 \
           or self.rect.y > screen_height or self.rect.y < 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):

    def __init__(self, player):
        super().__init__()

        self.image = pygame.image.load(BULLET_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (screen_width // 120, screen_width // 120 * 18 // 10))
        self.rect = self.image.get_rect()

        self.vel = Vector2(0, -8)
        self.rect.center = player.rect.center
        self.original_image = self.image
        self.image = pygame.transform.rotate(self.original_image, player.angle - 90)
        self.image = self.image.convert_alpha()

        self.vel.rotate_ip(-player.angle + 90)

    def update(self):

        self.rect = self.rect.move(self.vel)
        if self.rect.y < -10:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()

        self.image = pygame.image.load(EXPLOSION_IMG_PATHS[0]).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0

    def update(self):

        if self.frame == len(EXPLOSION_IMG_PATHS):
            self.kill()
        else:
            self.image = pygame.image.load(EXPLOSION_IMG_PATHS[self.frame]).convert_alpha()
            self.rect = self.image.get_rect(center=self.rect.center)

        self.frame += 1


class SpaceshipShooter:

    def __init__(self, player, all_sprites_list, asteroid_list, bullet_list):
        self.player = player
        self.all_sprites_list = all_sprites_list
        self.asteroid_list = asteroid_list

        self.bullet_list = bullet_list
        self.score = 0

    def draw_screen(self):

        screen.fill(WHITE)
        screen.blit(pygame.transform.scale(background, (screen_width, screen_height)), (0, 0))
        self.all_sprites_list.draw(screen)

        my_font = pygame.font.SysFont("serif", screen_width // 30)
        score_text, score_rect = text_objects("Score: {0}".format(self.score), my_font, WHITE)
        score_rect.center = (screen_width / 15, screen_height / 30)
        screen.blit(score_text, score_rect)

        pygame.display.flip()

    def generate_asteroids_every_interval(self, radius, angle, num, last_record_time, interval):

        curr_record_time = pygame.time.get_ticks()
        if curr_record_time - last_record_time >= interval:

            for i in range(num):
                x = np.random.normal(size=1, loc=radius * math.cos(math.radians(angle)), scale=70)
                y = np.random.normal(size=1, loc=radius * math.sin(math.radians(angle)), scale=70)

                if x >= 0:
                    x = min(x, screen_width / 2) + screen_width / 2
                else:
                    x = max(x, -screen_width / 2) + screen_width / 2

                y = screen_height - min(y, screen_height)

                asteroid = Asteroid(x, y, angle)
                self.asteroid_list.add(asteroid)
                self.all_sprites_list.add(asteroid)

            return curr_record_time
        return last_record_time

    def check_hit_update_score(self):

        for bullet in self.bullet_list:

            asteroid_hit_list = pygame.sprite.spritecollide(bullet, self.asteroid_list, True)

            for asteroid in asteroid_hit_list:
                expl = Explosion((asteroid.rect.x + asteroid.width / 2, asteroid.rect.y + asteroid.height / 2))
                self.all_sprites_list.add(expl)
                explosion.add(expl)
                # self.explosion

                self.score += 1
                print(self.score)

            if asteroid_hit_list != []:
                self.all_sprites_list.remove(bullet)
                self.bullet_list.remove(bullet)

    def update_all_sprites(self):
        self.player.update()
        self.bullet_list.update()
        self.asteroid_list.update()
        explosion.update()

    def spaceship_game_loop(self):

        last_record_time = pygame.time.get_ticks()
        radius = math.sqrt((screen_width / 2) ** 2 + screen_height ** 2)

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if player.angle < 180:
                            player.angle_speed = 10

                    elif event.key == pygame.K_RIGHT:
                        if player.angle > 0:
                            player.angle_speed = -10

                    # elif event.key == pygame.VIDEORESIZE:
                    #     SCREEN_WIDTH = event.w
                    #     SCREEN_HEIGHT = event.h

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        player.angle_speed = 0
                    elif event.key == pygame.K_RIGHT:
                        player.angle_speed = 0
                    elif event.key == pygame.K_SPACE:
                        bullet = Bullet(self.player)
                        self.all_sprites_list.add(bullet)
                        self.bullet_list.add(bullet)

            last_record_time = self.generate_asteroids_every_interval(radius, player.angle, 3, last_record_time, interval)

            self.check_hit_update_score()

            self.update_all_sprites()

            self.draw_screen()


all_sprites_list = pygame.sprite.Group()
asteroid_list = pygame.sprite.Group()
bullet_list = pygame.sprite.Group()
explosion = pygame.sprite.Group()

player = Player((screen_width / 2, screen_height / 22 * 20))
all_sprites_list.add(player)
space_shooter = SpaceshipShooter(player, all_sprites_list, asteroid_list, bullet_list)

play = menu()

if play:
    space_shooter.spaceship_game_loop()
else:
    quit_game()
