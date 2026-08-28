# ⚙️ Служба прийому та нормалізації IoT-телеметрії на Python

У розподілених телеметричних системах серверний приймач MQTT виконує роль вхідного шлюзу: він утримує постійні з'єднання з брокером, підписується на ієрархічні топіки пристроїв, валідує вхідні бінарні або текстові корисні навантаження, нормалізує формат дат і часових поясів та передає очищений потік у сховище часових рядів чи брокер повідомлень (наприклад, Kafka, ClickHouse або Redis Streams).

Головна інженерна вимога до такої служби — безперервність роботи та стійкість до мережевих розривів. Служба не повинна блокувати цикл подій під час валідації чи запису в базу даних, зобов'язана обмежувати внутрішні буфери для запобігання переповненню оперативної пам'яті (Backpressure) та коректно завершувати роботу за сигналами ОС без втрати вже прийнятих пакетів.

## 1. Архітектурні принципи та декомпозиція системи

Розробка промислового приймача телеметрії вимагає суворого розділення мережевого введення-виведення та обчислювальної бізнес-логіки. Якщо обробник вхідного повідомлення виконує повільний дисковий запис або складну аналітику безпосередньо в мережевому циклі, клієнт перестає вичитувати мережевий сокет. Це призводить до переповнення буфера TCP на стороні операційної системи, затримки відправлення пакетів `PINGREQ` та примусового розриву з'єднання брокером за таймаутом Keep-Alive.

Служба будується на основі трьох ключових архітектурних шаблонів:

1. **Патерн «Виробник — Споживач» (Producer-Consumer):**
   Мережевий слухач (`mqtt_listener_task`) виступає виробником: його єдине завдання — вичитати байти з мережі та якнайшвидше помістити об'єкт повідомлення у чергу пам'яті `asyncio.Queue`. Пул паралельних воркерів (`telemetry_worker`) виступає споживачем: вони паралельно витягують повідомлення з черги, десеріалізують JSON, виконують перевірку типів та накопичують батчі для масового запису в сховище.

2. **Захист від протитиску (Backpressure) та обмеження пам'яті:**
   У разі аварії бази даних або тимчасового сплеску трафіку черга повідомлень може розростатися до мільйонів об'єктів, що спричиняє вичерпання оперативної пам'яті процесу (Out of Memory). Встановлення жорсткого параметра `maxsize` для `asyncio.Queue` гарантує фіксований бюджет пам'яті. При переповненні черги служба реєструє інцидент у логах і застосовує політику скидання (Load Shedding), запобігаючи аварійному краху всього сервісу.

3. **Коректне завершення роботи (Graceful Shutdown):**
   При плановому оновленні сервісу або отриманні сигналів `SIGINT`/`SIGTERM` від системи оркестрації (Kubernetes, systemd) служба не обриває виконання раптово. Вона припиняє прийом нових пакетів з брокера, дозволяє воркерам повністю вичитати та зберегти залишок повідомлень з черги, скидає фінальний батч у базу даних і лише після цього закриває мережеві з'єднання.

## 2. Повна реалізація служби

Нижче наведено повний виробничий код сервісу на базі Python, бібліотеки `aiomqtt` (асинхронна обгортка над Paho MQTT v2) та валідатора схем `pydantic`.

