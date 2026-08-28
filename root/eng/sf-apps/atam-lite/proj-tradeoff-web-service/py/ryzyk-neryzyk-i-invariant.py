# Фітнес-функція: стереже інваріант «лаг реплікації < вікно W».
# Крутиться і в моніторингу (безперервно), і в CI (перед викочуванням змін).
# Порушиться інваріант — read-your-writes провалиться ТИХО, без помилки;
# тому ловимо завчасно, поки лаг лише підповзає до межі, а не після скарг.
import asyncio

WINDOW_MS = 1000               # те саме W, що й у маршрутизації читань
BUDGET_MS = 0.6 * WINDOW_MS    # тривога, коли лаг з'їв 60 % запасу вікна

async def replica_lag_ms(replica) -> float:
    # На Postgres: на скільки часу репліка відстає від основної.
    row = await replica.fetchrow(
        "SELECT extract(epoch from (now() - pg_last_xact_replay_timestamp()))"
        "       * 1000 AS lag_ms"
    )
    return row["lag_ms"] or 0.0

async def assert_lag_within_window(replicas, samples=300, interval_s=0.1):
    worst = []
    for _ in range(samples):
        worst.append(max([await replica_lag_ms(r) for r in replicas]))
        await asyncio.sleep(interval_s)
    worst.sort()
    p99 = worst[max(0, round(0.99 * len(worst)) - 1)]
    assert p99 < BUDGET_MS, (
        f"лаг p99 = {p99:.0f} мс перевищив бюджет {BUDGET_MS:.0f} мс "
        f"(вікно W = {WINDOW_MS} мс): read-your-writes більше НЕ гарантований — "
        f"або розшир W, або лікуй реплікацію"
    )
