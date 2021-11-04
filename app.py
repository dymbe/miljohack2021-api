from flask import Flask, request, make_response
import requests
import json
from dbutils import query
from datetime import datetime
from os import environ

app = Flask(__name__)
server_key = "AAAAUKuWS4o:APA91bEqw_9luyNSvNpEpDQOqhYFt1NV6-R4MweUKuyxDCHnFqjn4u1t8Fxx5-rDpHhBakhn7adRoJ3mArnkw7zexbEVzHVOy3wDtybd56TkFOif9EdyuB4qNhxe1hTM_o2iDNRr05VF"


@app.route("/")
def hello_world():
    return f"<p>Hello, World!</p>"


def package_message(status):
    if status == "sent":
        return f"Pakken er på vei"
    elif status == "ordered":
        return f"Frakt er bestilt"


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
            "message": package_message(status)
        })

    return json.dumps(response, ensure_ascii=False)


@app.route("/register-device")
def register_device():
    device_token = request.args.get("device_token")
    query("insert into device_token (value) values (?) on conflict do nothing", (device_token,))
    return device_token


@app.route("/notify")
def notify():
    tokens = [row[0] for row in query(f"select * from device_token")]
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


if __name__ == '__main__':
    app.debug = True
    host = environ["FLASK_HOST"]
    port = int(environ["FLASK_PORT"])
    app.run(host=host, port=port)
