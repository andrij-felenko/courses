from typing import Protocol

# Порт — стик телеметрії з рештою. Форма та сама, хоч у моноліті, хоч у сервісі.
class TelemetrySink(Protocol):
    async def record(self, e: DeviceEvent) -> None: ...

# Було, у моноліті: сусідній модуль у тому ж процесі — виклик у пам'яті.
class InProcessSink:
    async def record(self, e: DeviceEvent) -> None:
        self.store.append(e)                 # наносекунди, все-або-нічого

# Стало, після розрізу: той самий порт, але за ним — окремий сервіс за мережею.
# Уся мережева чесність зібрана ТУТ; ядро над портом її не бачить.
class RemoteSink:
    async def record(self, e: DeviceEvent) -> None:
        await self.bus.publish("telemetry", e)   # асинхронно, «щонайменше раз» + дедуп
