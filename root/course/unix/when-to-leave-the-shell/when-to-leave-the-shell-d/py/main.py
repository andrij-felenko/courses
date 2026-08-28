import json
from dataclasses import dataclass

@dataclass
class ServerConfig:
    host: str
    port: int
    enabled: bool

# Надійний парсинг із суворою перевіркою типів
data = json.loads(payload_str)
config = ServerConfig(host=data["host"], port=int(data["port"]), enabled=bool(data["enabled"]))
