from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from db import Database


class Logger:
    def __init__(self, database: Database):
        self._database = database
        self._db = database.db

        # кеш последнего записанного значения, чтобы не плодить дубликаты
        self._last: Dict[Tuple[str, str], Any] = {}

    def _should_insert(self, category: str, key: str, new_value: Any) -> bool:
        cache_key = (category, key)
        if self._last.get(cache_key) == new_value:
            return False
        self._last[cache_key] = new_value
        return True

    def get_status(self) -> Dict[str, Any]:
        status = self._database.get_status()
        status["dedupe_cache_size"] = len(self._last)
        return status

    def insert_sensor_reading(
        self,
        *,
        sensor_id: int,
        sensor_name: str,
        sensor_type: str,
        value: float,
        unit: str,
        status: bool,
        timestamp: Optional[datetime] = None,
    ):
        """
        Записать показание датчика (без дублей по значению).
        Коллекция: SensorReadings
        """
        key = f"{sensor_id}:{sensor_type}"
        if not self._should_insert("sensor", key, value):
            return None

        doc = {
            "timestamp": (timestamp or datetime.now()),
            "sensor": {
                "id": sensor_id,
                "name": sensor_name,
                "type": sensor_type,
                "unit": unit,
                "status": status,
            },
            "value": value,
        }

        try:
            return self._db["SensorReadings"].insert_one(doc)
        except Exception as exc:  # pragma: no cover
            print(f"[LOGGER] Ошибка записи SensorReadings: {exc}")
            return None

    def insert_device_event(
        self,
        *,
        device_id: int,
        device_name: str,
        device_type: str,
        status: bool,
        power: Optional[float] = None,
        event: str = "state",
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ):
        """
        Записать событие/состояние исполнительного устройства (без дублей по состоянию).
        Коллекция: DeviceEvents
        """
        dedupe_value = {
            "status": status,
            "power": power,
            "event": event,
            "details": details,
        }
        key = f"{device_id}:{device_type}"
        if not self._should_insert("device", key, dedupe_value):
            return None

        doc = {
            "timestamp": (timestamp or datetime.now()),
            "device": {
                "id": device_id,
                "name": device_name,
                "type": device_type,
            },
            "event": event,
            "status": status,
            "power": power,
            "details": details or {},
        }

        try:
            return self._db["DeviceEvents"].insert_one(doc)
        except Exception as exc:  # pragma: no cover
            print(f"[LOGGER] Ошибка записи DeviceEvents: {exc}")
            return None
