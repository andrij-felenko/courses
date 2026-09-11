# --- 1. СТАБІЛЬНЕ ЯДРО (I = 0) ---

# core/heating_plan.py
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

@dataclass(frozen=True)
class EnergyRate:
    price_per_kwh: float
    currency: str
    valid_until: datetime

# core/ports.py
# Контракт порту: належить доменному шару ядра.
class TariffProvider(Protocol):
    async def get_current_rate(self, zone_id: str) -> EnergyRate: ...

# core/heating_service.py
# Бізнес-логіка: використовує лише протокол TariffProvider.
class HeatingAutomationService:
    def __init__(self, tariff_provider: TariffProvider) -> None:
        self._tariff_provider = tariff_provider

    async def calculate_heating_power(
        self, zone_id: str, target_temp: float, current_temp: float
    ) -> float:
        temp_delta = target_temp - current_temp
        if temp_delta <= 0.0:
            return 0.0  # Кімната нагріта

        rate = await self._tariff_provider.get_current_rate(zone_id)

        # Консервативне правило: обмеження навантаження у дорогий період
        is_peak_rate = rate.price_per_kwh > 4.5
        base_power = temp_delta * 500.0  # Ват

        return base_power * 0.6 if is_peak_rate else base_power

# --- 2. ВОЛАТИЛЬНА ПЕРИФЕРІЯ (I = 1) ---

# adapters/nordpool_tariff_adapter.py
# Адаптер: реалізує протокол ядра та інкапсулює мережевий виклик.
import httpx
from core.heating_plan import EnergyRate
from core.ports import TariffProvider

class NordPoolTariffAdapter(TariffProvider):
    def __init__(self, api_endpoint: str) -> None:
        self._api_endpoint = api_endpoint

    async def get_current_rate(self, zone_id: str) -> EnergyRate:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._api_endpoint}/prices/latest", params={"zone": zone_id}
            )
            response.raise_for_status()
            raw_data = response.json()

        # Трансляція полів стороннього постачальника в доменну модель ядра
        return EnergyRate(
            price_per_kwh=raw_data["rate_cents_raw"] / 100.0,
            currency="UAH",
            valid_until=datetime.fromtimestamp(raw_data["expires_epoch_sec"]),
        )