```python
import asyncio
import json
import logging
import signal
import ssl
import sys
from datetime import datetime, timezone
from typing import Any
from dataclasses import dataclass

from aiomqtt import Client, MqttError, Message
from pydantic import BaseModel, Field, ValidationError

# Налаштування структурованого логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("mqtt_ingestion")


# ── 1. Схеми даних та валідація ───────────────────────────────────────────────

class SensorReading(BaseModel):
    """Схема валідації вхідних вимірювань давача."""
    temperature: float = Field(ge=-50.0, le=100.0, description="Температура в °C")
    humidity: float = Field(ge=0.0, le=100.0, description="Відносна вологість у %")
    battery_mv: int = Field(ge=1500, le=4500, description="Напруга живлення в мВ")
    timestamp_raw: int | str | None = Field(default=None, alias="ts")


class NormalizedPayload(BaseModel):
    """Нормалізований запис для збереження у сховищі часових рядів."""
    device_id: str
    tenant_id: str
    temperature: float
    humidity: float
    battery_v: float
    timestamp: datetime
    ingested_at: datetime


# ── 2. Конфігурація служби ───────────────────────────────────────────────────

@dataclass(frozen=True)
class ServiceConfig:
    broker_host: str = "mqtt.internal.iot"
    broker_port: int = 8883
    client_id: str = "telemetry-ingestion-srv-01"
    topic_subscription: str = "tenants/+/devices/+/telemetry"
    status_subscription: str = "tenants/+/devices/+/status"
    ca_cert_path: str | None = None
    client_cert_path: str | None = None
    client_key_path: str | None = None
    queue_capacity: int = 10000
    worker_concurrency: int = 4
    batch_flush_interval_sec: float = 1.0


# ── 3. Парсер топіків та нормалізатор ─────────────────────────────────────────

def parse_device_topic(topic: str) -> tuple[str, str, str] | None:
    """Розбирає ієрархічний топік 'tenants/{tenant}/devices/{device}/{type}'."""
    parts = topic.split("/")
    if len(parts) == 5 and parts[0] == "tenants" and parts[2] == "devices":
        return parts[1], parts[3], parts[4]
    return None


def normalize_timestamp(raw_ts: int | str | None) -> datetime:
    """Нормалізує різноманітні формати часових міток пристрою до єдиного UTC datetime."""
    now = datetime.now(timezone.utc)
    if raw_ts is None:
        return now

    try:
        if isinstance(raw_ts, (int, float)):
            # Обробка секунд або мілісекунд (Unix Epoch)
            if raw_ts > 1e11:  # Мілісекунди
                return datetime.fromtimestamp(raw_ts / 1000.0, tz=timezone.utc)
            return datetime.fromtimestamp(raw_ts, tz=timezone.utc)
        elif isinstance(raw_ts, str):
            # Парсинг ISO 8601
            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        logger.warning("Неможливо розпарсити мітку часу '%s', використовуємо поточний час", raw_ts)

    return now


# ── 4. Воркери обробки та запису ──────────────────────────────────────────────

async def telemetry_worker(
    worker_id: int,
    queue: asyncio.Queue[Message],
    shutdown_event: asyncio.Event
) -> None:
    """Корутина-воркер: вичитує сирі повідомлення, валідує та пакетує для сховища."""
    logger.info("Воркер #%d запущено", worker_id)
    batch: list[NormalizedPayload] = []

    while not shutdown_event.is_set() or not queue.empty():
        try:
            # Очікуємо повідомлення з черги з коротким таймаутом для періодичного скидання батчу
            message = await asyncio.wait_for(queue.get(), timeout=0.5)
        except asyncio.TimeoutError:
            # Таймаут: скидаємо накопичений батч, якщо є дані
            if batch:
                await flush_batch(batch)
                batch.clear()
            continue

        try:
            parsed = parse_device_topic(str(message.topic))
            if not parsed:
                logger.warning("Невідомий формат топіка: %s", message.topic)
                continue

            tenant_id, device_id, msg_type = parsed

            # Обробка телеметрії
            if msg_type == "telemetry":
                raw_data = json.loads(message.payload.decode("utf-8"))
                reading = SensorReading.model_validate(raw_data)

                normalized = NormalizedPayload(
                    device_id=device_id,
                    tenant_id=tenant_id,
                    temperature=reading.temperature,
                    humidity=reading.humidity,
                    battery_v=reading.battery_mv / 1000.0,
                    timestamp=normalize_timestamp(reading.timestamp_raw),
                    ingested_at=datetime.now(timezone.utc)
                )
                batch.append(normalized)

                if len(batch) >= 100:
                    await flush_batch(batch)
                    batch.clear()

            # Обробка LWT / статусу підключення
            elif msg_type == "status":
                status_text = message.payload.decode("utf-8", errors="replace")
                logger.info("Статус вузла [%s/%s]: %s (retain=%s)", tenant_id, device_id, status_text, message.retain)

        except ValidationError as err:
            logger.error("Помилка валідації payload від [%s]: %s", message.topic, err.json())
        except Exception as err:
            logger.exception("Непередбачений збій під час обробки пакета: %s", err)
        finally:
            queue.task_done()

    # Фінальне скидання залишків після завершення циклу
    if batch:
        await flush_batch(batch)
        batch.clear()

    logger.info("Воркер #%d коректно завершив роботу", worker_id)


async def flush_batch(batch: list[NormalizedPayload]) -> None:
    """Імітація пакетного асинхронного запису в сховище (ClickHouse / TimescaleDB)."""
    logger.info("Запис батчу з %d записів у базу даних...", len(batch))
    # В реальному коді: await db_pool.copy_records_to_table(..., records=batch)
    await asyncio.sleep(0.05)


# ── 5. Головний конвеєр служби ────────────────────────────────────────────────

def create_tls_context(config: ServiceConfig) -> ssl.SSLContext | None:
    """Створює захищений SSLContext для mTLS або верифікації брокера."""
    if not config.ca_cert_path:
        return None

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=config.ca_cert_path)
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    if config.client_cert_path and config.client_key_path:
        context.load_cert_chain(
            certfile=config.client_cert_path,
            keyfile=config.client_key_path
        )
    return context


async def mqtt_listener_task(
    config: ServiceConfig,
    queue: asyncio.Queue[Message],
    shutdown_event: asyncio.Event
) -> None:
    """Утримує з'єднання з брокером та передає вхідні пакети у чергу."""
    tls_ctx = create_tls_context(config)

    while not shutdown_event.is_set():
        try:
            logger.info("Підключення до MQTT брокера %s:%d...", config.broker_host, config.broker_port)
            async with Client(
                hostname=config.broker_host,
                port=config.broker_port,
                identifier=config.client_id,
                tls_context=tls_ctx,
                clean_session=False,
                timeout=10.0
            ) as client:
                logger.info("З'єднання встановлено. Оформлення підписок...")
                await client.subscribe([(config.topic_subscription, 1), (config.status_subscription, 1)])

                async for message in client.messages:
                    if shutdown_event.is_set():
                        break

                    try:
                        queue.put_nowait(message)
                    except asyncio.QueueFull:
                        logger.error("Черга переповнена (%d елементів)! Відкидання пакета з топіка %s",
                                     queue.maxsize, message.topic)

        except MqttError as err:
            if shutdown_event.is_set():
                break
            logger.warning("Розрив MQTT з'єднання: %s. Повторне підключення через 3с...", err)
            await asyncio.sleep(3.0)
        except Exception as err:
            if shutdown_event.is_set():
                break
            logger.exception("Фатальна помилка мережевого клієнта: %s", err)
            await asyncio.sleep(5.0)

    logger.info("Мережевий слухач MQTT завершив роботу.")


async def main() -> None:
    config = ServiceConfig(
        broker_host="localhost",
        broker_port=1883,
        ca_cert_path=None
    )

    queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=config.queue_capacity)
    shutdown_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    def handle_signal(sig_name: str) -> None:
        logger.info("Отримано сигнал %s. Початок Graceful Shutdown...", sig_name)
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal, sig.name)
        except NotImplementedError:
            pass

    worker_tasks = [
        asyncio.create_task(telemetry_worker(i, queue, shutdown_event), name=f"worker-{i}")
        for i in range(config.worker_concurrency)
    ]

    listener = asyncio.create_task(mqtt_listener_task(config, queue, shutdown_event), name="mqtt-listener")

    logger.info("Служба прийому IoT телеметрії успішно запущена.")

    await shutdown_event.wait()
    await listener

    logger.info("Очікування завершення обробки черги (%d залишок)...", queue.qsize())
    await asyncio.gather(*worker_tasks, return_exceptions=True)

    logger.info("Служба прийому IoT успішно зупинена.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```

