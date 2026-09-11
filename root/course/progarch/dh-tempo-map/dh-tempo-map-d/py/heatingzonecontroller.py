# digitalhomes/core/climate/heating_controller.py
from datetime import datetime
from digitalhomes.hardware.relays import ValveActuator
from digitalhomes.hardware.sensors import TemperatureSensor

# ДЕФЕКТ ІНВЕРСІЇ ТЕМПІВ: повільне ядро імпортує надшвидку периферію
from digitalhomes.cloud.tariffs import SpotPriceCloudClient
from digitalhomes.notifications.push import PushNotificationService


class HeatingZoneController:
    """Локальний контролер зони обігріву (повільне ядро, темп: місяці/роки)."""

    def __init__(
        self,
        zone_id: str,
        sensor: TemperatureSensor,
        valve: ValveActuator,
        target_temp: float = 21.0,
    ) -> None:
        self.zone_id = zone_id
        self.sensor = sensor
        self.valve = valve
        self.target_temp = target_temp

        # Прямі залежності ядра від зовнішньої хмари та мобільної периферії
        self.tariff_client = SpotPriceCloudClient(api_key="dh-prod-token")
        self.push_service = PushNotificationService()

    def evaluate_heating_cycle(self) -> None:
        """Регулярний такт регулювання температури (викликається щохвилини)."""
        current_temp = self.sensor.read_celsius()

        # ПРЯМИЙ ВИКЛИК ХМАРИ: синхронний блокувальний запит до біржі
        current_spot_rate = self.tariff_client.get_current_spot_price()

        effective_target = self.target_temp
        if current_spot_rate.is_economy_tier:
            # Накопичуємо дешеву теплову енергію
            effective_target += 1.0

        if current_temp < effective_target:
            self.valve.open()
            # ПРЯМИЙ ВИКЛИК ПЕРИФЕРІЇ: надсилання push-сповіщення
            self.push_service.send_alert(
                f"Зона {self.zone_id}: увімкнено нагрів за тарифом {current_spot_rate.price_eur} EUR/кВт·год"
            )
        else:
            self.valve.close()
