import re
from statistics import mean
from typing import Any, Dict, List, Optional

import pymongo
from werkzeug.wrappers import Request


class Database:
    def __init__(
        self,
        *,
        mongo_uri: str = "mongodb://localhost:27017/",
        db_name: str = "greenhouse_db",
    ):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self._client = pymongo.MongoClient(self.mongo_uri)
        self._db = self._client[self.db_name]

    @property
    def db(self):
        return self._db

    def get_status(self) -> Dict[str, Any]:
        try:
            self._client.admin.command("ping")
            collections = list(self._db.list_collection_names())
            counts: Dict[str, int] = {}
            total = 0
            for name in collections:
                c = int(self._db[name].estimated_document_count())
                counts[name] = c
                total += c
            return {
                "connection": "ok",
                "db_name": self.db_name,
                "uri": self.mongo_uri,
                "collections": counts,
                "records_total": total,
            }
        except Exception as exc:
            return {
                "connection": "error",
                "db_name": self.db_name,
                "uri": self.mongo_uri,
                "error": str(exc),
                "collections": {},
                "records_total": 0,
            }

    def get_sensor_value_stats(
        self,
        *,
        sensor_type: str,
        limit: int = 5000,
    ) -> Dict[str, Any]:
        try:
            cursor = (
                self._db["SensorReadings"]
                .find({"sensor.type": sensor_type}, {"value": 1})
                .sort("timestamp", pymongo.DESCENDING)
                .limit(int(limit))
            )

            values: List[float] = []
            for doc in cursor:
                v = doc.get("value")
                if v is None:
                    continue
                try:
                    values.append(float(v))
                except (TypeError, ValueError):
                    continue

            if not values:
                return {
                    "sensor_type": sensor_type,
                    "count": 0,
                    "avg": None,
                    "max": None,
                }

            return {
                "sensor_type": sensor_type,
                "count": len(values),
                "avg": float(mean(values)),
                "max": float(max(values)),
            }
        except Exception as exc:
            return {
                "sensor_type": sensor_type,
                "count": 0,
                "avg": None,
                "max": None,
                "error": str(exc),
            }

    def _apply_control(self, request: Request) -> None:
        cmd = request.args.get("database_command", "").strip()
        if not cmd:
            return
        if re.match(r"^[a-zA-Z0-9_\-]+$", cmd):
            print(f"[LOG] MongoDB: принята управляющая команда '{cmd}'")
        else:
            print(
                f"[LOG] Ошибка: команда БД '{cmd}' содержит недопустимые символы. Разрешены буквы, цифры, '_', '-'"
            )

    def connect(self, request: Optional[Request] = None) -> Dict[str, Any]:
        if request is not None:
            self._apply_control(request)
        status = self.get_status()
        if status.get("connection") == "ok":
            print(
                f"[LOG] MongoDB OK: db={status.get('db_name')}, всего записей={status.get('records_total')}"
            )
        else:
            print(f"[LOG] MongoDB ERROR: {status.get('error')}")

        # Аналитика данных
        if status.get("connection") == "ok":
            status["analytics"] = {
                "temperature": self.get_sensor_value_stats(sensor_type="temperature"),
                "humidity": self.get_sensor_value_stats(sensor_type="humidity"),
                "soil_moisture": self.get_sensor_value_stats(
                    sensor_type="soil_moisture"
                ),
            }
        else:
            status["analytics"] = {}

        return status
