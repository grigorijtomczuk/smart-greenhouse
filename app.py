import logging

from flask import Flask, jsonify, render_template, request

from devices import Actuator, Database, MainControlUnit, Sensor

app = Flask(__name__)

temperature_sensor = Sensor(1, "Датчик температуры", "temperature", "°C", "temperature")
humidity_sensor = Sensor(2, "Датчик влажности воздуха", "humidity", "%", "humidity")
soil_sensor = Sensor(3, "Датчик влажности почвы", "soil_moisture", "%", "soil")
fan = Actuator(101, "Вентилятор", "fan", 120.0)
pump = Actuator(102, "Насос полива", "pump", 80.0)
controller = MainControlUnit()
database = Database("sqlite:///greenhouse.db", "./data")

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
    return jsonify(temperature_sensor.connect())


@app.route("/connect/humidity")
def connect_humidity():
    return jsonify(humidity_sensor.connect())


@app.route("/connect/soil")
def connect_soil():
    return jsonify(soil_sensor.connect())


@app.route("/connect/fan")
def connect_fan():
    return jsonify(fan.connect())


@app.route("/connect/pump")
def connect_pump():
    return jsonify(pump.connect())


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

if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(debug=True)
