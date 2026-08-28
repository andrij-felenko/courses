# Похідна модель, якої НЕ було на старті. Свій акумулятор, своя згортка.
@dataclass(frozen=True)
class DepositStats:
    deposit_count: int = 0
    deposit_total: float = 0.0
    fee_count: int = 0

# apply_stats — інша згортка того самого потоку подій.
def apply_stats(s: DepositStats, e) -> DepositStats:
    if isinstance(e, Deposited):
        return DepositStats(s.deposit_count + 1, s.deposit_total + e.amount, s.fee_count)
    if isinstance(e, FeeCharged):
        return DepositStats(s.deposit_count, s.deposit_total, s.fee_count + 1)
    return s                          # зняття цю проєкцію не цікавлять — пропускаємо

# Побудувати проєкцію ЗАДНІМ ЧИСЛОМ: прогнати apply_stats по всьому журналу з минулого.
def build_deposit_stats(store: EventStore, stream_id: str) -> DepositStats:
    stats = DepositStats()
    for st in store.read(stream_id):
        stats = apply_stats(stats, st.event)
    return stats

# Похідна метрика: середнє поповнення = сума / кількість.
def average_deposit(stats: DepositStats) -> float:
    return 0.0 if stats.deposit_count == 0 else stats.deposit_total / stats.deposit_count
