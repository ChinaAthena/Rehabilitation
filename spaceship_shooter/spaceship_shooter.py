import pygame
from pygame.math import Vector2
import numpy as np
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
GREEN = (0, 128, 0)
MAROON = (128, 0, 0)

ASSETS_DIR = "../assets/"
BACKGROUND_IMG_PATH = ASSETS_DIR + "background.png"
SPACESHIP_IMG_PATH = ASSETS_DIR + "spaceship.png"
ASTEROID_IMG_PATH = ASSETS_DIR + "asteroid.png"
BULLET_IMG_PATH = ASSETS_DIR + "bullet.png"
EXPLOSION_IMG_PATHS = [ASSETS_DIR+"explosions/regularExplosion0%d.png" % i for i in range(9)]

pygame.init()


def draw_game_window(x=None, y=None):

    info_object = pygame.display.Info()
    if y is None:
        y = info_object.current_h
    if x is None:
        x = info_object.current_w

    return pygame.display.set_mode([x, y], pygame.RESIZABLE), x, y


def display_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def draw_button(surface, message, pos_x, pos_y, width, height, inactive_color, active_color):

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if pos_x + width > mouse[0] > pos_x and pos_y + height > mouse[1] > pos_y:
        pygame.draw.rect(surface, active_color, (pos_x, pos_y, width, height))

        if click[0] == 1:
            return True

    else:
        pygame.draw.rect(surface, inactive_color, (pos_x, pos_y, width, height))

    button_font = pygame.font.SysFont("serif", height // 3 * 2)
    display_text(message, button_font, WHITE, (pos_x + (width / 2)), (pos_y + (height / 2)))

    return False


def quit_game():
    pygame.quit()
    quit()


def menu(screen, screen_width, screen_height, headline):
        while True:
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    screen_width = event.w
                    screen_height = event.h

            headline_font = pygame.font.SysFont("serif", screen_width // 10)
            display_text(headline, headline_font, BLACK, (screen_width / 2), (screen_height / 2))

            button_play = draw_button(screen, "Go!", screen_width / 7 * 2, screen_height / 3 * 2, screen_width // 7,
                                      screen_height // 20, GREEN, BRIGHT_GREEN)
            button_quit = draw_button(screen, "Quit :(", screen_width / 7 * 4, screen_height / 3 * 2, screen_width // 7,
                                      screen_height // 20, MAROON, BRIGHT_RED)

            pygame.display.update()

            if button_play or button_quit:
                if button_play:
                    return True, screen, screen_width, screen_height
                else:
                    return False


class Player(pygame.sprite.Sprite):

    def __init__(self, player_image, center):
        super().__init__()

        self.image = player_image.copy()
        self.rect = self.image.get_rect(center=center)
        self.original_image = self.image

        self.angle = 90
        self.angle_speed = 0

    def update(self):

        if self.angle_speed:

            self.angle += self.angle_speed
            self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
            self.rect = self.image.get_rect(center=self.rect.center)

    def redraw(self, new_image, new_center):
        self.image = new_image.copy()
        self.original_image = self.image

        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect(center=new_center)


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, x, y, angle, screen_width, screen_height, asteroid_image):
        super().__init__()

        self.image = asteroid_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle

        self.vel = Vector2(0, -np.random.normal(size=1, loc=3, scale=1))
        self.vel.rotate_ip(-self.angle + 270)

        self.boundary_w = screen_width
        self.boundary_h = screen_height

    def update(self):
        self.rect = self.rect.move(self.vel)

        if self.rect.center[0] > self.boundary_w or self.rect.center[0] < 0 \
           or self.rect.center[1] > self.boundary_h or self.rect.center[1] < 0:
            self.kill()

    def redraw(self, new_image):
        self.image = pygame.transform.rotate(new_image.copy(), self.angle - 90)
        self.rect = self.image.get_rect(center=self.rect.center)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, player, bullet_image, vel):
        super().__init__()
        self.angle = player.angle
        self.image = pygame.transform.rotate(bullet_image.copy(), self.angle - 90)
        self.rect = self.image.get_rect(center=player.rect.center)

        self.vel = Vector2(0, vel)
        self.vel.rotate_ip(-self.angle + 90)

    def update(self):

        self.rect = self.rect.move(self.vel)
        if self.rect.y < -10:
            self.kill()

    def redraw(self, new_image, new_vel):
        self.image = pygame.transform.rotate(new_image.copy(), self.angle - 90)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.vel = Vector2(0, new_vel)
        self.vel.rotate_ip(-self.angle + 90)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()

        self.image = pygame.image.load(EXPLOSION_IMG_PATHS[0]).convert_alpha()
        self.rect = self.image.get_rect(center=center)
        self.frame = 0

    def update(self):

        if self.frame == len(EXPLOSION_IMG_PATHS):
            self.kill()
        else:
            self.image = pygame.image.load(EXPLOSION_IMG_PATHS[self.frame]).convert_alpha()
            self.rect = self.image.get_rect(center=self.rect.center)

        self.frame += 1


class SpaceshipShooter:

    def __init__(self, screen, screen_width, screen_height, player, all_sprites_list, asteroid_list, bullet_list, bullet_image, asteroid_image):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.bullet_image = bullet_image
        self.asteroid_image = asteroid_image

        self.player = player
        self.all_sprites_list = all_sprites_list
        self.asteroid_list = asteroid_list
        self.bullet_list = bullet_list
        
        self.score = 0

    def draw_screen(self):

        self.screen.fill(WHITE)
        self.screen.blit(pygame.transform.scale(background, (self.screen_width, self.screen_height)), (0, 0))
        self.all_sprites_list.draw(self.screen)

        score_font = pygame.font.SysFont("serif", self.screen_width // 30)
        display_text("Score: %d" % self.score, score_font, WHITE, self.screen_width / 15, self.screen_height / 30)

        pygame.display.flip()

    def generate_asteroids(self, radius, num, last_record_time, interval):

        curr_record_time = pygame.time.get_ticks()
        if curr_record_time - last_record_time >= interval:

            for i in range(num):
                x = np.random.normal(size=1, loc=radius * math.cos(math.radians(self.player.angle)), scale=70)
                y = np.random.normal(size=1, loc=radius * math.sin(math.radians(self.player.angle)), scale=70)

                if x >= 0:
                    x = min(x, self.screen_width / 2) + self.screen_width / 2
                else:
                    x = max(x, -self.screen_width / 2) + self.screen_width / 2

                y = self.screen_height - min(y, self.screen_height)

                asteroid = Asteroid(x, y, self.player.angle, self.screen_width, self.screen_height, self.asteroid_image)
                self.asteroid_list.add(asteroid)
                self.all_sprites_list.add(asteroid)

            return curr_record_time
        return last_record_time

    def check_hit_update_score(self):

        for bullet in self.bullet_list:

            asteroid_hit_list = pygame.sprite.spritecollide(bullet, self.asteroid_list, True)

            for asteroid in asteroid_hit_list:
                expl = Explosion((asteroid.rect.center[0], asteroid.rect.center[1]))
                self.all_sprites_list.add(expl)

                self.score += 1
                print(self.score)

            if asteroid_hit_list != []:
                bullet.kill()

    def spaceship_game_loop(self):

        last_record_time = pygame.time.get_ticks()
        radius = math.sqrt((self.screen_width / 2) ** 2 + self.screen_height ** 2)

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.player.angle < 180:
                            self.player.angle_speed = 10

                    elif event.key == pygame.K_RIGHT:
                        if self.player.angle > 0:
                            self.player.angle_speed = -10

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.player.angle_speed = 0
                    elif event.key == pygame.K_RIGHT:
                        self.player.angle_speed = 0
                    elif event.key == pygame.K_SPACE:
                        vel = -radius//100
                        bullet = Bullet(self.player, self.bullet_image, vel)
                        self.all_sprites_list.add(bullet)
                        self.bullet_list.add(bullet)

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.screen_width = event.w
                    self.screen_height = event.h
                    radius = math.sqrt((self.screen_width / 2) ** 2 + self.screen_height ** 2)

                    new_player_image = pygame.transform.scale(pygame.image.load(SPACESHIP_IMG_PATH).convert_alpha(),
                                                              (self.screen_width // 20, self.screen_width // 20 * 7 // 4))

                    player.redraw(new_player_image, (self.screen_width / 2, self.screen_height / 22 * 20))

                    self.asteroid_image = pygame.transform.scale(pygame.image.load(ASTEROID_IMG_PATH).convert_alpha(),
                                                                 (self.screen_width // 25, self.screen_width // 25))

                    self.bullet_image = pygame.transform.scale(pygame.image.load(BULLET_IMG_PATH).convert_alpha(),
                                                               (self.screen_width // 120, self.screen_width // 120 * 18 // 10))

                    for asteroid in self.asteroid_list:
                        asteroid.redraw(self.asteroid_image)
                    for bullet in self.bullet_list:
                        new_vel = -radius//100
                        bullet.redraw(self.bullet_image, new_vel)

            last_record_time = self.generate_asteroids(radius, 3, last_record_time, asteroids_generate_interval)

            self.check_hit_update_score()

            self.all_sprites_list.update()

            self.draw_screen()


screen, screen_width, screen_height = draw_game_window(600, 600)
pygame.display.set_caption("Spaceship Game")
play, screen, screen_width, screen_height = menu(screen, screen_width, screen_height, "Spaceship Shooter")


background = pygame.image.load(BACKGROUND_IMG_PATH)
asteroids_generate_interval = 3000
player_image = pygame.transform.scale(pygame.image.load(SPACESHIP_IMG_PATH).convert_alpha(),
                                      (screen_width // 20, screen_width // 20 * 7 // 4))
asteroid_image = pygame.transform.scale(pygame.image.load(ASTEROID_IMG_PATH).convert_alpha(),
                                        (screen_width // 25, screen_width // 25))
bullet_image = pygame.transform.scale(pygame.image.load(BULLET_IMG_PATH).convert_alpha(),
                                      (screen_width // 120, screen_width // 120 * 18 // 10))


if play:
    all_sprites_list = pygame.sprite.Group()
    asteroid_list = pygame.sprite.Group()
    bullet_list = pygame.sprite.Group()

    player = Player(player_image, (screen_width / 2, screen_height / 22 * 20))
    all_sprites_list.add(player)
    space_shooter = SpaceshipShooter(screen, screen_width, screen_height, player, all_sprites_list, asteroid_list,
                                     bullet_list, bullet_image, asteroid_image)
    space_shooter.spaceship_game_loop()
else:
    quit_game()
