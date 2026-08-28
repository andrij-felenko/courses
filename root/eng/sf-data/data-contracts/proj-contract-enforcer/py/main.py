import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

class DataContractValidator:
    def __init__(self, contract_version: str):
        self.contract_version = contract_version
        self.valid_states = {"PENDING", "PAID", "PROCESSING", "SHIPPED", "CANCELLED", "REFUNDED"}

    def validate_record(self, raw_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        # 1. Перевірка обов'язкових полів (Nullability)
        required_fields = ["event_id", "order_id", "user_id", "order_state", "currency", "total_amount_cents", "created_at"]
        for f in required_fields:
            if f not in raw_data or raw_data[f] is None:
                return False, f"Відсутнє обов'язкове поле: {f}"

        # 2. Перевірка типів і допустимих діапазонів
        amount = raw_data["total_amount_cents"]
        if not isinstance(amount, int) or amount < 0:
            return False, "Поле total_amount_cents має бути невід'ємним цілим числом"

        items = raw_data.get("items_count", 1)
        if not isinstance(items, int) or items <= 0 or items > 500:
            return False, "Поле items_count має бути цілим числом у діапазоні [1, 500]"

        if raw_data["order_state"] not in self.valid_states:
            return False, f"Недопустимий статус order_state: {raw_data['order_state']}"

        if len(raw_data.get("currency", "")) != 3:
            return False, "Код currency має складатися рівно з 3 літер ISO-4217"

        # 3. Перевірка бізнес-інваріанту: tax <= total
        tax = raw_data.get("tax_amount_cents", 0)
        if isinstance(tax, int) and tax > amount:
            return False, "Інваріант порушено: tax_amount_cents перевищує total_amount_cents"

        return True, None

class IngestionGateway:
    def __init__(self, validator: DataContractValidator):
        self.validator = validator
        self.dwh_sink: List[Dict[str, Any]] = []
        self.dlq_sink: List[Dict[str, Any]] = []

    def process_event(self, raw_payload: str) -> None:
        try:
            record = json.loads(raw_payload)
        except Exception as e:
            self._route_to_dlq(raw_payload, f"Помилка парсингу JSON: {str(e)}")
            return

        is_valid, error_reason = self.validator.validate_record(record)
        if is_valid:
            # Збагачення метаданими валідації та запис у DWH
            record["_ingested_at"] = datetime.now(timezone.utc).isoformat()
            record["_contract_version"] = self.validator.contract_version
            self.dwh_sink.append(record)
        else:
            self._route_to_dlq(raw_payload, error_reason)

    def _route_to_dlq(self, payload: Any, reason: Optional[str]) -> None:
        quarantine_envelope = {
            "dlq_id": str(uuid.uuid4()),
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "contract_version": self.validator.contract_version,
            "error_reason": reason,
            "raw_payload": payload
        }
        self.dlq_sink.append(quarantine_envelope)

if __name__ == "__main__":
    val = DataContractValidator("2.3.0")
    gateway = IngestionGateway(val)

    good_event = json.dumps({
        "event_id": "a1b2c3d4-0000-0000-0000-000000000001",
        "order_id": "b2c3d4e5-0000-0000-0000-000000000002",
        "user_id": "c3d4e5f6-0000-0000-0000-000000000003",
        "order_state": "PAID",
        "currency": "USD",
        "total_amount_cents": 15000,
        "tax_amount_cents": 3000,
        "items_count": 2,
        "created_at": "2026-08-20T12:00:00Z"
    })

    bad_event = json.dumps({
        "event_id": "a1b2c3d4-0000-0000-0000-000000000002",
        "order_id": "b2c3d4e5-0000-0000-0000-000000000004",
        "user_id": "c3d4e5f6-0000-0000-0000-000000000005",
        "order_state": "UNKNOWN_STATE",
        "currency": "USD",
        "total_amount_cents": -500,
        "created_at": "2026-08-20T12:01:00Z"
    })

    gateway.process_event(good_event)
    gateway.process_event(bad_event)

    print(f"Прийнято у DWH: {len(gateway.dwh_sink)} | Відправлено в DLQ: {len(gateway.dlq_sink)}")
