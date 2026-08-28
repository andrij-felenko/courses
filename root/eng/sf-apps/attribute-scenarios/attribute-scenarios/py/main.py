from dataclasses import dataclass

# Межа зі сценарію: перерва не довша за 30 секунд.
SCENARIO_MAX_OUTAGE_MS = 30_000


@dataclass
class Failover:
    down_at_ms: int     # коли головний вузол перестав відповідати (стимул)
    up_at_ms: int       # коли резерв почав обслуговувати (відповідь)
    serving: bool       # чи хтось узагалі обслуговує запити


# True — сценарій виконано (перерва в межах міри); False — порушено.
def failover_meets_scenario(f: Failover) -> bool:
    if not f.serving:                # взагалі не піднялися — це відмова
        return False

    outage = f.up_at_ms - f.down_at_ms   # фактична перерва, мс
    return outage <= SCENARIO_MAX_OUTAGE_MS   # порівняння з мірою