## 3. Розбір крайових випадків та відмовостійкість

Під час промислової експлуатації служба стикається з низкою специфічних мережевих та апаратних аномалій, які необхідно враховувати в архітектурі:

1. **Дрейф апаратного годинника давачів (Clock Skew):**
   Дешеві мікроконтролери без резервної батарейки RTC або доступу до серверів точного часу NTP часто надсилають некоректні мітки часу: або епоху 1970 року після скидання живлення, або мітки з майбутнього. Функція `normalize_timestamp` зобов'язана перевіряти правдоподібність вхідного значення: якщо мітка відхиляється від серверного часу більше ніж на допустимий поріг (наприклад, 24 години), запис маркується спеціальним прапорцем підозрілості або замінюється поточним часом сервера `ingested_at`.

2. **Шторм перепідключень (Reconnection Storm):**
   Після відновлення електропостачання в цілому районі тисячі пристроїв одночасно намагаються відновити TCP-сесії з брокером. Якщо приймач перезапуститься в цей момент, він отримає лавину накопичених збережених повідомлень QoS 1. Використання пакетного запису (`flush_batch`) дозволяє об'єднувати сотні рядків в одну транзакцію `INSERT INTO ... VALUES`, утримуючи час відгуку сховища в межах норми.

3. **Обробка помилок валідації та отруйні повідомлення (Poison Pills):**
   Якщо пристрій через збій прошивки надсилає невалідний JSON або байти випадкового шуму, парсер `json.loads` або валідатор `SensorReading` викидає виняток. Обробник у воркері перехоплює `ValidationError`, записує інцидент у лог або відправляє сире повідомлення у спеціальний топік аварій (Dead Letter Queue) та продовжує виконання, не допускаючи падіння корутини воркера.

