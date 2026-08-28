import os
import sys
import time
import json
import random
import logging
import signal
from typing import Optional, Dict, Any
import redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(process)d: %(message)s")
logger = logging.getLogger("iot_worker")

STREAM_NAME = "iot:telemetry:stream"
GROUP_NAME = "telemetry_workers"
DLQ_STREAM_NAME = "iot:telemetry:dlq"
MAX_RETRIES = 3
BASE_BACKOFF_SEC = 1.5
MAX_BACKOFF_SEC = 30.0
LEASE_TIMEOUT_MS = 60000  # 60 секунд для XAUTOCLAIM

class GracefulKiller:
    """Перехоплювач системних сигналів для штатної зупинки воркера."""
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger.info(f"Отримано сигнал {signum}. Завершуємо поточні задачі та виходимо...")
        self.kill_now = True

def compute_jitter_backoff(attempt: int, base: float, cap: float) -> float:
    """Розрахунок Full Jitter затримки: random_uniform(0, min(cap, base * 2^attempt))."""
    temp = min(cap, base * (2 ** attempt))
    return random.uniform(0.0, temp)

def process_telemetry_payload(data: Dict[str, Any]) -> None:
    """
    Емуляція бізнес-логіки обробки IoT телеметрії:
    валідація датчиків, калібрування, збереження в Time-Series DB.
    """
    device_id = data.get("device_id")
    temperature = float(data.get("temp", 0.0))
    pressure = float(data.get("pressure", 0.0))

    if temperature < -50.0 or temperature > 150.0:
        raise ValueError(f"Аномальна температура {temperature}°C для пристрою {device_id} (фізичний брак сенсора)")

    # Емуляція випадкового тимчасового збою зв'язку з базою (10% випадків)
    if random.random() < 0.10:
        raise ConnectionResetError("Тимчасова помилка з'єднання з Time-Series сховищем")

    # Успішна обробка
    logger.info(f"✓ Успішно збережено телеметрію {device_id}: t={temperature:.1f}°C, p={pressure:.1f} hPa")

def run_worker(redis_client: redis.Redis, worker_name: str) -> None:
    killer = GracefulKiller()

    # Створюємо групу споживачів, якщо вона ще не існує
    try:
        redis_client.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
        logger.info(f"Створено споживчу групу '{GROUP_NAME}' на потоці '{STREAM_NAME}'")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

    logger.info(f"Воркер '{worker_name}' готовий до прийому IoT пакетів...")

    while not killer.kill_now:
        try:
            # 1. Спершу перевіряємо та перехоплюємо завислі повідомлення з інших воркерів (Pel Claim)
            claimed_entries = redis_client.xautoclaim(
                name=STREAM_NAME,
                groupname=GROUP_NAME,
                consumername=worker_name,
                min_idle_time=LEASE_TIMEOUT_MS,
                start_id="0-0",
                count=5
            )
            messages_to_process = claimed_entries[1]

            # 2. Якщо завислих немає, читаємо нові повідомлення зі стріму (блокування до 2000 мс)
            if not messages_to_process:
                response = redis_client.xreadgroup(
                    groupname=GROUP_NAME,
                    consumername=worker_name,
                    streams={STREAM_NAME: ">"},
                    count=10,
                    block=2000
                )
                if response:
                    _, messages_to_process = response[0]

            if not messages_to_process:
                continue

            for msg_id, raw_fields in messages_to_process:
                if killer.kill_now:
                    break

                # Розпакування полів із Redis (байти -> str -> JSON)
                payload_str = raw_fields.get(b"payload", b"{}").decode("utf-8")
                attempts = int(raw_fields.get(b"attempts", b"0"))
                data = json.loads(payload_str)

                device_id = data.get("device_id", "unknown")
                seq_no = data.get("seq_no", 0)
                dedup_key = f"iot:dedup:{device_id}:{seq_no}"

                # Дедуплікація на рівні виконання
                if not redis_client.set(dedup_key, "1", nx=True, ex=3600):
                    logger.warning(f"Пакет {device_id} seq={seq_no} уже був оброблений (дублікат). Надсилаємо XACK.")
                    redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)
                    continue

                try:
                    process_telemetry_payload(data)
                    # Успіх -> підтверджуємо в Redis Stream
                    redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)

                except ConnectionResetError as trans_err:
                    # Тимчасовий збій -> перевіряємо ліміт спроб
                    attempts += 1
                    logger.warning(f"Тимчасовий збій для {msg_id} (спроба {attempts}/{MAX_RETRIES}): {trans_err}")

                    if attempts < MAX_RETRIES:
                        backoff = compute_jitter_backoff(attempts, BASE_BACKOFF_SEC, MAX_BACKOFF_SEC)
                        logger.info(f"Пауза {backoff:.2f} с перед повтором...")
                        time.sleep(backoff)
                        # Оновлюємо лічильник спроб у стрімі
                        redis_client.xadd(STREAM_NAME, {"payload": payload_str, "attempts": str(attempts)})
                        redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)
                    else:
                        logger.error(f"Вичерпано спроби для {msg_id}. Перенаправлення в DLQ.")
                        dlq_entry = {
                            "original_id": msg_id,
                            "payload": payload_str,
                            "error": str(trans_err),
                            "attempts": str(attempts),
                            "failed_at": str(time.time())
                        }
                        redis_client.xadd(DLQ_STREAM_NAME, dlq_entry)
                        redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)

                except Exception as perm_err:
                    # Фатальна помилка (аномальні дані, некоректний тип) -> миттєво в DLQ
                    logger.error(f"Фатальна помилка для {msg_id}: {perm_err}. Відправляємо в DLQ без повторів.")
                    dlq_entry = {
                        "original_id": msg_id,
                        "payload": payload_str,
                        "error": str(perm_err),
                        "attempts": str(attempts + 1),
                        "failed_at": str(time.time())
                    }
                    redis_client.xadd(DLQ_STREAM_NAME, dlq_entry)
                    redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)

        except Exception as loop_err:
            logger.error(f"Помилка головного циклу воркера: {loop_err}")
            time.sleep(1.0)

    logger.info(f"Воркер '{worker_name}' коректно завершив роботу.")

if __name__ == "__main__":
    r = redis.Redis(host="localhost", port=6379, db=0)
    worker_id = f"worker_{os.getpid()}"
    run_worker(r, worker_id)
