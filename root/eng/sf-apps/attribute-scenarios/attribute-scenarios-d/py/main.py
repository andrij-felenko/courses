import math

def p95(samples_ms: list[float]) -> float:
    ordered = sorted(samples_ms)
    # Метод найближчого рангу: індекс, нижче за який лежить 95% значень.
    k = math.ceil(0.95 * len(ordered)) - 1
    return ordered[max(k, 0)]

def meets_latency_scenario(samples_ms: list[float], threshold_ms: float) -> bool:
    # Сценарій: у пік профіль віддається за <= threshold у 95% випадків.
    if not samples_ms:
        return False                     # без даних вимогу не підтверджено
    return p95(samples_ms) <= threshold_ms
