from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union

class Device(ABC):
    def __init__(self, device_id: int, name: str, status: bool = False):
        self.id = device_id
        self.name = name
        self.status = status

    def turn_on(self):
        self.status = True
        print(f"[LOG] {self.__class__.__name__} {self.name} (ID: {self.id}) включён")

    def turn_off(self):
        self.status = False
        print(f"[LOG] {self.__class__.__name__} {self.name} (ID: {self.id}) выключен")

    def get_status(self) -> bool:
        print(f"[LOG] Запрос статуса {self.__class__.__name__} {self.name} (ID: {self.id}) -> {self.status}")
        return self.status


class Sensor(Device):
    def __init__(self, device_id: int, name: str, sensor_type: str, unit: str):
        super().__init__(device_id, name)
        self.type = sensor_type
        self.unit = unit
        self.value: float = 0.0

    def measure(self):
        self.value = 22.5
        print(f"[LOG] Датчик {self.name} (ID: {self.id}) измерил: {self.value} {self.unit}")

    def calibrate(self, value: float):
        self.value = value
        print(f"[LOG] Датчик {self.name} (ID: {self.id}) откалиброван на значение {value} {self.unit}")

class Actuator(Device):
    def __init__(self, device_id: int, name: str, actuator_type: str, power: float = 0.0):
        super().__init__(device_id, name)
        self.type = actuator_type
        self.power = power

    def apply_action(self, action: str):
        print(f"[LOG] Исполнительное устройство {self.name} (ID: {self.id}) выполняет действие: {action}")

    def set_power(self, level: float):
        self.power = level
        print(f"[LOG] Мощность устройства {self.name} (ID: {self.id}) установлена на {level} Вт")


class MainControlUnit:
    def __init__(self):
        self.mode = "auto"
        self.schedule: Dict[str, str] = {}
        self.alerts: List[str] = []

    def process_data(self, sensor_data: Dict[int, float]):
        print(f"[LOG] Контроллер обрабатывает данные с датчиков: {sensor_data}")

    def send_command(self, actuator: Actuator, command: str):
        print(f"[LOG] Контроллер отправляет команду '{command}' устройству {actuator.name} (ID: {actuator.id})")
        actuator.apply_action(command)

    def check_alerts(self):
        print("[LOG] Контроллер проверяет наличие тревог...")
        if self.alerts:
            print(f"[LOG] Активные тревоги: {self.alerts}")
        else:
            print("[LOG] Тревог нет")


class Database:
    def __init__(self, connection_string: str, storage_path: str):
        self.connection_string = connection_string
        self.storage_path = storage_path

    def save_reading(self, sensor_id: int, value: float, timestamp: datetime):
        print(f"[LOG] БД: сохранено показание датчика {sensor_id} = {value} в {timestamp}")

    def save_event(self, device_id: int, action: str, timestamp: datetime):
        print(f"[LOG] БД: сохранено событие устройства {device_id}: {action} в {timestamp}")

    def get_history(self, start: datetime, end: datetime, device_id: Optional[int] = None):
        print(f"[LOG] БД: запрос истории с {start} по {end} для устройства {device_id if device_id else 'всех'}")

        return []
