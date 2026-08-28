from dataclasses import dataclass
from typing import Protocol, List

# 1. Незмінна структура події телеметрії
@dataclass(frozen=True)
class TelemetryEvent:
    device_id: int
    timestamp_ms: int
    temperature_c: float
    pressure_bar: float
    flags: int

# 2. Інтерфейс підписника
class TelemetryConsumer(Protocol):
    def on_telemetry(self, event: TelemetryEvent) -> None:
        ...

# 3. Модуль стану пристроїв (Device Twin)
class DeviceTwinModule:
    def on_telemetry(self, event: TelemetryEvent) -> None:
        # Пряме оновлення оперативної пам'яті
        pass

# 4. Модуль порогових правил (Rules Engine)
class RulesEngineModule:
    def on_telemetry(self, event: TelemetryEvent) -> None:
        if event.temperature_c > 80.0:
            self._trigger_emergency_alert(event.device_id, event.temperature_c)
            
    def _trigger_emergency_alert(self, device_id: int, temp: float) -> None:
        pass

# 5. Внутрішня шина подій
class InMemoryEventBus:
    def __init__(self):
        self._consumers: List[TelemetryConsumer] = []
        
    def subscribe(self, consumer: TelemetryConsumer) -> None:
        self._consumers.append(consumer)
        
    def publish(self, event: TelemetryEvent) -> None:
        for consumer in self._consumers:
            consumer.on_telemetry(event)
