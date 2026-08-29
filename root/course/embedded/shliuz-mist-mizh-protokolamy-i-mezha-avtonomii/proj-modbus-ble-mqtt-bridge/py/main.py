#!/usr/bin/env python3
"""Шлюз між польовим сегментом (RS-485 + BLE) і хмарним брокером MQTT.

Три задачі, жодна не чекає на іншу:
  poller  — опитує Modbus і тут-таки виконує правило автономії;
  ble     — слухає ефір і розбирає рекламні кадри давачів;
  uplink  — тримає з'єднання з брокером і спорожняє буфер.
Зв'язок між ними — тільки через буфер Store-and-Forward.

Запуск із теки проєкту: ``python3 main.py``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import signal
import time
from itertools import count

from gateway import (
    BleError,
    BleScanner,
    ModbusError,
    ModbusMaster,
    MqttClient,
    MqttError,
    StoreForward,
    TelemetryMessage,
    regs_to_float,
)

MODBUS_DEVICE = "/dev/ttyUSB0"
MODBUS_BAUD = 19200
MODBUS_TIMEOUT = 0.5
SLAVE_ID = 1
PRESSURE_REGISTER = 0x0001  # два регістри: float32 тиску в барах
EMERGENCY_DUMP_COIL = 0x0010
ALARM_SET_BAR = 10.0
ALARM_CLEAR_BAR = 9.5  # гістерезис: інакше клапан смикався б навколо порога
POLL_PERIOD = 1.0

HCI_INDEX = 0

BROKER_HOST = "broker.plant.local"
BROKER_PORT = 1883
CLIENT_ID = "gw-unit1"
KEEPALIVE = 30

FRESH_CAPACITY = 64
BACKLOG_CAPACITY = 4096
DRAIN_RATE_PER_SECOND = 5.0
DRAIN_BURST = 10.0
BACKOFF_MIN = 1.0
BACKOFF_MAX = 30.0

log = logging.getLogger("gateway")
_sequence = count(1)


async def publish(buffer: StoreForward, topic: str, **fields: object) -> None:
    """Номер послідовності й мітку часу ставить шлюз, а не давач: за розривом у
    seq сервер бачить, скільки записів згоріло в переповненому буфері."""
    seq = next(_sequence)
    payload = json.dumps({"seq": seq, "ts": round(time.time() * 1000), **fields},
                         ensure_ascii=False, separators=(",", ":"))
    await buffer.publish(TelemetryMessage(topic=topic, payload=payload, seq=seq))


async def poller_task(bus: ModbusMaster, buffer: StoreForward, stop: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    alarm_latched = False
    errors_in_row = 0

    while not stop.is_set():
        started = loop.time()
        try:
            regs = await bus.read_holding(SLAVE_ID, PRESSURE_REGISTER, 2)
            if errors_in_row >= 3:
                await publish(buffer, "plant/unit1/status/fieldbus", link="up", slave=SLAVE_ID)
            errors_in_row = 0
            bar = regs_to_float(regs)

            # Межа автономії проходить саме тут. Дорога до хмари й назад коштує
            # секунд і може не відбутися взагалі, а клапан треба відкрити зараз.
            if not alarm_latched and bar > ALARM_SET_BAR:
                try:
                    await bus.write_coil(SLAVE_ID, EMERGENCY_DUMP_COIL, True)
                    alarm_latched = True
                    log.warning("[автономія] тиск %.2f бар > %.1f — котушку 0x%04X увімкнено",
                                bar, ALARM_SET_BAR, EMERGENCY_DUMP_COIL)
                    await publish(buffer, "plant/unit1/event/alarm", rule="pressure_high",
                                  p_bar=round(bar, 2), action="dump_on")
                except ModbusError as error:
                    # Засувка не спрацювала — засувка й лишається метою: латч не
                    # ставимо, наступний такт спробує знову.
                    log.error("[автономія] СКИДАННЯ НЕ ПРОЙШЛО (%s) — повтор наступним тактом", error)
                    await publish(buffer, "plant/unit1/event/alarm", rule="pressure_high",
                                  p_bar=round(bar, 2), action="dump_failed")
            elif alarm_latched and bar < ALARM_CLEAR_BAR:
                await bus.write_coil(SLAVE_ID, EMERGENCY_DUMP_COIL, False)
                alarm_latched = False
                log.info("[автономія] тиск %.2f бар — аварію знято, котушку вимкнено", bar)
                await publish(buffer, "plant/unit1/event/alarm", rule="pressure_high",
                              p_bar=round(bar, 2), action="dump_off")

            await publish(buffer, "plant/unit1/telemetry/pressure", dev="boiler_1",
                          p_bar=round(bar, 2), alarm=alarm_latched)

        except ModbusError as error:
            errors_in_row += 1
            log.warning("[modbus] вузол %d: %s (підряд %d)", SLAVE_ID, error, errors_in_row)
            # Про смерть шини сервер має дізнатися окремим повідомленням:
            # мовчання телеметрії він списав би на обрив WAN.
            if errors_in_row == 3:
                await publish(buffer, "plant/unit1/status/fieldbus", link="down",
                              slave=SLAVE_ID, why=str(error))

        await asyncio.sleep(max(0.0, POLL_PERIOD - (loop.time() - started)))


async def ble_task(buffer: StoreForward, stop: asyncio.Event) -> None:
    try:
        scanner = await BleScanner.start(HCI_INDEX)
    except (BleError, OSError) as error:
        # Радіо не піднялося — це привід працювати без нього, а не падати:
        # дротова шина й аварійне правило від BLE не залежать.
        log.error("[ble] сканер hci%d не піднявся (%s) — шлюз працює лише по шині",
                  HCI_INDEX, error)
        return

    log.info("[ble] пасивне сканування hci%d увімкнено", HCI_INDEX)
    try:
        while not stop.is_set():
            try:
                sample = await scanner.next_sample(0.5)
            except BleError as error:
                log.error("[ble] сканування зупинено: %s", error)
                return
            if sample is None:
                continue
            await publish(buffer, "plant/unit1/telemetry/temperature",
                          dev=sample.address_text, t_c=round(sample.temperature_c, 2),
                          batt=sample.battery_pct, rssi=sample.rssi_dbm)
    finally:
        await scanner.close()


async def uplink_task(buffer: StoreForward, stop: asyncio.Event) -> None:
    backoff = BACKOFF_MIN

    while not stop.is_set():
        try:
            client = await MqttClient.connect(BROKER_HOST, BROKER_PORT, CLIENT_ID, KEEPALIVE)
        except MqttError as error:
            stats = buffer.stats()
            # Джитер обов'язковий: після падіння базової станції сотні шлюзів
            # прокидаються разом, і рівний відступ звів би їх в один залп.
            wait = random.uniform(backoff / 2, backoff * 1.5)
            log.warning("[wan] %s; повтор через %.1f с; у буфері %d+%d, втрачено %d",
                        error, wait, stats.fresh, stats.backlog, stats.dropped)
            await asyncio.sleep(wait)
            backoff = min(BACKOFF_MAX, backoff * 2)
            continue

        backoff = BACKOFF_MIN
        log.info("[wan] з'єднання з брокером піднято")
        loop = asyncio.get_running_loop()
        tokens = DRAIN_BURST
        last_fill = loop.time()

        try:
            while not stop.is_set():
                now = loop.time()
                tokens = min(DRAIN_BURST, tokens + (now - last_fill) * DRAIN_RATE_PER_SECOND)
                last_fill = now

                lease = await buffer.peek(0.2)
                if lease is None:
                    continue

                # Свіже йде без обмежень, архів — лише за наявності токена:
                # інакше викачування триденної історії з'їло б увесь канал, і
                # щойно зняті показники чекали б за спиною в старих записів.
                if lease.from_backlog and tokens < 1.0:
                    await asyncio.sleep(0.05)
                    continue

                await client.publish_qos1(lease.message.topic, lease.message.payload)
                await buffer.commit(lease)
                if lease.from_backlog:
                    tokens -= 1.0
        except MqttError as error:
            # Непідтверджене повідомлення лишається в черзі й піде після
            # перепідключення; брокер може отримати дублікат — нормальна ціна
            # доставки «щонайменше раз».
            log.warning("[wan] %s — перепідключення", error)
        finally:
            await client.close()


async def stats_task(buffer: StoreForward, stop: asyncio.Event) -> None:
    while not stop.is_set():
        await asyncio.sleep(5.0)
        stats = buffer.stats()
        log.info("[буфер] свіжих %d, архівних %d, втрачено назавжди %d",
                 stats.fresh, stats.backlog, stats.dropped)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    buffer = StoreForward(FRESH_CAPACITY, BACKLOG_CAPACITY)
    try:
        bus = ModbusMaster(MODBUS_DEVICE, MODBUS_BAUD, MODBUS_TIMEOUT)
    except (OSError, ModbusError) as error:
        log.error("порт %s не відкрився: %s", MODBUS_DEVICE, error)
        return

    log.info("=== шлюз піднято: %s @ %d, брокер %s:%d ===",
             MODBUS_DEVICE, MODBUS_BAUD, BROKER_HOST, BROKER_PORT)

    tasks = [
        asyncio.create_task(poller_task(bus, buffer, stop)),
        asyncio.create_task(ble_task(buffer, stop)),
        asyncio.create_task(uplink_task(buffer, stop)),
        asyncio.create_task(stats_task(buffer, stop)),
    ]

    await stop.wait()
    log.info("зупинка за сигналом…")
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    bus.close()
    log.info("=== шлюз зупинено ===")


if __name__ == "__main__":
    asyncio.run(main())
