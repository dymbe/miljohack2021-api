from flask import Flask, request, make_response
import requests
import json
import sqlite3
import time
from dbutils import query
from datetime import datetime

app = Flask(__name__)
server_key = "AAAAUKuWS4o:APA91bEqw_9luyNSvNpEpDQOqhYFt1NV6-R4MweUKuyxDCHnFqjn4u1t8Fxx5-rDpHhBakhn7adRoJ3mArnkw7zexbEVzHVOy3wDtybd56TkFOif9EdyuB4qNhxe1hTM_o2iDNRr05VF"


@app.route("/")
def hello_world():
    return f"<p>Hello, World!</p>"


def package_message(status, date_str):
    if status == "sent":
        return f"Pakken er på vei - {date_str}"
    elif status == "ordered":
        return f"Frakt er bestilt - {date_str}"


@app.route("/packages")
def packages():
    results = query("select shop_name, delivery_time, status from package")

    response = []
    for shop_name, delivery_time, status in results:
        dt = datetime.strptime(delivery_time, "%Y-%m-%d %H:%M:%S.%f")
        time_str = dt.strftime("%H:%M")
        date_str = dt.strftime("%d/%m")
        response.append({
            "shop_name": shop_name,
            "delivery_time": time_str,
            "delivery_date": date_str,
            "message": package_message(status, date_str)
        })

    return json.dumps(response)


@app.route("/notify")
def notify():
    time.sleep(3)
    device_token = request.args.get("device_token")

    query("insert into device_token (value) values (?) on conflict do nothing", (device_token,))

    tokens = [row[0] for row in cur.execute(f"select * from device_token")]
    print(tokens)

    for token in tokens:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + server_key,
        }

        body = {
            'notification': {
                'title': 'Sending push form python script',
                'body': 'New Message'
            },
            'to': token,
            'priority': 'high',
        }

        requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))

    return "Tried to send notification"