4. **Ідемпотентність при QoS 1:**
   Рівень доставки QoS 1 гарантує надходження повідомлення «щонайменше один раз». При короткочасних мережевих затримках пакет підтвердження `PUBACK` від брокера може не дійти до пристрою вчасно, і давач надішле той самий пакет повторно. Сховище даних повинно підтримувати ідемпотентний запис (наприклад, конструкцію `ON CONFLICT (device_id, timestamp) DO UPDATE` в PostgreSQL або дедуплікацію на рівні рушія `ReplacingMergeTree` у ClickHouse).

## 4. Конфігурація системної служби systemd

Для розгортання приймача в середовищі Linux сервіс оформлюється як системний юніт `systemd`, що гарантує автоматичний запуск при старті ОС, ізоляцію ресурсів та автоматичний перезапуск при непередбачених збоях.

```ini
[Unit]
Description=IoT Telemetry MQTT Ingestion Service
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=iot-service
Group=iot-service
WorkingDirectory=/opt/iot-ingestion
ExecStart=/opt/iot-ingestion/.venv/bin/python -m ingestion.main
Restart=always
RestartSec=5s

# Обмеження пам'яті та ресурсів
MemoryMax=1G
MemoryHigh=800M
CPUQuota=200%

# Захист та ізоляція процесу
ProtectSystem=strict
ProtectHome=true
NoNewPrivileges=true
PrivateTmp=true

# Тайм-аут на Graceful Shutdown (час на вичитку черги)
TimeoutStopSec=30s
KillSignal=SIGTERM

[Install]
WantedBy=multi-user.target
```

Параметр `TimeoutStopSec=30s` надає службі достатньо часу після надсилання `SIGTERM`, щоб спорожнити внутрішню чергу `asyncio.Queue`, скинути всі накопичені батчі на диск та коректно надіслати `DISCONNECT` брокеру перед тим, як `systemd` примусово завершить процес сигналом `SIGKILL`.
