# platform_client.py — Робочий Python SDK платформи для Stream-команд
import time
import uuid
import logging
import requests
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DHPlatformClient")

@dataclass
class DatabaseProvisionSpec:
    service_name: str
    team_id: str
    db_name: str
    allocated_storage_gb: int
    enable_ha: bool = True
    backup_retention_days: int = 30

class DHPlatformException(Exception):
    """Базовий виняток при помилці платформи."""
    pass

class DigitalHomesPlatformClient:
    """
    Платформний клієнт для замовлення інфраструктури без квитанцій і чекання.
    """
    def __init__(self, endpoint: str, api_token: str, timeout_sec: float = 15.0):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout_sec
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "X-DH-Client-Version": "2.4.0-py"
        })

    def provision_postgres_database(
        self, 
        spec: DatabaseProvisionSpec, 
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ідемпотентний запит на створення бази даних.
        """
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())

        url = f"{self.endpoint}/v1/resources/postgresql"
        headers = {"X-Idempotency-Key": idempotency_key}
        payload = asdict(spec)

        logger.info("Надсилання запиту на розгортання БД '%s' для команди '%s'", spec.db_name, spec.team_id)
        
        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise DHPlatformException(f"Мережева помилка зв'язку з платформою: {e}") from e

        if resp.status_code != 202:
            raise DHPlatformException(f"Платформа відхилила запит ({resp.status_code}): {resp.text}")

        job_data = resp.json()
        job_id = job_data.get("jobId")
        logger.info("Запит прийнято платформою. JobID: %s. Починаємо опитування...", job_id)
        
        return self._poll_job_until_completion(job_id)

    def _poll_job_until_completion(self, job_id: str, max_wait_sec: int = 180) -> Dict[str, Any]:
        url = f"{self.endpoint}/v1/jobs/{job_id}"
        start_time = time.time()

        while time.time() - start_time < max_wait_sec:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status")
                    
                    if status == "COMPLETED":
                        logger.info("Ресурс успішно розгорнуто платформою за %.1f сек!", time.time() - start_time)
                        return data.get("resultResource", {})
                    elif status == "FAILED":
                        error_msg = data.get("error", "Невідома помилка платформи")
                        raise DHPlatformException(f"Створення ресурсу провалилося: {error_msg}")
                    
                    logger.debug("Стан розгортання [%s]... Чекаємо 4 сек.", status)
            except requests.RequestException as e:
                logger.warning("Тимчасова помилка опитача: %s. Повторюємо...", e)

            time.sleep(4.0)

        raise DHPlatformException(f"Перевищено таймаут очікування розгортання ресурсу ({max_wait_sec} сек)")
