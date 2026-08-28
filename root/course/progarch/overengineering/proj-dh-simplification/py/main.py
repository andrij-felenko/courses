# ============================================================================
# ВАРІАНТ B (Прагматичний): Модульний моноліт на Python
# Пряма обробка пачки без Kafka та gRPC
# ============================================================================

from dataclasses import dataclass
from typing import List, Dict, Any
import json

@dataclass(frozen=True)
class TelemetryMetric:
    device_id: str
    home_id: str
    energy_kwh: float
    temperature_c: float
    timestamp: int

@dataclass(frozen=True)
class AggregateResult:
    home_id: str
    total_energy_kwh: float
    avg_temperature_c: float
    threshold_exceeded: bool

class HomeAnalyticsService:
    def process_hourly_batch(
        self,
        home_id: str,
        metrics: List[TelemetryMetric],
        max_energy_threshold: float
    ) -> AggregateResult:
        if not metrics:
            raise ValueError("Empty metrics batch")

        total_energy = sum(m.energy_kwh for m in metrics)
        avg_temp = sum(m.temperature_c for m in metrics) / len(metrics)
        alert_needed = total_energy > max_energy_threshold

        # Атомарне збереження в БД й додавання події в outbox:
        # with db.transaction():
        #     db.execute(
        #         "INSERT INTO hourly_aggregates (home_id, total_energy_kwh, avg_temperature_c) VALUES (%s, %s, %s)",
        #         (home_id, total_energy, avg_temp)
        #     )
        #     if alert_needed:
        #         db.execute(
        #             "INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) VALUES (%s, %s, %s, %s)",
        #             ("HomeAggregate", home_id, "HIGH_ENERGY_ALERT", json.dumps({"home_id": home_id, "energy": total_energy}))
        #         )

        return AggregateResult(
            home_id=home_id,
            total_energy_kwh=total_energy,
            avg_temperature_c=avg_temp,
            threshold_exceeded=alert_needed
        )
