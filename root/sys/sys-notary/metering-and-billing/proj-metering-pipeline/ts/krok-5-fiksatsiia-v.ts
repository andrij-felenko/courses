export interface LedgerEntry {
  transactionId: string;
  accountId: string;
  accountType: "asset" | "liability" | "revenue" | "expense";
  amountMicros: bigint;
  referenceId: string;
  createdAt: Date;
}

export class DoubleEntryLedger {
  private entries: LedgerEntry[] = [];

  public recordUsageCharge(
    transactionId: string,
    tenantId: string,
    amountMicros: bigint,
    eventRef: string
  ): boolean {
    if (amountMicros <= 0n) return false;

    const liabilityAccount = `liability:${tenantId}`;
    const revenueAccount = "revenue:api_compute";

    // 1. Дебет рахунку депозиту клієнта (-amount)
    this.entries.push({
      transactionId,
      accountId: liabilityAccount,
      accountType: "liability",
      amountMicros: -amountMicros,
      referenceId: eventRef,
      createdAt: new Date(),
    });

    // 2. Кредит доходу платформи (+amount)
    this.entries.push({
      transactionId,
      accountId: revenueAccount,
      accountType: "revenue",
      amountMicros: amountMicros,
      referenceId: eventRef,
      createdAt: new Date(),
    });

    return true;
  }

  public getAccountBalance(accountId: string): bigint {
    return this.entries
      .filter((e) => e.accountId === accountId)
      .reduce((sum, e) => sum + e.amountMicros, 0n);
  }

  public verifyAuditInvariant(): boolean {
    const totalSum = this.entries.reduce((sum, e) => sum + e.amountMicros, 0n);
    return totalSum === 0n;
  }
}
