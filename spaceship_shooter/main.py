from Spaceship_Shooter import SpaceshipShooterGame
from main_function import initialize_game_window, menu, load_transparent_images, quit_game
import constant as cons
import pygame
from twilio.rest import Client


if __name__ == '__main__':
    # Your Account SID from twilio.com/console
    account_sid = "AC82b1c13b2ef1aec55246fca1d131a08c"
    # Your Auth Token from twilio.com/console
    auth_token = "9c729f510477e860d22f57faf28b4a5b"

    pygame.init()

    screen = initialize_game_window(700, 600)

    background = pygame.image.load(cons.BACKGROUND_IMG_PATH).convert()

    player_image = load_transparent_images(cons.SPACESHIP_IMG_PATH)

    asteroid_image = [load_transparent_images(cons.ASTEROID_IMG_PATH[0]), load_transparent_images(cons.ASTEROID_IMG_PATH[1])]

    bullet_image = load_transparent_images(cons.BULLET_IMG_PATH)

    pygame.display.set_caption("Spaceship Game")

    play, screen = menu(screen, "Spaceship Shooter")

    if play:
        print("hi")
        space_shooter = SpaceshipShooterGame(screen, background, player_image, asteroid_image, bullet_image)
        data = space_shooter.spaceship_game_loop()

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            to="+12137132689",
            from_="+12132779054",
            body="Hello! This is an exercise report from your patient. "
                 "The number of turns your patient finished today is " + str(data[0]) +
                 ". The total time spent for today's exercise is " + str(data[1]) + " seconds. Good job!")

        print(message.sid)

    else:
        quit_game()
