import pygame
import random
from pygame.math import Vector2
import numpy as np
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
GREEN = (0, 128, 0)
MAROON = (128, 0, 0)
BRIGHT_BLUE = (0, 0, 255)
BLUE = (0, 0, 128)

ASSETS_DIR = "../assets/"
BACKGROUND_IMG_PATH = ASSETS_DIR + "background.png"
SPACESHIP_IMG_PATH = ASSETS_DIR + "spaceship.png"
ASTEROID_IMG_PATH = [ASSETS_DIR + "asteroid0%d.png" % i for i in range(3)]
BULLET_IMG_PATH = ASSETS_DIR + "bullet.png"
EXPLOSION_IMG_PATHS = [ASSETS_DIR+"explosions/regularExplosion0%d.png" % i for i in range(9)]

pygame.init()


def draw_game_window(x=None, y=None):

    info_object = pygame.display.Info()
    if y is None:
        y = info_object.current_h
    if x is None:
        x = info_object.current_w

    return pygame.display.set_mode([x, y], pygame.RESIZABLE)


def display_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def draw_button(surface, message, pos_x, pos_y, width, height, inactive_color, active_color, button_font):

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if pos_x + width > mouse[0] > pos_x and pos_y + height > mouse[1] > pos_y:
        pygame.draw.rect(surface, active_color, (pos_x, pos_y, width, height))

        if click[0] == 1:
            return True

    else:
        pygame.draw.rect(surface, inactive_color, (pos_x, pos_y, width, height))

    display_text(message, button_font, WHITE, (pos_x + (width / 2)), (pos_y + (height / 2)))

    return False


def quit_game():
    pygame.quit()
    quit()


