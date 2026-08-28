from typing import Protocol

class Connection(Protocol):
    def query(self, sql: str) -> list: ...
    def close(self) -> None: ...

class ConnectionFactory(Protocol):        # порт-творець
    def open(self) -> Connection: ...

class ReportService:
    def __init__(self, factory: ConnectionFactory):
        self._factory = factory

    def daily(self) -> "Report":
        conn = self._factory.open()       # створили, не назвавши деталь
        try:
            return build(conn.query("select ..."))
        finally:
            conn.close()
