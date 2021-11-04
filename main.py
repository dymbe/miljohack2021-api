from flask import Flask, request, make_response
import requests
import json
import sqlite3
import time

app = Flask(__name__)
server_key = "AAAAUKuWS4o:APA91bEqw_9luyNSvNpEpDQOqhYFt1NV6-R4MweUKuyxDCHnFqjn4u1t8Fxx5-rDpHhBakhn7adRoJ3mArnkw7zexbEVzHVOy3wDtybd56TkFOif9EdyuB4qNhxe1hTM_o2iDNRr05VF"


@app.route("/")
def hello_world():
    device_token = request.args.get("device_token")
    return f"<p>Hello, World! device_key={device_token}</p>"


@app.route("/notification")
def notify():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    device_token = request.args.get("device_token")

    cur.execute("insert into device_token (value) values (?)", (device_token,))

    tokens = [row[0] for row in cur.execute(f"select * from device_token")]
    print(tokens)
    con.commit()
    con.close()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + server_key,
    }

    body = {
        'notification': {
            'title': 'Sending push form python script',
            'body': 'New Message'
        },
        'to': tokens,
        'priority': 'high',
        #   'data': dataPayLoad,
    }

    print(body)

    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))

    if response.status_code == 200:
        return response.json()
    else:
        return str(response.status_code), response.status_code
