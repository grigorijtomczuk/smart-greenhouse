import logging

from flask import Flask, jsonify, render_template, request

from db import Database
from devices import Actuator, MainControlUnit, Sensor
from logger import Logger
import pymongo
from datetime import datetime

app = Flask(__name__)

temperature_sensor = Sensor(1, "Датчик температуры", "temperature", "°C", "temperature")
humidity_sensor = Sensor(2, "Датчик влажности воздуха", "humidity", "%", "humidity")
soil_sensor = Sensor(3, "Датчик влажности почвы", "soil_moisture", "%", "soil")
fan = Actuator(101, "Вентилятор", "fan", 120.0)
pump = Actuator(102, "Насос полива", "pump", 80.0)
controller = MainControlUnit(fan_device=fan, pump_device=pump)

database = Database(mongo_uri="mongodb://localhost:27017", db_name="greenhouse_logs")
db_logger = Logger(database)

last_temperature = 0.0
last_soil = 0.0

temperature_sensor.turn_on()
humidity_sensor.turn_on()
soil_sensor.turn_on()
fan.turn_on()
pump.turn_on()


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/connect/temperature")
def connect_temperature():
    global last_temperature
    data = temperature_sensor.connect()
    last_temperature = data["value"]
    controller.auto_control(float(last_temperature), float(last_soil))
    db_logger.insert_sensor_reading(
        sensor_id=int(data["id"]),
        sensor_name=str(data["name"]),
        sensor_type=str(data["type"]),
        value=float(data["value"]),
        unit=str(data["unit"]),
        status=bool(data["status"]),
    )
    db_logger.insert_device_event(
        device_id=fan.id,
        device_name=fan.name,
        device_type=fan.type,
        status=bool(fan.status),
        power=float(fan.power),
        event="auto_control",
        details={"reason": "temperature update"},
    )
    db_logger.insert_device_event(
        device_id=pump.id,
        device_name=pump.name,
        device_type=pump.type,
        status=bool(pump.status),
        power=float(pump.power),
        event="auto_control",
        details={"reason": "temperature update"},
    )
    return jsonify(data)


@app.route("/connect/soil")
def connect_soil():
    global last_soil
    data = soil_sensor.connect()
    last_soil = data["value"]
    controller.auto_control(float(last_temperature), float(last_soil))
    db_logger.insert_sensor_reading(
        sensor_id=int(data["id"]),
        sensor_name=str(data["name"]),
        sensor_type=str(data["type"]),
        value=float(data["value"]),
        unit=str(data["unit"]),
        status=bool(data["status"]),
    )
    db_logger.insert_device_event(
        device_id=fan.id,
        device_name=fan.name,
        device_type=fan.type,
        status=bool(fan.status),
        power=float(fan.power),
        event="auto_control",
        details={"reason": "soil update"},
    )
    db_logger.insert_device_event(
        device_id=pump.id,
        device_name=pump.name,
        device_type=pump.type,
        status=bool(pump.status),
        power=float(pump.power),
        event="auto_control",
        details={"reason": "soil update"},
    )
    return jsonify(data)


@app.route("/connect/humidity")
def connect_humidity():
    data = humidity_sensor.connect()
    db_logger.insert_sensor_reading(
        sensor_id=int(data["id"]),
        sensor_name=str(data["name"]),
        sensor_type=str(data["type"]),
        value=float(data["value"]),
        unit=str(data["unit"]),
        status=bool(data["status"]),
    )
    return jsonify(data)


@app.route("/connect/fan")
def connect_fan():
    data = fan.connect()
    db_logger.insert_device_event(
        device_id=int(data["id"]),
        device_name=str(data["name"]),
        device_type=str(data["type"]),
        status=bool(data["status"]),
        power=float(data["power"]),
        event="manual_poll",
    )
    return jsonify(data)


@app.route("/connect/pump")
def connect_pump():
    data = pump.connect()
    db_logger.insert_device_event(
        device_id=int(data["id"]),
        device_name=str(data["name"]),
        device_type=str(data["type"]),
        status=bool(data["status"]),
        power=float(data["power"]),
        event="manual_poll",
    )
    return jsonify(data)


@app.route("/connect/controller")
def connect_controller():
    return jsonify(controller.connect())


@app.route("/connect/database")
def connect_database():
    return jsonify(database.connect())


@app.route("/connect/command", methods=["GET"])
def connect_command():
    """Применить управляющие параметры ко всем вещам."""
    return jsonify(
        {
            "temperature": temperature_sensor.connect(request),
            "humidity": humidity_sensor.connect(request),
            "soil": soil_sensor.connect(request),
            "fan": fan.connect(request),
            "pump": pump.connect(request),
            "controller": controller.connect(request),
            "database": database.connect(request),
        }
    )


@app.route("/api/temperature_history")
def temperature_history():
    """Возвращает историю температуры для построения графика."""
    limit = request.args.get("limit", default=30, type=int)

    collection = database.db["SensorReadings"]

    cursor = collection.find(
        {"sensor.type": "temperature"},
        {"timestamp": 1, "value": 1, "_id": 0}
    ).sort("timestamp", pymongo.DESCENDING).limit(limit)

    records = list(cursor)[::-1]

    timestamps = []
    values = []
    for rec in records:
        ts = rec["timestamp"]
        if isinstance(ts, datetime):
            timestamps.append(ts.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            timestamps.append(str(ts))
        values.append(rec["value"])

    return jsonify({
        "timestamps": timestamps,
        "values": values
    })



if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(debug=True)
