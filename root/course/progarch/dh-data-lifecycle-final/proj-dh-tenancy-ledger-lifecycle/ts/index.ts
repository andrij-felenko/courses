// TypeScript Implementation: Multi-Tenant LifeCycle & Ledger Controller

export interface TenantContext {
  readonly tenantId: string;
  readonly planTier: 'FREE' | 'PRO' | 'ENTERPRISE';
  readonly traceId: string;
}

export interface LedgerEntry {
  readonly id: string;
  readonly tenantId: string;
  readonly idempotencyKey: string;
  readonly debitAccount: string;
  readonly creditAccount: string;
  readonly amountCents: bigint; // Захист від floating point
  readonly createdAt: Date;
}

export interface TelemetryBatch {
  readonly homeId: string;
  readonly eventCount: number;
  readonly payloadSizeBytes: number;
  readonly windowStart: Date;
  readonly windowEnd: Date;
}

export class DoubleEntryLedger {
  private readonly entries: LedgerEntry[] = [];
  private readonly idempotencyMap = new Set<string>();

  public postTransaction(
    ctx: TenantContext,
    idempotencyKey: string,
    debitAccount: string,
    creditAccount: string,
    amountCents: bigint
  ): LedgerEntry {
    if (amountCents <= 0n) {
      throw new Error(`Invalid transaction amount: ${amountCents}`);
    }

    const fullKey = `${ctx.tenantId}:${idempotencyKey}`;
    if (this.idempotencyMap.has(fullKey)) {
      const existing = this.entries.find((e) => e.idempotencyKey === fullKey);
      if (existing) return existing;
      throw new Error(`Idempotency key conflict: ${fullKey}`);
    }

    const entry: LedgerEntry = {
      id: `ldg_${Math.random().toString(36).substring(2, 10)}`,
      tenantId: ctx.tenantId,
      idempotencyKey: fullKey,
      debitAccount,
      creditAccount,
      amountCents,
      createdAt: new Date(),
    };

    this.entries.push(entry);
    this.idempotencyMap.add(fullKey);
    return entry;
  }

  public getBalance(tenantId: string, account: string): bigint {
    let balance = 0n;
    for (const entry of this.entries) {
      if (entry.tenantId !== tenantId) continue;
      if (entry.debitAccount === account) balance += entry.amountCents;
      if (entry.creditAccount === account) balance -= entry.amountCents;
    }
    return balance;
  }

  public auditCheck(): { totalDebit: bigint; totalCredit: bigint; isBalanced: boolean } {
    let totalDebit = 0n;
    let totalCredit = 0n;
    for (const entry of this.entries) {
      totalDebit += entry.amountCents;
      totalCredit += entry.amountCents;
    }
    return {
      totalDebit,
      totalCredit,
      isBalanced: totalDebit === totalCredit,
    };
  }
}

export class MeteringEngine {
  constructor(private readonly ledger: DoubleEntryLedger) {}

  public processTelemetry(ctx: TenantContext, batch: TelemetryBatch): bigint {
    // Тарифікація: 1 цент за кожні 10 000 подій
    const ratePer10k = 1n;
    const billableUnits = BigInt(Math.floor(batch.eventCount / 10000));
    const costCents = billableUnits * ratePer10k;

    if (costCents > 0n) {
      const idempotencyKey = `meter_${batch.homeId}_${batch.windowStart.getTime()}`;
      this.ledger.postTransaction(
        ctx,
        idempotencyKey,
        `tenant:${ctx.tenantId}:unbilled_usage`,
        `system:revenue:telemetry`,
        costCents
      );
    }

    return costCents;
  }
}

export class TenantDecommissioner {
  private readonly tombstonedTenants = new Map<string, Date>();
  private readonly destroyedKmsKeys = new Set<string>();

  constructor(private readonly ledger: DoubleEntryLedger) {}

  public executeDecommissionCascade(ctx: TenantContext): {
    finalBalanceCents: bigint;
    tombstoneTime: Date;
    kmsShredded: boolean;
  } {
    // 1. Фінальний розрахунок балансу
    const unbilled = this.ledger.getBalance(
      ctx.tenantId,
      `tenant:${ctx.tenantId}:unbilled_usage`
    );

    if (unbilled > 0n) {
      // Перенос з unbilled в остаточний дебіторський рахунок
      this.ledger.postTransaction(
        ctx,
        `decom_settle_${Date.now()}`,
        `tenant:${ctx.tenantId}:ar_final`,
        `tenant:${ctx.tenantId}:unbilled_usage`,
        unbilled
      );
    }

    // 2. Встановлення надгробка (Tombstone)
    const tombstoneTime = new Date();
    this.tombstonedTenants.set(ctx.tenantId, tombstoneTime);

    // 3. Crypto-shredding (знищення KMS ключа шифрування архівних бакетів S3)
    const kmsKeyId = `kms-key-${ctx.tenantId}`;
    this.destroyedKmsKeys.add(kmsKeyId);

    return {
      finalBalanceCents: unbilled,
      tombstoneTime,
      kmsShredded: true,
    };
  }

  public isTenantActive(tenantId: string): boolean {
    return !this.tombstonedTenants.has(tenantId);
  }
}
