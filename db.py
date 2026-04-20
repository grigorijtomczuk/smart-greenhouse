import re
from typing import Any, Dict, Optional

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
        return status
