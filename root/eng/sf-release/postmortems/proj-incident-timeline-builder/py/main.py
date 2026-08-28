from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional


class Phase(Enum):
    DEFECT_INJECTED = "defect_injected"
    TRIGGER_EVENT = "trigger_event"
    IMPACT_STARTED = "impact_started"
    DETECTED_BY_ALERT = "detected_by_alert"
    ACKNOWLEDGED_BY_ONCALL = "acknowledged_by_oncall"
    MITIGATION_APPLIED = "mitigation_applied"
    IMPACT_ENDED = "impact_ended"
    FULLY_RESOLVED = "fully_resolved"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TimelineEvent:
    timestamp: datetime
    phase: Phase
    component: str
    description: str
    source_url: str


@dataclass
class IncidentMetrics:
    mttd_seconds: float
    mtta_seconds: float
    mttm_seconds: float
    mttr_seconds: float
    total_impact_seconds: float


class ValidationError(Exception):
    pass


class TimelineReconstructor:
    def __init__(self) -> None:
        self._events: List[TimelineEvent] = []

    def add_event(self, event: TimelineEvent) -> None:
        self._events.append(event)

    def process_and_validate(self) -> IncidentMetrics:
        if not self._events:
            raise ValidationError("Таймлайн порожній")

        # Сортування за міткою часу
        sorted_events = sorted(self._events, key=lambda e: e.timestamp)

        phases_map = {ev.phase: ev.timestamp for ev in sorted_events}

        t_impact = phases_map.get(Phase.IMPACT_STARTED)
        t_detect = phases_map.get(Phase.DETECTED_BY_ALERT)
        t_ack = phases_map.get(Phase.ACKNOWLEDGED_BY_ONCALL)
        t_mitigate = phases_map.get(Phase.MITIGATION_APPLIED)
        t_impact_end = phases_map.get(Phase.IMPACT_ENDED)
        t_resolve = phases_map.get(Phase.FULLY_RESOLVED)

        if not t_impact:
            raise ValidationError("Відсутня обов'язкова фаза початку впливу (IMPACT_STARTED)")
        if not t_resolve and not t_impact_end:
            raise ValidationError("Відсутня фаза завершення інциденту (FULLY_RESOLVED або IMPACT_ENDED)")

        if t_detect and t_ack and t_ack < t_detect:
            raise ValidationError("Порушення інваріанту: підтвердження (ACK) раніше за виявлення алерта")
        if t_detect and t_mitigate and t_mitigate < t_detect:
            raise ValidationError("Порушення інваріанту: пом'якшення раніше за виявлення алерта")

        mttd = (t_detect - t_impact).total_seconds() if t_detect and t_impact else 0.0
        mtta = (t_ack - t_detect).total_seconds() if t_ack and t_detect else 0.0
        mttm = (t_mitigate - t_ack).total_seconds() if t_mitigate and t_ack else 0.0
        mttr = (t_resolve - t_impact).total_seconds() if t_resolve and t_impact else 0.0

        if t_impact_end and t_impact:
            total_impact = (t_impact_end - t_impact).total_seconds()
        else:
            total_impact = mttr

        return IncidentMetrics(
            mttd_seconds=mttd,
            mtta_seconds=mtta,
            mttm_seconds=mttm,
            mttr_seconds=mttr,
            total_impact_seconds=total_impact,
        )


if __name__ == "__main__":
    t0 = datetime.now(timezone.utc)
    reconstructor = TimelineReconstructor()

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0,
            phase=Phase.IMPACT_STARTED,
            component="checkout-gateway",
            description="Стрибок 5xx помилок через блокування пулу HikariCP",
            source_url="https://monitoring.internal/alerts/500",
        )
    )

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0 + timedelta(seconds=120),
            phase=Phase.DETECTED_BY_ALERT,
            component="alertmanager",
            description="Спрацював алерт High5xxErrorRate (burn rate > 14x)",
            source_url="https://alertmanager.internal/#/alert/412",
        )
    )

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0 + timedelta(seconds=300),
            phase=Phase.ACKNOWLEDGED_BY_ONCALL,
            component="pagerduty",
            description="Черговий інженер підтвердив інцидент",
            source_url="https://pagerduty.internal/inc/841",
        )
    )

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0 + timedelta(seconds=1500),
            phase=Phase.MITIGATION_APPLIED,
            component="feature-flags",
            description="Вимкнено виклик зовнішнього податкового шлюзу",
            source_url="https://flags.internal/tax-fallback",
        )
    )

    reconstructor.add_event(
        TimelineEvent(
            timestamp=t0 + timedelta(seconds=2400),
            phase=Phase.FULLY_RESOLVED,
            component="checkout-gateway",
            description="Черги розвантажилися, p99 латентність повернулася до норми",
            source_url="https://grafana.internal/d/health",
        )
    )

    metrics = reconstructor.process_and_validate()
    print(f"MTTD: {metrics.mttd_seconds / 60:.1f} хв")
    print(f"MTTA: {metrics.mtta_seconds / 60:.1f} хв")
    print(f"MTTM: {metrics.mttm_seconds / 60:.1f} хв")
    print(f"MTTR: {metrics.mttr_seconds / 60:.1f} хв")
