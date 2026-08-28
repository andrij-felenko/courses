import asyncio
from time import monotonic
from typing import Protocol

# ── Шов, який ми вже маємо: хаб говорить мовою DevicePort, а не мовою радіо. ──
class DevicePort(Protocol):
    async def read_temp(self, dev: str) -> float: ...          # °C
    async def set_relay(self, dev: str, on: bool) -> None: ...

# ── Усе правило хаба. Знає ЛИШЕ шов — жодного слова «Zigbee». Переживе спайк. ──
async def one_rule(port: DevicePort) -> None:
    if await port.read_temp("temp-1") < 20.0:
        await port.set_relay("heater-1", on=True)

# ── Адаптер: усе про Zigbee — ТІЛЬКИ тут. Помре спайк — а це зостанеться за швом. ──
# zigpy — той самий стек, що несе інтеграцію ZHA в Home Assistant (теж Python).
from bellows.zigbee.application import ControllerApplication   # bellows = Silicon Labs
import zigpy.types as t

ONOFF, TEMP, MEASURED = 0x0006, 0x0402, "measured_value"       # кластери/атрибут ZCL

class ZigbeeAdapter:
    def __init__(self, app: ControllerApplication):
        self._app = app
        self._ieee: dict[str, t.EUI64] = {}          # ім'я хаба → IEEE-адреса радіо

    def bind(self, name: str, ieee: str) -> None:    # шов ховає адресацію радіо
        self._ieee[name] = t.EUI64.convert(ieee)

    def _cluster(self, dev: str, cluster: int):
        node = self._app.devices[self._ieee[dev]]
        for ep_id, ep in node.endpoints.items():
            if ep_id != 0 and cluster in ep.in_clusters:   # ep 0 — ZDO, не прикладний
                return ep.in_clusters[cluster]
        raise LookupError(f"{dev}: кластер {cluster:#06x} не знайдено")

    async def read_temp(self, dev: str) -> float:
        ok, _ = await self._cluster(dev, TEMP).read_attributes([MEASURED])
        raw = ok[MEASURED]                           # напр. 1975 — а НЕ 19.75
        print(f"[драйвер] {dev}: сире={raw} → {raw / 100:.2f} °C")   # міряємо чесність
        return raw / 100.0                           # СОТІ °C → °C: робота адаптера

    async def set_relay(self, dev: str, on: bool) -> None:
        await self._cluster(dev, ONOFF).command(0x01 if on else 0x00)   # on / off


async def spike() -> None:
    # 1. Реальний координатор (USB-донгл). auto_form — сформувати мережу, як ще нема.
    app = ControllerApplication({"device": {"path": "/dev/ttyUSB0"},
                                 "database_path": "spike.db"})
    await app.startup(auto_form=True)
    port = ZigbeeAdapter(app)

    # 2. Парування — головне, чого не видно з дошки. Відчиняємо вікно, ЧЕКАЄМО ЗАЛІЗО.
    class OnJoin:
        def device_initialized(self, node):          # спрацьовує ПІСЛЯ інтерв'ю
            print(f"[парування] приєднався {node.ieee}, endpoint'ів: {len(node.endpoints) - 1}")
    app.add_listener(OnJoin())

    print("[спайк] вікно 60 с — тепер тисни кнопку парування НА ДАВАЧІ")
    t0 = monotonic()
    await app.permit(60)
    await asyncio.sleep(60)                           # даємо залізу час приєднатися
    print(f"[парування] у мережі {len(app.devices)} пристроїв за {monotonic() - t0:.0f} с")

    # 3. Людина звіряє, ЩО саме приєдналося, і в'яже дружні імена до IEEE-адрес.
    port.bind("temp-1",   "00:0d:6f:00:11:22:33:44")
    port.bind("heater-1", "00:0d:6f:00:aa:bb:cc:dd")

    # 4. Одне правило крізь шов — і заміряти актуатор: чи справді клацнуло реле.
    t1 = monotonic()
    await one_rule(port)
    print(f"[актуатор] команда on крізь шов за {(monotonic() - t1) * 1000:.0f} мс")

    # 5. Чи реле САМО звітує новий стан? Багато дешевих — мовчать; це теж факт.
    await asyncio.sleep(1)
    try:
        back, _ = await port._cluster("heater-1", ONOFF).read_attributes(["on_off"])
        print(f"[актуатор] реле звітує стан: {back['on_off']}")
    except Exception:
        print("[актуатор] реле НЕ звітує стан (дешеве реле) — правило працює всліпу")

    await app.shutdown()

asyncio.run(spike())
