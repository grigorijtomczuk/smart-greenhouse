import random
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union

from werkzeug.wrappers import Request


class Device(ABC):
    def __init__(self, device_id: int, name: str, status: bool = False):
        self.id = device_id
        self.name = name
        self.status = status

    def turn_on(self):
        self.status = True
        print(f"[LOG] {self.name} (ID: {self.id}) включён")

    def turn_off(self):
        self.status = False
        print(f"[LOG] {self.name} (ID: {self.id}) выключен")

    def get_status(self) -> bool:
        print(f"[LOG] Запрос статуса {self.name} (ID: {self.id}) -> {self.status}")
        return self.status

    @abstractmethod
    def connect(
        self, request: Optional[Request] = None
    ) -> Dict[str, Union[int, float, str, bool]]:
        """Мониторинг (request is None) или применение команд (передан request)."""


class Sensor(Device):
    def __init__(
        self,
        device_id: int,
        name: str,
        sensor_type: str,
        unit: str,
        control_prefix: str,
    ):
        super().__init__(device_id, name)
        self.type = sensor_type
        self.unit = unit
        self.control_prefix = control_prefix
        self.value: float = 0.0

    def measure(self):
        # Генерация случайных значений
        if self.type == "temperature":
            self.value = round(random.uniform(15.0, 35.0), 1)
        elif self.type == "humidity":
            self.value = round(random.uniform(30.0, 80.0), 1)
        elif self.type == "soil_moisture":
            self.value = round(random.uniform(20.0, 60.0), 1)
        else:
            self.value = round(random.uniform(0, 100), 1)
        print(
            f"[LOG] Датчик {self.name} (ID: {self.id}) измерил: {self.value} {self.unit}"
        )
        return self.value

    def calibrate(self, value: float):
        self.value = value
        print(
            f"[LOG] Датчик {self.name} (ID: {self.id}) откалиброван на значение {value} {self.unit}"
        )

    def _apply_control(self, request: Request) -> None:
        p = self.control_prefix
        power_raw = request.args.get(f"{p}_power", "").strip().lower()
        if power_raw:
            # Допустимо on, off, 1, 0, true, false
            if re.match(r"^(on|off|1|0|true|false)$", power_raw):
                if power_raw in ("on", "1", "true"):
                    self.turn_on()
                else:
                    self.turn_off()
            else:
                print(
                    f"[LOG] Ошибка: недопустимое значение power '{power_raw}' для {self.name}. Допустимо: on/off/1/0/true/false"
                )

        raw_cal = request.args.get(f"{p}_calibrate", "").strip()
        if raw_cal:
            try:
                # Заменяем запятую на точку и преобразуем в float
                value = float(raw_cal.replace(",", "."))
                self.calibrate(value)
            except ValueError:
                print(
                    f"[LOG] Ошибка: калибровка {self.name} – некорректное число '{raw_cal}'"
                )

    def connect(
        self, request: Optional[Request] = None
    ) -> Dict[str, Union[int, float, str, bool]]:
        if request is not None:
            self._apply_control(request)
            print(
                f"[LOG] Управляющая команда для датчика {self.name}: значение {self.value} {self.unit}, статус {self.status}"
            )
        else:
            # Без команд выполняем измерение
            self.measure()
            print(
                f"[LOG] Опрос датчика {self.name}: текущее значение {self.value} {self.unit}"
            )
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "unit": self.unit,
            "value": self.value,
            "status": self.status,
        }


class Actuator(Device):
    def __init__(
        self, device_id: int, name: str, actuator_type: str, power: float = 0.0
    ):
        super().__init__(device_id, name)
        self.type = actuator_type
        self.power = power
        self.control_prefix = actuator_type

    def apply_action(self, action: str):
        print(
            f"[LOG] Исполнительное устройство {self.name} (ID: {self.id}) выполняет действие: {action}"
        )

    def set_power(self, level: float):
        self.power = level
        print(
            f"[LOG] Мощность устройства {self.name} (ID: {self.id}) установлена на {level} Вт"
        )

    def _apply_control(self, request: Request) -> None:
        p = self.control_prefix

        power_kw = request.args.get(f"{p}_power_cmd", "").strip()
        if power_kw:
            try:
                self.set_power(float(power_kw.replace(",", ".")))
            except ValueError:
                print(
                    f"[LOG] Ошибка: мощность {self.name} – некорректное число '{power_kw}'"
                )

        action = request.args.get(f"{p}_action", "").strip()
        if action:
            if re.match(r"^[a-zA-Zа-яА-Я0-9_\-]+$", action):
                self.apply_action(action)
            else:
                print(
                    f"[LOG] Ошибка: действие '{action}' для {self.name} содержит недопустимые символы. Разрешены буквы, цифры, '_', '-'"
                )

        st = request.args.get(f"{p}_power_state", "").strip().lower()
        if st:
            if re.match(r"^(on|off|1|0|true|false)$", st):
                if st in ("on", "1", "true"):
                    self.turn_on()
                else:
                    self.turn_off()
            else:
                print(
                    f"[LOG] Ошибка: неверное состояние питания '{st}' для {self.name}"
                )

    def connect(
        self, request: Optional[Request] = None
    ) -> Dict[str, Union[int, float, str, bool]]:
        if request is not None:
            self._apply_control(request)
            print(
                f"[LOG] Управление {self.name}: мощность {self.power} Вт, статус {self.status}"
            )
        else:
            print(
                f"[LOG] Опрос исполнительного устройства {self.name}: {self.power} Вт, статус: {self.status}"
            )
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "power": self.power,
            "status": self.status,
        }


