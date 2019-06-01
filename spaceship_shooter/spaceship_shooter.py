import pygame
from pygame.math import Vector2
from pygame.locals import *
import random
import numpy as np
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
Bright_RED = (255, 0, 0)
Bright_Green = (0, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
MAROON = (128, 0, 0)
Bright_Yellow = (255, 255, 0)
Bright_Orange = (255, 165, 0)
Orange_Red = (255, 69, 0)
GOLD = (255, 215, 0)

pygame.init()

ASSETS_DIR = "../assets/"
BACKGROUND_IMG_PATH = ASSETS_DIR + "background.png"
SPACESHIP_IMG_PATH = ASSETS_DIR + "spaceship.png"
ASTEROID_IMG_PATH = ASSETS_DIR + "asteroid.png"
BULLET_IMG_PATH = ASSETS_DIR + "bullet.png"
EXPLOSION_IMG_PATHS = [ASSETS_DIR+"explosions/regularExplosion0%d.png" % i for i in range(9)]

infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
# SCREEN_WIDTH = 700
# SCREEN_HEIGHT = 700
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], RESIZABLE)
pygame.display.set_caption("Spaceship Game")
background = pygame.image.load(BACKGROUND_IMG_PATH)


def text_objects(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def create_button(message, x, y, width, height, inactive_color, active_color):

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height))

        if click[0] == 1:
            return True

    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    small_text = pygame.font.SysFont("serif", 40)
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

            large_text = pygame.font.SysFont("serif", 80)
            text_surf, text_rect = text_objects("Spaceship Shooter", large_text, BLACK)
            text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))
            screen.blit(text_surf, text_rect)

            button_play = create_button("Go!", SCREEN_WIDTH/5*2, SCREEN_HEIGHT/3*2, 100, 50, GREEN, Bright_Green)
            button_quit = create_button("Quit :(", SCREEN_WIDTH/5*2.5, SCREEN_HEIGHT/3*2, 100, 50, MAROON, Bright_RED)

            pygame.display.update()
            clock.tick(20)

            if button_play or button_quit:
                if button_play:
                    return True
                else:
                    return False


class Player(pygame.sprite.Sprite):

    def __init__(self, image, position):
        super().__init__()

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH//20, SCREEN_WIDTH//20 * 7 // 4))
        self.rect = self.image.get_rect()

        self.rect.center = position
        self.original_image = self.image
        self.angle = 90
        self.angle_speed = 0

    def update(self):

        if self.angle_speed:

            self.angle += self.angle_speed
            self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
            self.image = self.image.convert_alpha()
            self.rect = self.image.get_rect(center=self.rect.center)


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, image, x, y, angle):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH // 25, SCREEN_WIDTH // 25))
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.vel = Vector2(np.random.normal(size=1, loc=3, scale=1), np.random.normal(size=1, loc=3, scale=1))
        self.rect.x = x
        self.rect.y = y
        self.vel.rotate_ip(random.randrange(0, 360))

    def update(self):
        self.rect = self.rect.move(self.vel)

        if self.rect.x > SCREEN_WIDTH or self.rect.x < 0 \
           or self.rect.y > SCREEN_HEIGHT or self.rect.y < 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):

    def __init__(self, image, player):
        super().__init__()

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH // 120, SCREEN_WIDTH // 120 * 18 // 10))
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
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 9

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
        if self.frame == len(EXPLOSION_IMG_PATHS):
            self.kill()
        else:
            self.image = pygame.image.load(EXPLOSION_IMG_PATHS[self.frame]).convert_alpha()
            self.rect = self.image.get_rect(center=self.rect.center)


class SpaceshipShooter:

    def __init__(self, player, all_sprites_list, asteroid_list, bullet_list):
        self.player = player
        self.all_sprites_list = all_sprites_list
        self.asteroid_list = asteroid_list

        self.bullet_list = bullet_list
        self.score = 0

    def draw_screen(self):

        screen.fill(WHITE)
        screen.blit(pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        self.all_sprites_list.draw(screen)

        my_font = pygame.font.SysFont("serif", 32)
        score_text, score_rect = text_objects("Score: {0}".format(self.score), my_font, WHITE)
        score_rect.center = (SCREEN_WIDTH/20, SCREEN_HEIGHT/25)
        screen.blit(score_text, score_rect)

        pygame.display.flip()

    def generate_asteroids_every_interval(self, radius, angle, num, last_record_time, interval):

        curr_record_time = pygame.time.get_ticks()
        if curr_record_time - last_record_time >= interval:

            for i in range(num):
                x = np.random.normal(size=1, loc=radius * math.cos(math.radians(angle)), scale=70)
                y = np.random.normal(size=1, loc=radius * math.sin(math.radians(angle)), scale=70)

                if x >= 0:
                    x = min(x, SCREEN_WIDTH / 2) + SCREEN_WIDTH / 2
                else:
                    x = max(x, -SCREEN_WIDTH / 2) + SCREEN_WIDTH / 2

                y = SCREEN_HEIGHT - min(y, SCREEN_HEIGHT)

                asteroid = Asteroid(ASTEROID_IMG_PATH, x, y, angle)
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

                self.score += 1
                print(self.score)

            if asteroid_hit_list != []:
                self.all_sprites_list.remove(bullet)
                self.bullet_list.remove(bullet)

    def update_all_sprites(self):
        self.all_sprites_list.update()

    def spaceship_game_loop(self):

        last_record_time = pygame.time.get_ticks()
        interval = 3000

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

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        player.angle_speed = 0
                    elif event.key == pygame.K_RIGHT:
                        player.angle_speed = 0
                    elif event.key == pygame.K_SPACE:
                        bullet = Bullet(BULLET_IMG_PATH, self.player)
                        self.all_sprites_list.add(bullet)
                        self.bullet_list.add(bullet)

            last_record_time = self.generate_asteroids_every_interval(radius, player.angle, 3, last_record_time, interval)

            self.check_hit_update_score()

            self.update_all_sprites()

            self.draw_screen()


clock = pygame.time.Clock()
radius = math.sqrt((SCREEN_WIDTH/2)**2 + SCREEN_HEIGHT**2)
all_sprites_list = pygame.sprite.Group()
asteroid_list = pygame.sprite.Group()
bullet_list = pygame.sprite.Group()
explosion = pygame.sprite.Group()

player = Player(SPACESHIP_IMG_PATH, (SCREEN_WIDTH/2, SCREEN_HEIGHT/22*20))
all_sprites_list.add(player)
space_shooter = SpaceshipShooter(player, all_sprites_list, asteroid_list, bullet_list)

play = menu()

if play:
    space_shooter.spaceship_game_loop()
else:
    quit_game()