def menu(screen, headline):
    screen_width = screen.get_width()
    screen_height = screen.get_height()

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

        button_font = pygame.font.SysFont("serif", screen_height // 30)
        button_play = draw_button(screen, "Go!", screen_width / 7 * 2, screen_height / 3 * 2, screen_width // 7,
                                  screen_height // 20, GREEN, BRIGHT_GREEN, button_font)
        button_quit = draw_button(screen, "Quit :(", screen_width / 7 * 4, screen_height / 3 * 2, screen_width // 7,
                                  screen_height // 20, MAROON, BRIGHT_RED, button_font)

        pygame.display.update()

        if button_play:
            return True, screen
        elif button_quit:
            return False


def pause(screen_width, screen_height):

    paused = True

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    paused = False

                elif event.key == pygame.K_q:
                    quit_game()

        screen.fill(WHITE)

        larger_font = pygame.font.SysFont("serif", screen_width // 10)
        display_text("Paused", larger_font, BLACK, (screen_width / 2), (screen_height / 2))
        smaller_font = pygame.font.SysFont("serif", screen_width // 30)
        display_text("Press C to continue or Q to quit.", smaller_font, BLACK, (screen_width / 4), (screen_height / 4))

        pygame.display.update()


class Player(pygame.sprite.Sprite):

    def __init__(self, player_image, position):
        super().__init__()

        self.image = player_image.copy()
        self.rect = self.image.get_rect(center=position)
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


class MovingSprite(pygame.sprite.Sprite):

    def __init__(self, image, position, vel, screen_width, screen_height):
        super().__init__()

        self.image = image.copy()
        self.rect = self.image.get_rect(center=position)
        self.vel = vel
        self.boundary_w = screen_width
        self.boundary_h = screen_height

    def update(self):
        self.rect = self.rect.move(self.vel)

        if self.rect.center[0] > self.boundary_w or self.rect.center[0] < 0 \
           or self.rect.center[1] > self.boundary_h or self.rect.center[1] < 0:
            self.kill()

    def relocate(self, new_screen_width, new_screen_height):
        width_proportion = self.rect.center[0] / self.boundary_w
        height_proportion = self.rect.center[1] / self.boundary_h
        vel_proportion = [self.vel[0] / self.boundary_w, self.vel[1] / self.boundary_h]

        self.boundary_w = new_screen_width
        self.boundary_h = new_screen_height

        self.vel = (vel_proportion[0] * self.boundary_w, vel_proportion[1] * self.boundary_h)
        self.rect.center = (width_proportion * self.boundary_w, height_proportion * self.boundary_h)


class Asteroid(MovingSprite):

    def __init__(self, asteroid_image, image_index, position, vel, screen_width, screen_height):
        MovingSprite.__init__(self, asteroid_image, position, vel, screen_width, screen_height)

        self.image_index = image_index
        self.rotate_angle = 2
        self.angle = 90
        self.original_image = self.image

    def redraw(self, new_image, new_screen_width, new_screen_height):
        self.relocate(new_screen_width, new_screen_height)
        self.image = new_image.copy()
        self.original_image = new_image.copy()

    def rotate(self):

        self.angle += self.rotate_angle
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect(center=self.rect.center)


class Bullet(MovingSprite):

    def __init__(self, bullet_image, vel, angle, position, screen_width, screen_height):
        MovingSprite.__init__(self, bullet_image, position, vel, screen_width, screen_height)

        self.angle = angle
        self.image = pygame.transform.rotate(self.image, self.angle - 90)

    def redraw(self, new_image, new_screen_width, new_screen_height):
        self.relocate(new_screen_width, new_screen_height)
        self.image = pygame.transform.rotate(new_image.copy(), self.angle - 90)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()

        self.image = pygame.image.load(EXPLOSION_IMG_PATHS[0]).convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.frame = 0

    def update(self):

        if self.frame == len(EXPLOSION_IMG_PATHS):
            self.kill()
        else:
            self.image = pygame.image.load(EXPLOSION_IMG_PATHS[self.frame]).convert_alpha()
            self.rect = self.image.get_rect(center=self.rect.center)

        self.frame += 1


class SpaceshipShooter:

    def __init__(self, screen):
        self.screen = screen

        self.player_image = pygame.image.load(SPACESHIP_IMG_PATH).convert_alpha()
        self.asteroid_image = [pygame.image.load(ASTEROID_IMG_PATH[0]).convert_alpha(),
                               pygame.image.load(ASTEROID_IMG_PATH[1]).convert_alpha(),
                               pygame.image.load(ASTEROID_IMG_PATH[2]).convert_alpha()]
        self.bullet_image = pygame.image.load(BULLET_IMG_PATH).convert_alpha()

        self.player = Player(pygame.transform.scale(self.player_image,
                                                    (self.screen_width // scale_of_player_image[0],
                                                     self.screen_width // scale_of_player_image[1])),
                             (self.screen_width * player_relative_position[0],
                              self.screen_height * player_relative_position[1]))
        self.asteroid_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.explosion_list = pygame.sprite.Group()
        
        self.score = 0
        self.turns_done = 0

        self.seconds_before_next_call_to_generate_asteroids = None
        self.seconds_before_next_call_to_generate_bullets = None
        self.last_record_time_for_asteroids = None
        self.last_record_time_for_bullets = None
        self.counter_clockwise = True

    @property
    def screen_width(self):
        return self.screen.get_width()

    @property
    def screen_height(self):
        return self.screen.get_height()

    @property
    def radius(self):
        return math.sqrt((self.screen_width / 2) ** 2 + self.screen_height ** 2)

    def draw_screen(self):
        self.screen.blit(pygame.transform.scale(background, (self.screen_width, self.screen_height)), (0, 0))

        self.screen.blit(self.player.image, self.player.rect)
        self.bullet_list.draw(self.screen)
        self.asteroid_list.draw(self.screen)
        self.explosion_list.draw(self.screen)

        score_font = pygame.font.SysFont("serif", self.screen_width // 30)
        display_text("Score: %d" % self.score, score_font, WHITE, self.screen_width / 15, self.screen_height / 30)

    def get_position_on_screen_edge(self, angle):
        pos_x = self.radius * math.cos(math.radians(angle))
        pos_y = self.radius * math.sin(math.radians(angle))

        if pos_x >= 0:
            pos_x = min(pos_x, self.screen_width / 2) + self.screen_width / 2
        else:
            pos_x = max(pos_x, -self.screen_width / 2) + self.screen_width / 2

        pos_y = self.screen_height - min(pos_y, self.screen_height)

        return pos_x, pos_y

    def generate_asteroid_with_random_image(self, speed, position):
        num = random.randrange(3)
        asteroid_image = pygame.transform.scale(self.asteroid_image[num],
                                                (self.screen_width // scale_of_asteroid_image[0],
                                                 self.screen_width // scale_of_asteroid_image[1]))
        asteroid = Asteroid(asteroid_image, num, position, speed, self.screen_width, self.screen_height)
        self.asteroid_list.add(asteroid)

    def generate_asteroid_with_random_speed_and_angle_on_screen_edge(
            self,
            speed_mean,
            angle_mean,
            angle_variance,
            counter_clockwise
    ):

        vel = Vector2(0, -speed_mean)
        angle_difference = 15
        if counter_clockwise:
            angle = np.random.normal(size=1, loc=angle_mean+angle_difference, scale=angle_variance)
        else:
            angle = np.random.normal(size=1, loc=angle_mean-angle_difference, scale=angle_variance)

        vel.rotate_ip(-angle + 270)

        position = self.get_position_on_screen_edge(angle)
        return self.generate_asteroid_with_random_image(vel, position)

    def generate_asteroids_with_a_random_frequency(self, lam, *args):

        if self.seconds_before_next_call_to_generate_asteroids is None:
            self.seconds_before_next_call_to_generate_asteroids = np.random.poisson(lam)

        curr_record_time = pygame.time.get_ticks()

        if curr_record_time - self.last_record_time_for_asteroids > self.seconds_before_next_call_to_generate_asteroids:
            self.last_record_time_for_asteroids = curr_record_time
            self.seconds_before_next_call_to_generate_asteroids = None
            return self.generate_asteroid_with_random_speed_and_angle_on_screen_edge(*args)

    def generate_bullets_with_a_random_frequency_and_specific_vel(self, lam, vel):

        if self.seconds_before_next_call_to_generate_bullets is None:
            self.seconds_before_next_call_to_generate_bullets = np.random.poisson(lam)

        curr_record_time = pygame.time.get_ticks()

        if curr_record_time - self.last_record_time_for_bullets > self.seconds_before_next_call_to_generate_bullets:
            self.last_record_time_for_bullets = curr_record_time
            self.seconds_before_next_call_to_generate_bullets = None

            bullet_vel = Vector2(0, -vel)
            bullet_vel.rotate_ip(-self.player.angle + 90)

            bullet_image = pygame.transform.scale(self.bullet_image,
                                                  (self.screen_width // scale_of_bullet_image[0],
                                                   self.screen_width // scale_of_bullet_image[1]))

            bullet = Bullet(bullet_image, bullet_vel, self.player.angle, self.player.rect.center,
                            self.screen_width, self.screen_height)

            self.bullet_list.add(bullet)

    def check_hit_update_score(self):

        for bullet in self.bullet_list:

            asteroid_hit_list = pygame.sprite.spritecollide(bullet, self.asteroid_list, True)

            for asteroid in asteroid_hit_list:
                exp = Explosion((asteroid.rect.center[0], asteroid.rect.center[1]))
                self.explosion_list.add(exp)
                self.score += 1

            if len(asteroid_hit_list) is not 0:
                bullet.kill()

    def update_all_sprites(self):
        self.player.update()
        self.explosion_list.update()
        self.asteroid_list.update()
        self.bullet_list.update()

    def redraw_all_sprites(self):

        player_image = pygame.transform.scale(self.player_image,
                                              (self.screen_width // scale_of_player_image[0],
                                               self.screen_width // scale_of_player_image[1]))
        self.player.redraw(player_image, (self.screen_width * player_relative_position[0],
                                          self.screen_height * player_relative_position[1]))

        for asteroid in self.asteroid_list:
            asteroid_image = pygame.transform.scale(self.asteroid_image[asteroid.image_index],
                                                    (self.screen_width // scale_of_asteroid_image[0],
                                                     self.screen_width // scale_of_asteroid_image[1]))
            asteroid.redraw(asteroid_image, self.screen_width, self.screen_height)

        bullet_image = pygame.transform.scale(self.bullet_image,
                                              (self.screen_width // scale_of_bullet_image[0],
                                               self.screen_width // scale_of_bullet_image[1]))
        for bullet in self.bullet_list:
            bullet.redraw(bullet_image, self.screen_width, self.screen_height)

    def spaceship_game_loop(self):

        self.last_record_time_for_asteroids = pygame.time.get_ticks()
        self.last_record_time_for_bullets = pygame.time.get_ticks()

        while True:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.player.angle >= 180:
                            if self.counter_clockwise is True:
                                self.counter_clockwise = False
                                self.turns_done = self.turns_done + 1
                                print("You have done %d turns. Congrats" % self.turns_done)

                        if self.player.angle < 180:
                            self.player.angle_speed = 5

                    elif event.key == pygame.K_RIGHT:
                        if self.player.angle <= 0:
                            if self.counter_clockwise is False:
                                self.counter_clockwise = True
                                self.turns_done = self.turns_done + 1
                                print("You have done %d turns. Congrats" % self.turns_done)

                        if self.player.angle > 0:
                            self.player.angle_speed = -5

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.player.angle_speed = 0

                    elif event.key == pygame.K_RIGHT:
                        self.player.angle_speed = 0

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.redraw_all_sprites()

            self.generate_asteroids_with_a_random_frequency(lam_of_generating_asteroid,
                                                            self.radius // scale_of_asteroid_vel,
                                                            self.player.angle, angle_variance_of_asteroid,
                                                            self.counter_clockwise)

            self.generate_bullets_with_a_random_frequency_and_specific_vel(lam_of_generating_bullet,
                                                                           self.radius // scale_of_bullet_vel)

            self.check_hit_update_score()

            self.update_all_sprites()

            self.draw_screen()

            button_font = pygame.font.SysFont("serif", self.screen_height // 30)
            button_pause = draw_button(self.screen, "Pause", self.screen_width / 15 * 12, self.screen_height / 40,
                                       self.screen_width // 7, self.screen_height // 20, BLUE, BRIGHT_BLUE, button_font)

            if button_pause:
                pause(self.screen_width, self.screen_height)

            if self.turns_done > 10:
                print("Congratulations! You finish the exercise!")

            for asteroid in self.asteroid_list:
                asteroid.rotate()

            pygame.display.flip()


if __name__ == '__main__':
    scale_of_player_image = [10, 6]
    scale_of_asteroid_image = [7, 7]
    scale_of_bullet_image = [80, 50]
    lam_of_generating_asteroid = 1000
    lam_of_generating_bullet = 400
    scale_of_asteroid_vel = 170
    scale_of_bullet_vel = 150
    angle_variance_of_asteroid = 0.01
    player_relative_position = [0.5, 0.9]

    screen = draw_game_window(700, 600)
    pygame.display.set_caption("Spaceship Game")
    play, screen = menu(screen, "Spaceship Shooter")

    if play:
        background = pygame.image.load(BACKGROUND_IMG_PATH)
        space_shooter = SpaceshipShooter(screen)
        space_shooter.spaceship_game_loop()

    else:
        quit_game()