class MainControlUnit:
    def __init__(self, fan_device=None, pump_device=None):
        self.mode = "auto"
        self.schedule: Dict[str, str] = {}
        self.alerts: List[str] = []
        self.fan = fan_device
        self.pump = pump_device

    def process_data(self, sensor_data: Dict[int, float]):
        print(f"[LOG] Контроллер обрабатывает данные с датчиков: {sensor_data}")

    def send_command(self, actuator: Actuator, command: str):
        print(
            f"[LOG] Контроллер отправляет команду '{command}' устройству {actuator.name} (ID: {actuator.id})"
        )
        actuator.apply_action(command)

    def check_alerts(self):
        print("[LOG] Контроллер проверяет наличие тревог...")
        if self.alerts:
            print(f"[LOG] Активные тревоги: {self.alerts}")
        else:
            print("[LOG] Тревог нет")

    def _apply_control(self, request: Request) -> None:
        mode = request.args.get("controller_mode", "").strip().lower()
        if mode:
            if re.match(r"^(auto|manual)$", mode):
                self.mode = mode
                print(f"[LOG] Контроллер: режим установлен в {self.mode}")
            else:
                print(
                    f"[LOG] Ошибка: неверный режим '{mode}'. Допустимо: auto / manual"
                )

        clear = request.args.get("controller_clear_alerts", "").strip().lower()
        if clear:
            if re.match(r"^(1|true|yes|on)$", clear):
                self.alerts = []
                print("[LOG] Контроллер: список тревог очищен")
            else:
                print(
                    f"[LOG] Ошибка: неверное значение clear_alerts '{clear}'. Игнорируем."
                )

    def connect(
        self, request: Optional[Request] = None
    ) -> Dict[str, Union[str, int, List[str]]]:
        if request is not None:
            self._apply_control(request)
        print(
            f"[LOG] Подключение к контроллеру выполнено, режим: {self.mode}, количество тревог: {len(self.alerts)}"
        )
        return {
            "mode": self.mode,
            "alerts_count": len(self.alerts),
            "alerts": list(self.alerts),
        }

    def auto_control(self, temperature: float, soil_moisture: float):
        """Автоматическое управление на основе показаний датчиков"""
        if self.mode != "auto":
            print("[LOG] Автоматика отключена (ручной режим)")
            return

        # Управление вентилятором по температуре
        if self.fan:
            if temperature > 28.0 and not self.fan.status:
                self.fan.turn_on()
                self.alerts.append(f"Авто: вентилятор включён при {temperature}°C")
                print(
                    f"[LOG] Автоматика: включён вентилятор (температура {temperature}°C)"
                )
            elif temperature <= 28.0 and self.fan.status:
                self.fan.turn_off()
                self.alerts.append(f"Авто: вентилятор выключен при {temperature}°C")
                print(
                    f"[LOG] Автоматика: выключен вентилятор (температура {temperature}°C)"
                )

        # Управление насосом по влажности почвы
        if self.pump:
            if soil_moisture < 30.0 and not self.pump.status:
                self.pump.turn_on()
                self.alerts.append(
                    f"Авто: насос включён (влажность почвы {soil_moisture}%)"
                )
                print(
                    f"[LOG] Автоматика: включён насос (влажность почвы {soil_moisture}%)"
                )
            elif soil_moisture >= 30.0 and self.pump.status:
                self.pump.turn_off()
                self.alerts.append(
                    f"Авто: насос выключен (влажность почвы {soil_moisture}%)"
                )
                print(
                    f"[LOG] Автоматика: выключен насос (влажность почвы {soil_moisture}%)"
                )


class Database:
    def __init__(self, connection_string: str, storage_path: str):
        self.connection_string = connection_string
        self.storage_path = storage_path
        self.records_today: int = 0

    def save_reading(self, sensor_id: int, value: float, timestamp: datetime):
        self.records_today += 1
        print(
            f"[LOG] БД: сохранено показание датчика {sensor_id} = {value} в {timestamp}"
        )

    def save_event(self, device_id: int, action: str, timestamp: datetime):
        self.records_today += 1
        print(
            f"[LOG] БД: сохранено событие устройства {device_id}: {action} в {timestamp}"
        )

    def get_history(
        self, start: datetime, end: datetime, device_id: Optional[int] = None
    ):
        print(
            f"[LOG] БД: запрос истории с {start} по {end} для устройства {device_id if device_id else 'всех'}"
        )

        return []

    def _apply_control(self, request: Request) -> None:
        cmd = request.args.get("database_command", "").strip()
        if cmd:
            if re.match(r"^[a-zA-Z0-9_\-]+$", cmd):
                print(f"[LOG] БД: принята управляющая команда '{cmd}'")
            else:
                print(
                    f"[LOG] Ошибка: команда БД '{cmd}' содержит недопустимые символы. Разрешены буквы, цифры, '_', '-'"
                )

    def connect(self, request: Optional[Request] = None) -> Dict[str, Union[str, int]]:
        if request is not None:
            self._apply_control(request)
        data = {
            "connection": "ok",
            "storage_path": self.storage_path,
            "records_today": self.records_today,
        }
        print(
            f"[LOG] Подключение к БД выполнено, записей за сегодня: {data['records_today']}, путь: {data['storage_path']}"
        )
        return data
