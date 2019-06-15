from spaceship_shooter.Spaceship_Shooter import *
from spaceship_shooter.main_function import *

if __name__ == '__main__':
    pygame.init()

    screen = initialize_game_window(700, 600)

    player_image = load_transparent_images(SPACESHIP_IMG_PATH)
    asteroid_image = [load_transparent_images(ASTEROID_IMG_PATH[0]), load_transparent_images(ASTEROID_IMG_PATH[1]),
                      load_transparent_images(ASTEROID_IMG_PATH[2])]
    bullet_image = load_transparent_images(BULLET_IMG_PATH)

    pygame.display.set_caption("Spaceship Game")
    play, screen = menu(screen, "Spaceship Shooter")

    if play:

        space_shooter = SpaceshipShooterGame(screen, player_image, asteroid_image, bullet_image)
        space_shooter.spaceship_game_loop()

    else:
        quit_game()
