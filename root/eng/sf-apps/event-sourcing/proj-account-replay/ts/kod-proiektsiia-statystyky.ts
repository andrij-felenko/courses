// Похідна модель, якої НЕ було на старті. Свій акумулятор, своя згортка.
interface DepositStats {
  depositCount: number;
  depositTotal: number;
  feeCount: number;
}
const STATS_ZERO: DepositStats = { depositCount: 0, depositTotal: 0, feeCount: 0 };

// applyStats — інша згортка того самого потоку подій.
function applyStats(s: DepositStats, e: AccountEvent): DepositStats {
  switch (e.kind) {
    case "Deposited":
      return { ...s, depositCount: s.depositCount + 1,
                     depositTotal: s.depositTotal + e.amount };
    case "FeeCharged":
      return { ...s, feeCount: s.feeCount + 1 };
    case "Withdrawn":
      return s;                       // цю проєкцію зняття не цікавлять — пропускаємо
  }
}

// Побудувати проєкцію ЗАДНІМ ЧИСЛОМ: прогнати applyStats по всьому журналу з минулого.
function buildDepositStats(store: EventStore, streamId: string): DepositStats {
  return store.read(streamId).reduce((s, st) => applyStats(s, st.event), STATS_ZERO);
}

// Похідна метрика: середнє поповнення = сума / кількість.
function averageDeposit(stats: DepositStats): number {
  return stats.depositCount === 0 ? 0 : stats.depositTotal / stats.depositCount;
}
