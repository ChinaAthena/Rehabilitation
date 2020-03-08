import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

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
            f = open("difficulty.txt", "w")
            f.write(s)
            f.close()
            resp.message("Difficulty Updated! Now is " + s)
        else:
            resp.message("Wrong input!")
    elif 'statistics' in body:
        resp.message("....")
    else:
        resp.message("Hi doctor Lee, what do you wanna do today? \n 1) update difficulty 1 - 10 (e.g. update 4)\n 2) check patient's statistics (e.g. check)")

    return str(resp)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="127.0.0.1", port=8080)
