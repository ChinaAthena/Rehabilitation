import constant as cons
import pygame
import Leap, sys

def load_transparent_images(path, is_transparent=True):
    image = pygame.image.load(path).convert()

    if is_transparent:
        image.set_colorkey(cons.BLACK)
    return image


def initialize_game_window(width=None, height=None):

    info_object = pygame.display.Info()
    if height is None:
        height = info_object.current_h
    if width is None:
        width = info_object.current_w

    return pygame.display.set_mode([width, height], pygame.RESIZABLE)


def draw_text(screen, text, font, color, x, y):
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

    draw_text(surface, message, button_font, cons.WHITE, (pos_x + (width / 2)), (pos_y + (height / 2)))

    return False


def quit_game():
    pygame.quit()
    quit()


def menu(screen, headline):
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    while True:
        screen.fill(cons.WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True, screen
            elif event.type == pygame.VIDEORESIZE:
                screen_width = event.w
                screen_height = event.h

                if screen_width < 400:
                    screen_width = 400
                if screen_height < 300:
                    screen_height = 300
                if screen_width < 1 / 2 * screen_height:
                    screen_width = 1 / 2 * screen_height
                if screen_width > 2 * screen_height:
                    screen_width = 2 * screen_height

                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

        headline_font = pygame.font.SysFont("serif", screen_width // 10)
        draw_text(screen, headline, headline_font, cons.BLACK, (screen_width / 2), (screen_height / 2))

        button_font = pygame.font.SysFont("serif", screen_height // 30)
        button_play = draw_button(screen, "Go!", screen_width / 7 * 2, screen_height / 3 * 2, screen_width // 7,
                                  screen_height // 20, cons.GREEN, cons.BRIGHT_GREEN, button_font)
        button_quit = draw_button(screen, "Quit :(", screen_width / 7 * 4, screen_height / 3 * 2, screen_width // 7,
                                  screen_height // 20, cons.MAROON, cons.BRIGHT_RED, button_font)

        pygame.display.update()

        if button_play:
            return True, screen
        elif button_quit:
            return False


# make this pause_screen a class
def pause_screen(screen, frame):
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    paused = True

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit_game()

                # elif event.key == pygame.K_c:
                #     paused = False

        hands = frame.hands

        if not hands.is_empty:
            first_hand = hands[0]
            pitch = first_hand.direction.pitch
            print(pitch)
            if pitch < 1:
                paused = False

        screen.fill(cons.WHITE)

        larger_font = pygame.font.SysFont("serif", screen_width // 10)
        draw_text(screen, "Paused", larger_font, cons.BLACK, (screen_width / 2), (screen_height / 2))
        smaller_font = pygame.font.SysFont("serif", screen_width // 30)
        draw_text(screen, "Press C to continue or Q to quit.", smaller_font, cons.BLACK,
                  (screen_width / 4), (screen_height / 4))

        pygame.display.update()
