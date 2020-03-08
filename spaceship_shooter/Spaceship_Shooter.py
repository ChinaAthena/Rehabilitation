import pygame
import random
from pygame.math import Vector2
import numpy as np
import math
from main_function import draw_text, quit_game, draw_button, pause_screen
import constant as cons
import Leap, sys

class Player(pygame.sprite.Sprite):

    def __init__(self, player_image, position):
        super().__init__()

        self.image = player_image.copy()
        self.rect = self.image.get_rect(center=position)
        self.original_image = self.image

        self.angle = 90
        self.angle_speed = 0

    def update(self):

        # if self.angle_speed:

            # self.angle += self.angle_speed
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

        self.image = pygame.image.load(cons.EXPLOSION_IMG_PATHS[0]).convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.frame = 0

    def update(self):

        if self.frame == len(cons.EXPLOSION_IMG_PATHS):
            self.kill()
        else:
            self.image = pygame.image.load(cons.EXPLOSION_IMG_PATHS[self.frame]).convert_alpha()
            self.rect = self.image.get_rect(center=self.rect.center)

        self.frame += 1


class SpaceshipShooterGame:

    def __init__(self, screen, background, player_image, asteroid_image, bullet_image):
        self.screen = screen
        self.background = background

        self.player_image = player_image
        self.asteroid_image = asteroid_image
        self.bullet_image = bullet_image

        self.player = Player(pygame.transform.scale(self.player_image,
                                                    (round(self.screen_width * cons.scale_of_player_image[0]),
                                                     round(self.screen_width * cons.scale_of_player_image[1]))),
                             (self.screen_width * cons.player_relative_position[0],
                              self.screen_height * cons.player_relative_position[1]))

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
        self.blink = 0
        self.alpha = 255

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
        self.screen.blit(pygame.transform.scale(self.background, (self.screen_width, self.screen_height)), (0, 0))

        self.bullet_list.draw(self.screen)
        self.asteroid_list.draw(self.screen)
        self.explosion_list.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)

        score_font = pygame.font.SysFont("serif", self.screen_width // 30)
        draw_text(self.screen, "Score: %d" % self.score, score_font, cons.WHITE,
                  self.screen_width / 15, self.screen_height / 30)

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
        num = random.randrange(len(self.asteroid_image))
        image = pygame.transform.scale(self.asteroid_image[num],
                                       (round(self.screen_width * cons.scale_of_asteroid_image[0]),
                                        round(self.screen_width * cons.scale_of_asteroid_image[1])))
        asteroid = Asteroid(image, num, position, speed, self.screen_width, self.screen_height)
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

        if self.blink == 0:

            if self.seconds_before_next_call_to_generate_bullets is None:
                self.seconds_before_next_call_to_generate_bullets = np.random.poisson(lam)

            curr_record_time = pygame.time.get_ticks()

            if curr_record_time - self.last_record_time_for_bullets > self.seconds_before_next_call_to_generate_bullets:
                self.last_record_time_for_bullets = curr_record_time
                self.seconds_before_next_call_to_generate_bullets = None

                bullet_vel = Vector2(0, -vel)
                bullet_vel.rotate_ip(-self.player.angle + 90)

                image = pygame.transform.scale(self.bullet_image,
                                               (round(self.screen_width * cons.scale_of_bullet_image[0]),
                                                round(self.screen_width * cons.scale_of_bullet_image[1])))

                bullet = Bullet(image, bullet_vel, self.player.angle, self.player.rect.center,
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

        new_player_image = pygame.transform.scale(self.player_image,
                                                  (round(self.screen_width * cons.scale_of_player_image[0]),
                                                   round(self.screen_width * cons.scale_of_player_image[1])))
        self.player.redraw(new_player_image, (self.screen_width * cons.player_relative_position[0],
                                              self.screen_height * cons.player_relative_position[1]))

        for asteroid in self.asteroid_list:
            new_asteroid_image = pygame.transform.scale(self.asteroid_image[asteroid.image_index],
                                                        (round(self.screen_width * cons.scale_of_asteroid_image[0]),
                                                         round(self.screen_width * cons.scale_of_asteroid_image[1])))
            asteroid.redraw(new_asteroid_image, self.screen_width, self.screen_height)

        new_bullet_image = pygame.transform.scale(self.bullet_image,
                                                  (round(self.screen_width * cons.scale_of_bullet_image[0]),
                                                   round(self.screen_width * cons.scale_of_bullet_image[1])))
        for bullet in self.bullet_list:
            bullet.redraw(new_bullet_image, self.screen_width, self.screen_height)

    def check_hit_blink_image(self):

        asteroid_hit_list = pygame.sprite.spritecollide(self.player, self.asteroid_list, True)

        if len(asteroid_hit_list) is not 0:
            if self.blink == 0:
                self.blink = 16
            self.score -= 1

        if self.blink:
            self.blink -= 1
            if self.alpha == 255:
                self.alpha = 0
            else:
                self.alpha = 255
            self.player.image.set_alpha(self.alpha)
            pygame.time.delay(20)

    def spaceship_game_loop(self):

        self.last_record_time_for_asteroids = pygame.time.get_ticks()
        self.last_record_time_for_bullets = pygame.time.get_ticks()
        controller = Leap.Controller()

        while True:
            self.screen.fill(cons.WHITE)

            frame = controller.frame()
            hands = frame.hands

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    time = pygame.time.get_ticks() * 0.001
                    return [self.turns_done, round(time)]
                    # quit_game()

                elif event.type == pygame.VIDEORESIZE:
                    screen_width = event.w
                    screen_height = event.h

                    if screen_width < 400:
                        screen_width = 400
                    if screen_height < 300:
                        screen_height = 300
                    if screen_width < 1/2 * screen_height:
                        screen_width = 1/2 * screen_height
                    if screen_width > 2 * screen_height:
                        screen_width = 2 * screen_height

                    self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                    self.redraw_all_sprites()

            if not hands.is_empty:
                first_hand = hands[0]
                yaw = first_hand.direction.yaw
                # print("----yaw-----")
                # print(yaw * -90 + 90)
                current_angle = yaw * -90 + 90

                if current_angle >= 180:
                    if self.counter_clockwise is True:
                        self.counter_clockwise = False
                        self.turns_done = self.turns_done + 1
                        print("You have done %d turns. Congrats" % self.turns_done)
                    current_angle = 180
                elif current_angle <= 0:
                    if self.counter_clockwise is False:
                        self.counter_clockwise = True
                        self.turns_done = self.turns_done + 1
                        print("You have done %d turns. Congrats" % self.turns_done)
                    current_angle = 0

                self.player.angle = current_angle
                # time.sleep(1)

            self.check_hit_blink_image()

            self.generate_asteroids_with_a_random_frequency(cons.lam_of_generating_asteroid,
                                                            self.radius * cons.scale_of_asteroid_vel,
                                                            self.player.angle, cons.angle_variance_of_asteroid,
                                                            self.counter_clockwise)

            self.generate_bullets_with_a_random_frequency_and_specific_vel(cons.lam_of_generating_bullet,
                                                                           self.radius * cons.scale_of_bullet_vel)

            self.check_hit_update_score()

            self.update_all_sprites()

            self.draw_screen()

            button_font = pygame.font.SysFont("serif", self.screen_height // 30)
            button_pause = draw_button(self.screen, "Pause", self.screen_width / 15 * 12, self.screen_height / 40,
                                       self.screen_width // 7, self.screen_height // 20, cons.BLUE, cons.BRIGHT_BLUE, button_font)

            if button_pause:
                pause_screen(self.screen)

            if self.turns_done > 10:
                print("Congratulations! You finish the exercise!")

            for asteroid in self.asteroid_list:
                asteroid.rotate()

            pygame.display.update()

