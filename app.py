from flask import Flask
from datetime import datetime
from devices import Sensor, Actuator, MainControlUnit, Database

app = Flask(__name__)

@app.route('/')
def index():
    # Датчик температуры
    temp_sensor = Sensor(1, "Датчик температуры", "temperature", "C")
    temp_sensor.turn_on()
    temp_sensor.measure()
    temp_sensor.calibrate(23.0)
    status = temp_sensor.get_status()
    temp_sensor.turn_off()

    # Исполнительное устройство (вентилятор)
    fan = Actuator(101, "Вентилятор", "fan", 150)
    fan.turn_on()
    fan.apply_action("увеличить обороты")
    fan.set_power(200)
    fan.turn_off()

    # Контроллер
    controller = MainControlUnit()
    controller.process_data({1: 23.0, 2: 65.0})
    controller.check_alerts()
    controller.send_command(fan, "включить на полную мощность")

    # База данных
    db = Database("sqlite:///greenhouse.db", "./data")
    now = datetime.now()
    db.save_reading(1, 23.0, now)
    db.save_event(101, "вентилятор включён", now)
    history = db.get_history(now, now)

    return "Проверьте терминал. В нём отражены логи сервера."


@app.route('/sensor')
def sensor_example():
    humidity = Sensor(2, "Датчик влажности", "humidity", "%")
    humidity.turn_on()
    humidity.measure()
    humidity.calibrate(65.0)
    humidity.turn_off()
    return "Датчик влажности сработал. Смотрите лог."


if __name__ == '__main__':
    app.run(debug=True)