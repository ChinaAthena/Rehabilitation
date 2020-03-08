from Spaceship_Shooter import SpaceshipShooterGame
from main_function import initialize_game_window, menu, load_transparent_images, quit_game
import constant as cons
import pygame
from twilio.rest import Client
import pyodbc
from datetime import date

if __name__ == '__main__':
    # Your Account SID from twilio.com/console
    account_sid = "*"
    # Your Auth Token from twilio.com/console
    auth_token = "*"

    pygame.init()

    screen = initialize_game_window(700, 600)

    background = pygame.image.load(cons.BACKGROUND_IMG_PATH).convert()

    player_image = load_transparent_images(cons.SPACESHIP_IMG_PATH)

    asteroid_image = [load_transparent_images(cons.ASTEROID_IMG_PATH[0]),
                      load_transparent_images(cons.ASTEROID_IMG_PATH[1])]

    bullet_image = load_transparent_images(cons.BULLET_IMG_PATH)

    pygame.display.set_caption("Spaceship Game")

    play, screen = menu(screen, "Spaceship Shooter")

    if play:
        space_shooter = SpaceshipShooterGame(screen, background, player_image, asteroid_image, bullet_image)
        data = space_shooter.spaceship_game_loop()
        turns = data[0]
        seconds = data[1]
        score = data[2]
        ScorevsTime = score / seconds
        client = Client(account_sid, auth_token)

        server = 'mysqlrehabilitationr.database.windows.net'
        database = 'Patients'
        username = 'azureuser'
        password = '*'
        driver = '{ODBC Driver 17 for SQL Server}'
        cnxn = pyodbc.connect(
            'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()

        cursor.execute("SELECT * FROM dbo.Patientinfos;")
        row = cursor.fetchone()
        avg_score = 0
        avg_time = 0
        avg_turn = 0
        avg_score_vs_time = 0
        it = 0
        while row:
            print(str(row[0]) + " " + str(row[1]))
            avg_score += int(row[2])
            avg_time += int(row[3])
            avg_turn += int(row[4])
            avg_score_vs_time += float(row[5])
            it += 1
            row = cursor.fetchone()

        avg_score /= it
        avg_time /= it
        avg_turn /= it
        avg_score_vs_time /= it
        perform_improved = round(((seconds/turns - avg_time/avg_turn) / (seconds/turns)) * 100)

        message = client.messages.create(
            to="+12137132689",
            from_="+12132779054",
            body="Hello! This is today's exercise report from your patient.\n\nHistory Record \nAverage score: " + str(
                avg_score) + "\nAverage time elapsed: " + str(avg_time) + " \nAverage turns finished: " + str(
                avg_turn) +
                 "\n\nYour patient got " + str(score) + " scores today. The number of turns he/she finished is " + str(turns) +
                 ". The total time spent for today's exercise is " + str(
                seconds) + " seconds. \n\nThe overall improvement of today's performance is " + str(
                perform_improved) + "%. Good job!")

        today = str(date.today())
        command = "INSERT INTO dbo.Patientinfos ([TrialId], [Date], [Score], [TimeElapsed], [NumOfTurn], [ScorevsTime]) VALUES ( " + str(it + 1) + ", N'" + today + "', N'" + str(score) + "', N'" + str(seconds) + "', N'" + str(turns) + "', N'" + str(round(ScorevsTime), 2) + "');"
        cursor.execute(command)
        cnxn.commit()
    else:
        quit_game()

