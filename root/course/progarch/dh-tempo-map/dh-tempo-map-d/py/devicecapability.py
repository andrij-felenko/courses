# Канонічні можливості фізичного обладнання
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Set

class DeviceCapability(str, Enum):
    BINARY_SWITCH = "binary-switch"
    DIMMABLE = "dimmable"
    POWER_METER = "power-meter"

@dataclass(frozen=True)
class DeviceProperties:
    power: Optional[bool] = None
    brightness_percent: Optional[int] = None  # Фізична яскравість: 0..100%
    power_watts: Optional[float] = None       # Споживана потужність за системою SI

@dataclass(frozen=True)
class CanonicalStateSnapshot:
    device_id: str
    capabilities: Set[DeviceCapability]
    target: DeviceProperties
    actual: DeviceProperties
    last_confirmed_at: float
    has_discrepancy: bool

# Канонічний агрегат ядра: містить лише фізичні реалії
class CanonicalDevice:
    def __init__(
        self,
        device_id: str,
        capabilities: Set[DeviceCapability],
        initial_actual: DeviceProperties
    ) -> None:
        self.id: str = device_id
        self.capabilities: Set[DeviceCapability] = capabilities
        self._target: DeviceProperties = initial_actual
        self._actual: DeviceProperties = initial_actual
        self._last_confirmation_time: float = 0.0

    def apply_command(self, mutation: DeviceProperties) -> None:
        self._validate_mutation(mutation)
        self._target = DeviceProperties(
            power=mutation.power if mutation.power is not None else self._target.power,
            brightness_percent=mutation.brightness_percent if mutation.brightness_percent is not None else self._target.brightness_percent,
            power_watts=self._target.power_watts
        )

    def confirm_actual(self, confirmed: DeviceProperties, timestamp: float) -> None:
        self._validate_mutation(confirmed)
        self._actual = DeviceProperties(
            power=confirmed.power if confirmed.power is not None else self._actual.power,
            brightness_percent=confirmed.brightness_percent if confirmed.brightness_percent is not None else self._actual.brightness_percent,
            power_watts=confirmed.power_watts if confirmed.power_watts is not None else self._actual.power_watts
        )
        self._last_confirmation_time = timestamp

    def get_snapshot(self) -> CanonicalStateSnapshot:
        has_discrepancy = False
        if self._target.power is not None and self._target.power != self._actual.power:
            has_discrepancy = True
        if self._target.brightness_percent is not None and self._target.brightness_percent != self._actual.brightness_percent:
            has_discrepancy = True

        return CanonicalStateSnapshot(
            device_id=self.id,
            capabilities=set(self.capabilities),
            target=self._target,
            actual=self._actual,
            last_confirmed_at=self._last_confirmation_time,
            has_discrepancy=has_discrepancy
        )

    def _validate_mutation(self, props: DeviceProperties) -> None:
        if props.power is not None and DeviceCapability.BINARY_SWITCH not in self.capabilities:
            raise ValueError(f"Пристрій {self.id} не підтримує бінарне перемикання")
        if props.brightness_percent is not None and DeviceCapability.DIMMABLE not in self.capabilities:
            raise ValueError(f"Пристрій {self.id} не підтримує регулювання рівня")

# Адаптер швидкої периферії: мобільний додаток підлаштовується під ядро
class MobileUiDeviceAdapter:
    def __init__(self, device: CanonicalDevice) -> None:
        self._device: CanonicalDevice = device

    def on_user_toggle(self, requested_power: bool) -> None:
        self._device.apply_command(DeviceProperties(power=requested_power))

    def build_view_model(self, localized_name: str, active_theme_color: str) -> dict:
        snapshot = self._device.get_snapshot()
        return {
            "title": localized_name,
            "color": active_theme_color,
            "is_switching": snapshot.has_discrepancy,
            "is_on": snapshot.actual.power is True,
            "current_load_watts": snapshot.actual.power_watts or 0.0
        }
