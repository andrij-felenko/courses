export interface ActiveReservation {
  reservationId: string;
  tenantId: string;
  reservedMicros: bigint;
  state: "ACTIVE" | "SETTLED" | "RELEASED";
}

export class CreditQuotaManager {
  private availableBalanceMicros: bigint;
  private lockedHoldMicros: bigint = 0n;
  private reservations = new Map<string, ActiveReservation>();

  constructor(initialBalanceMicros: bigint) {
    this.availableBalanceMicros = initialBalanceMicros;
  }

  // Фаза 1: Резервування ліміту
  public acquireHold(tenantId: string, reservationId: string, estimatedMaxCost: bigint): ActiveReservation | null {
    if (estimatedMaxCost <= 0n || this.availableBalanceMicros < estimatedMaxCost) {
      return null; // Недостатній баланс
    }

    this.availableBalanceMicros -= estimatedMaxCost;
    this.lockedHoldMicros += estimatedMaxCost;

    const res: ActiveReservation = {
      reservationId,
      tenantId,
      reservedMicros: estimatedMaxCost,
      state: "ACTIVE",
    };
    this.reservations.set(reservationId, res);
    return res;
  }

  // Фаза 3а: Фіналізація фактичного споживання
  public settleHold(reservationId: string, actualCost: bigint): boolean {
    const res = this.reservations.get(reservationId);
    if (!res || res.state !== "ACTIVE" || actualCost > res.reservedMicros || actualCost < 0n) {
      return false;
    }

    const unusedFunds = res.reservedMicros - actualCost;
    this.lockedHoldMicros -= res.reservedMicros;
    this.availableBalanceMicros += unusedFunds; // повертаємо здачу
    res.state = "SETTLED";
    return true;
  }

  // Фаза 3б: Скасування в разі збою
  public releaseHold(reservationId: string): void {
    const res = this.reservations.get(reservationId);
    if (!res || res.state !== "ACTIVE") return;

    this.lockedHoldMicros -= res.reservedMicros;
    this.availableBalanceMicros += res.reservedMicros;
    res.state = "RELEASED";
  }

  public getAvailableBalance(): bigint {
    return this.availableBalanceMicros;
  }
}
