"""Лічильники й гістограма конвеєра у текстовому форматі Prometheus."""

from __future__ import annotations

from .wire_format import Reason

# Смуги гістограми в секундах: від сотні мікросекунд до чверті секунди.
BUCKETS_S = (0.0001, 0.00025, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25)


class Metrics:
    def __init__(self) -> None:
        self.ingested_total = 0
        self.dropped_total = 0
        self.stored_total = 0
        self.batches_total = 0
        self.out_of_range_total = 0
        self.rejected: dict[str, int] = {reason.value: 0 for reason in Reason}
        self._buckets = [0] * (len(BUCKETS_S) + 1)
        self._latency_sum = 0.0
        self._latency_count = 0

    def on_rejected(self, reason: Reason) -> None:
        self.rejected[reason.value] += 1

    def on_stored(self, rows: int) -> None:
        self.stored_total += rows
        self.batches_total += 1

    def observe_latency(self, seconds: float) -> None:
        if seconds < 0.0:
            seconds = 0.0
        index = 0
        while index < len(BUCKETS_S) and seconds > BUCKETS_S[index]:
            index += 1
        self._buckets[index] += 1
        self._latency_sum += seconds
        self._latency_count += 1

    def render_prometheus(self) -> str:
        lines = [
            "# HELP telemetry_ingested_total Кадрів, узятих приймачем у чергу.",
            "# TYPE telemetry_ingested_total counter",
            f"telemetry_ingested_total {self.ingested_total}",
            "# HELP telemetry_dropped_total Кадрів, утрачених через переповнення черги.",
            "# TYPE telemetry_dropped_total counter",
            f"telemetry_dropped_total {self.dropped_total}",
            "# HELP telemetry_rejected_total Кадрів, відкинутих розбором.",
            "# TYPE telemetry_rejected_total counter",
        ]
        for reason, count in self.rejected.items():
            lines.append(f'telemetry_rejected_total{{reason="{reason}"}} {count}')

        lines += [
            "# HELP telemetry_out_of_range_total Подій поза фізичним діапазоном давача.",
            "# TYPE telemetry_out_of_range_total counter",
            f"telemetry_out_of_range_total {self.out_of_range_total}",
            "# HELP telemetry_stored_total Рядків, записаних у сховище.",
            "# TYPE telemetry_stored_total counter",
            f"telemetry_stored_total {self.stored_total}",
            "# HELP telemetry_processing_latency_seconds Час від прийому до розбору.",
            "# TYPE telemetry_processing_latency_seconds histogram",
        ]

        # Смуги гістограми — накопичувальні: кожна включає всі попередні.
        cumulative = 0
        for edge, count in zip(BUCKETS_S, self._buckets):
            cumulative += count
            lines.append(f'telemetry_processing_latency_seconds_bucket{{le="{edge}"}} {cumulative}')
        cumulative += self._buckets[-1]
        lines += [
            f'telemetry_processing_latency_seconds_bucket{{le="+Inf"}} {cumulative}',
            f"telemetry_processing_latency_seconds_sum {self._latency_sum:.6f}",
            f"telemetry_processing_latency_seconds_count {self._latency_count}",
        ]
        return "\n".join(lines)
