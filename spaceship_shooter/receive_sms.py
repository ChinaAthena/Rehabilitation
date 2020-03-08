import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import pyodbc
from datetime import date

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello!</h1>'

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    body = request.values.get('Body', None)
    # Start our TwiML response
    resp = MessagingResponse()
    # Add a message
    if 'update' in body and len(body.split()) == 2:
        s = body.split()[1]
        if s.isdigit():
            f = open("difficulty.txt", "w+")
            f.write(s)
            f.close()
            resp.message("Difficulty Updated! Now is " + s)
        else:
            resp.message("Wrong input!")
    elif 'check' in body:
        server = 'mysqlrehabilitationr.database.windows.net'
        database = 'Patients'
        username = 'azureuser'
        password = 'Azure12345'
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

        body = "History Record \nAverage score: " + str(round(avg_score, 2)) + "\nAverage time elapsed: " + str(round(avg_time, 2)) + " \nAverage turns finished: " + str(round(avg_turn, 2))
        resp.message(body)

    else:
        resp.message("Hi doctor Lee, what do you wanna do today? \n 1) update difficulty 1 - 10 (e.g. update 4)\n 2) check patient's statistics (e.g. check)")

    return str(resp)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="127.0.0.1", port=8080)
