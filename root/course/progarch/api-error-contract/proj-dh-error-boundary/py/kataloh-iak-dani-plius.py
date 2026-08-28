from dataclasses import dataclass

# доменні помилки — ті самі, що впираються в межу HTTP знизу
class DomainError(Exception): ...
class DeviceNotFound(DomainError):
    def __init__(self, id): self.id = id
class DeviceUnavailable(DomainError):
    def __init__(self, id): self.id = id
class InvalidCommand(DomainError):
    def __init__(self, field, reason): self.field, self.reason = field, reason
class RateLimited(DomainError):
    def __init__(self, retry_after_s): self.retry_after_s = retry_after_s

@dataclass(frozen=True)
class Row:                      # контракт ОДНОГО класу, як дані
    status: int
    code: str                   # стабільний машинний ярлик — НЕ міняється ніколи
    title: str
    retryable: bool = False
    retry_after_s: int | None = None

# КЛЮЧ — сам клас (тип), а не рядок-назва
CATALOG: dict[type, Row] = {
    DeviceNotFound:    Row(404, "device_not_found",   "Пристрій не знайдено"),
    DeviceUnavailable: Row(503, "device_unavailable", "Пристрій тимчасово недоступний", retryable=True, retry_after_s=5),
    InvalidCommand:    Row(400, "invalid_command",    "Некоректна команда"),
    RateLimited:       Row(429, "rate_limited",       "Забагато запитів", retryable=True),
}
