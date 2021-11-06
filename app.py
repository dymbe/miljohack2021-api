import os

from flask import Flask, request
import requests
import json
from dbutils import query
from datetime import datetime
from collections import Counter
import pandas as pd
from multiprocessing import Process
import time


app = Flask(__name__)
server_key = "AAAAUKuWS4o:APA91bEqw_9luyNSvNpEpDQOqhYFt1NV6-R4MweUKuyxDCHnFqjn4u1t8Fxx5-rDpHhBakhn7adRoJ3mArnkw7zexbEVzHVOy3wDtybd56TkFOif9EdyuB4qNhxe1hTM_o2iDNRr05VF"


@app.route("/")
def hello_world():
    return f"<p>Hello, World!</p>"


@app.route("/packages")
def packages():
    results = query("select rowid, user_id, shop_name, delivery_time, climate_optimized from package where user_id = 1")
    response = []
    for package_id, user_id, shop_name, delivery_time, climate_optimized in results:
        dt = datetime.strptime(delivery_time, "%Y-%m-%d %H:%M:%S")
        time_str = dt.strftime("%H:%M")
        date_str = dt.strftime("%d/%m")
        response.append({
            "package_id": package_id,
            "user_id": user_id,
            "shop_name": shop_name,
            "delivery_time": time_str,
            "delivery_date": date_str,
            "delivery_timestamp": delivery_time,
            "climate_optimized": climate_optimized
        })

    return json.dumps(response, ensure_ascii=False)


def run_ml():
    time.sleep(6)
    rows = query(
        "select rowid, user_id, shop_name, delivery_time, terminal_time, ordered_time, climate_optimized from package"
    )

    df = pd.DataFrame([
        {
            "package_id": rowid,
            "user_id": user_id,
            "shop_name": shop_name,
            "delivery_time": delivery_time,
            "terminal_time": terminal_time,
            "ordered_time": ordered_time,
            "climate_optimized": climate_optimized
        }
        for rowid, user_id, shop_name, delivery_time, terminal_time, ordered_time, climate_optimized in rows
    ])
    df["climate_optimized"] = (df["climate_optimized"] == 1) | (df["climate_optimized"] == "True")
    df["delivery_time"] = pd.to_datetime(df["delivery_time"])
    print(df[["delivery_time", "user_id", "climate_optimized"]])

    latest_timestamp = df[df["user_id"] == 1]["delivery_time"].max()
    package_ids = df[(df["climate_optimized"] == True) & (df["user_id"] == 1)]["package_id"]
    for packid in package_ids:
        query("update package set delivery_time = ? where rowid = ?", (str(latest_timestamp), packid))

    notify()


def set_package_optimization(package_id, optimize):
    query("update package set climate_optimized = ? where rowid = ?", (optimize, package_id))

    p = Process(target=run_ml)
    p.start()

    result = query(
        "select rowid, shop_name, delivery_time, climate_optimized from package where rowid = ?",
        (package_id,)
    )[0]

    package_id, shop_name, delivery_time, climate_optimized = result
    dt = datetime.strptime(delivery_time, "%Y-%m-%d %H:%M:%S")
    time_str = dt.strftime("%H:%M")
    date_str = dt.strftime("%d/%m")
    response = {
        "package_id": package_id,
        "shop_name": shop_name,
        "delivery_time": time_str,
        "delivery_date": date_str,
        "delivery_timestamp": delivery_time,
        "climate_optimized": climate_optimized
    }
    return json.dumps(response, ensure_ascii=False)


@app.route("/optimize-package")
def optimize_package():
    package_id = request.args.get("package_id")
    return set_package_optimization(package_id, True)


@app.route("/unoptimize-package")
def unoptimize_package():
    package_id = request.args.get("package_id")
    return set_package_optimization(package_id, False)


@app.route("/register-device")
def register_device():
    device_token = request.args.get("device_token")
    query("insert into device_token (value) values (?) on conflict do nothing", (device_token,))
    return device_token


@app.route("/notify")
def notify():
    tokens = [row[0] for row in query(f"select * from device_token")]

    for token in tokens:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "key=" + server_key,
        }

        body = {
            "notification": {
                "title": "Pakken din har blitt klimaoptimal",
                "body": "Vi har regnet ut en leveringstid som minimerer ditt klimaavtrykk"
            },
            "to": token,
            "priority": "high",
        }

        requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))

    return "Tried to send notification"


@app.route("/leaderboard")
def leaderboard():
    optimize_counter = Counter()
    total_counter = Counter()

    rows = query("select climate_optimized, zip_code from package")

    for climate_optimized, zip_code in rows:
        print(climate_optimized, climate_optimized == "True", zip_code)
        optimize_counter[zip_code] += int(climate_optimized == "True")
        total_counter[zip_code] += 1

    results = sorted([
        {"zip_code": zip_code, "score": optimize_counter[zip_code] / total_counter[zip_code]}
        for zip_code in total_counter
    ], key=lambda x: x["score"], reverse=True)

    return json.dumps(results)


if __name__ == "__main__":
    app.debug = True
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host=host, port=port)
