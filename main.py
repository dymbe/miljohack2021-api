from flask import Flask, request
import requests
import json

app = Flask(__name__)

server_key = "AAAAUKuWS4o:APA91bEqw_9luyNSvNpEpDQOqhYFt1NV6-R4MweUKuyxDCHnFqjn4u1t8Fxx5-rDpHhBakhn7adRoJ3mArnkw7zexbEVzHVOy3wDtybd56TkFOif9EdyuB4qNhxe1hTM_o2iDNRr05VF"


@app.route("/")
def hello_world():
    device_token = request.args.get("device_token")
    return f"<p>Hello, World! device_key={device_token}</p>"


@app.route("/notification")
def notify():
    device_token = request.args.get("device_token")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + server_key,
    }

    body = {
        'notification': {
            'title': 'Sending push form python script',
            'body': 'New Message'
        },
        'to': device_token,
        'priority': 'high',
        #   'data': dataPayLoad,
    }

    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
    print(response.status_code)

    return response.json()
