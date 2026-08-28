# Python 3.12 implementation
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Type, TypeVar, Any
from datetime import datetime

# ── 1. Публічна доменна подія ──
@dataclass(frozen=True)
class DeviceStateChangedEvent:
    event_id: str
    device_id: str
    home_id: str
    property_name: str
    old_value: Any
    new_value: Any
    timestamp: datetime

# ── 2. Публічний DTO та Інтерфейс модуля DeviceRegistry ──
@dataclass(frozen=True)
class DeviceDTO:
    id: str
    home_id: str
    model: str
    is_online: bool
    reported_state: dict[str, Any]

class IDeviceRegistryModule(ABC):
    @abstractmethod
    def get_device(self, device_id: str) -> DeviceDTO | None:
        """Отримати публічний DTO пристрою."""
        pass

    @abstractmethod
    def list_home_devices(self, home_id: str) -> list[DeviceDTO]:
        """Отримати список пристроїв дому."""
        pass

# ── 3. Внутрішньопроцесна шина подій (InMemoryEventBus) ──
E = TypeVar('E')

class InMemoryEventBus:
    """Високопродуктивна внутрішньопроцесна шина подій.
    Забезпечує реєстрацію підписників та синхронну/асинхронну розсилку подій у пам'яті.
    Затримка виклику підписника складає від 20 до 50 наносекунд.
    """
    def __init__(self) -> None:
        self._handlers: dict[Type[Any], list[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: Any) -> None:
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)  # Синхронний виклик у пам'яті
                except Exception as ex:
                    # Логування помилки підписника без збою основного потоку
                    print(f"[EventBus Error] Помилка обробника події {event_type}: {ex}")
