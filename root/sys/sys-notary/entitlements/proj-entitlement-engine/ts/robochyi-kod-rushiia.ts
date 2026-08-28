// ── Типи та моделі даних ───────────────────────────────────────────────────

export type FeatureKey = "sso" | "custom_domains" | "audit_logs" | "advanced_analytics" | "export_csv";
export type MetricKey = "monthly_api_calls" | "storage_bytes" | "monthly_reports";

export type PlanDefinition = {
  id: string;
  name: string;
  features: Record<FeatureKey, boolean>;
  limits: Record<string, number>;
  quotas: Record<MetricKey, number>;
};

export type AddonDefinition = {
  id: string;
  featureOverrides?: Partial<Record<FeatureKey, boolean>>;
  limitIncrements?: Record<string, number>;
  quotaIncrements?: Partial<Record<MetricKey, number>>;
};

export type SubscriptionStatus = "active" | "trialing" | "past_due" | "canceled" | "unpaid";

export type TenantContract = {
  tenantId: string;
  planId: string;
  activeAddonIds: string[];
  customFeatureOverrides: Partial<Record<FeatureKey, boolean>>;
  customLimitOverrides: Record<string, number>;
  customQuotaOverrides: Partial<Record<MetricKey, number>>;
  status: SubscriptionStatus;
  gracePeriodEndsAt?: Date;
  updatedAt: Date;
};

export type EffectiveSnapshot = {
  tenantId: string;
  version: number;
  features: Record<FeatureKey, boolean>;
  limits: Record<string, number>;
  quotas: Record<MetricKey, number>;
  isReadOnly: boolean;
  computedAt: number;
};

export type QuotaReservationResult = {
  allowed: boolean;
  reservationId?: string;
  currentUsage: number;
  limit: number;
  remaining: number;
};

// ── Сховища планів і контрактів ────────────────────────────────────────────

export interface IContractStore {
  getPlan(planId: string): Promise<PlanDefinition | null>;
  getAddon(addonId: string): Promise<AddonDefinition | null>;
  getTenantContract(tenantId: string): Promise<TenantContract | null>;
}

export interface IQuotaStore {
  /** Атомарно перевіряє ліміт і резервує одиниці квоти за період */
  checkAndReserve(
    tenantId: string,
    metric: MetricKey,
    amount: number,
    limit: number,
    windowSec: number
  ): Promise<{ allowed: boolean; newUsage: number; reservationId: string }>;

  /** Повертає зарезервовану квоту в разі аварії бізнес-логіки */
  release(tenantId: string, metric: MetricKey, reservationId: string, amount: number): Promise<void>;

  /** Отримує поточне використання */
  getUsage(tenantId: string, metric: MetricKey): Promise<number>;
}

// ── Конвеєр резолюції та рушій перевірки ────────────────────────────────────

export class EntitlementEngine {
  private l1Cache = new Map<string, { snapshot: EffectiveSnapshot; expiresAt: number }>();
  private readonly l1TtlMs = 15_000; // 15 секунд для локального кешу інстансу

  constructor(
    private readonly contractStore: IContractStore,
    private readonly quotaStore: IQuotaStore
  ) {}

  /**
   * Компілює комерційний контракт організації в ефективний незмінний зліпок.
   */
  async resolveSnapshot(tenantId: string): Promise<EffectiveSnapshot> {
    const contract = await this.contractStore.getTenantContract(tenantId);
    if (!contract) {
      // Контракт відсутній — повертаємо базовий безкоштовний зліпок за замовчуванням
      return this.buildDefaultFreeSnapshot(tenantId);
    }

    const basePlan = await this.contractStore.getPlan(contract.planId);
    if (!basePlan) {
      throw new Error(`Plan definition not found: ${contract.planId}`);
    }

    // 1. Початкові значення з базового тарифу
    const features: Record<FeatureKey, boolean> = { ...basePlan.features };
    const limits: Record<string, number> = { ...basePlan.limits };
    const quotas: Record<MetricKey, number> = { ...basePlan.quotas };

    // 2. Накладання докупованих пакетів (Add-ons)
    for (const addonId of contract.activeAddonIds) {
      const addon = await this.contractStore.getAddon(addonId);
      if (!addon) continue;

      if (addon.featureOverrides) {
        for (const [k, v] of Object.entries(addon.featureOverrides)) {
          if (v !== undefined) features[k as FeatureKey] = v;
        }
      }
      if (addon.limitIncrements) {
        for (const [k, v] of Object.entries(addon.limitIncrements)) {
          limits[k] = (limits[k] || 0) + v;
        }
      }
      if (addon.quotaIncrements) {
        for (const [k, v] of Object.entries(addon.quotaIncrements)) {
          if (v !== undefined) quotas[k as MetricKey] = (quotas[k as MetricKey] || 0) + v;
        }
      }
    }

    // 3. Накладання індивідуальних винятків (Overrides)
    for (const [k, v] of Object.entries(contract.customFeatureOverrides)) {
      if (v !== undefined) features[k as FeatureKey] = v;
    }
    for (const [k, v] of Object.entries(contract.customLimitOverrides)) {
      limits[k] = v;
    }
    for (const [k, v] of Object.entries(contract.customQuotaOverrides)) {
      if (v !== undefined) quotas[k as MetricKey] = v;
    }

    // 4. Оцінка платіжного статусу (Dunning & Grace period)
    const now = new Date();
    let isReadOnly = false;

    if (contract.status === "past_due") {
      const inGrace = contract.gracePeriodEndsAt && contract.gracePeriodEndsAt > now;
      if (!inGrace) {
        // Пільговий період минув — переводимо в режим тільки читання
        isReadOnly = true;
      }
    } else if (contract.status === "canceled" || contract.status === "unpaid") {
      isReadOnly = true;
    }

    const snapshot: EffectiveSnapshot = {
      tenantId,
      version: contract.updatedAt.getTime(),
      features,
      limits,
      quotas,
      isReadOnly,
      computedAt: Date.now(),
    };

    // Зберігаємо в локальний кеш
    this.l1Cache.set(tenantId, {
      snapshot,
      expiresAt: Date.now() + this.l1TtlMs,
    });

    return snapshot;
  }

  /**
   * Отримує ефективний зліпок із кешу L1 або запускає резолюцію.
   */
  async getEffectiveSnapshot(tenantId: string): Promise<EffectiveSnapshot> {
    const cached = this.l1Cache.get(tenantId);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.snapshot;
    }
    return this.resolveSnapshot(tenantId);
  }

  /**
   * Інвалідує кеш для організації при зміні підписки або оплаті.
   */
  invalidateCache(tenantId: string): void {
    this.l1Cache.delete(tenantId);
  }

  /**
   * Швидка перевірка булевого прапорця (< 0.1 мс).
   */
  async checkFeature(tenantId: string, feature: FeatureKey): Promise<boolean> {
    const snapshot = await this.getEffectiveSnapshot(tenantId);
    if (snapshot.isReadOnly) {
      return false;
    }
    return Boolean(snapshot.features[feature]);
  }

  /**
   * Перевірка статичного ліміту під час створення ресурсу.
   */
  async checkStaticLimit(tenantId: string, limitKey: string, currentCount: number): Promise<boolean> {
    const snapshot = await this.getEffectiveSnapshot(tenantId);
    if (snapshot.isReadOnly) {
      return false;
    }
    const maxAllowed = snapshot.limits[limitKey] ?? 0;
    return currentCount < maxAllowed;
  }

  /**
   * Атомарна перевірка та резервування періодичної метричної квоти.
   */
  async checkAndReserveQuota(
    tenantId: string,
    metric: MetricKey,
    amount = 1,
    windowSec = 2592000 // 30 днів
  ): Promise<QuotaReservationResult> {
    const snapshot = await this.getEffectiveSnapshot(tenantId);
    if (snapshot.isReadOnly) {
      return {
        allowed: false,
        currentUsage: 0,
        limit: snapshot.quotas[metric] ?? 0,
        remaining: 0,
      };
    }

    const limit = snapshot.quotas[metric] ?? 0;
    if (limit <= 0) {
      return { allowed: false, currentUsage: 0, limit: 0, remaining: 0 };
    }

    const res = await this.quotaStore.checkAndReserve(tenantId, metric, amount, limit, windowSec);
    if (!res.allowed) {
      return {
        allowed: false,
        currentUsage: res.newUsage,
        limit,
        remaining: 0,
      };
    }

    return {
      allowed: true,
      reservationId: res.reservationId,
      currentUsage: res.newUsage,
      limit,
      remaining: Math.max(0, limit - res.newUsage),
    };
  }

  /**
   * Звільнення зарезервованої квоти при збої бізнес-операції.
   */
  async releaseQuota(tenantId: string, metric: MetricKey, reservationId: string, amount = 1): Promise<void> {
    await this.quotaStore.release(tenantId, metric, reservationId, amount);
  }

  private buildDefaultFreeSnapshot(tenantId: string): EffectiveSnapshot {
    return {
      tenantId,
      version: 1,
      features: {
        sso: false,
        custom_domains: false,
        audit_logs: false,
        advanced_analytics: false,
        export_csv: true,
      },
      limits: { max_projects: 3, max_seats: 2 },
      quotas: { monthly_api_calls: 1000, storage_bytes: 104857600, monthly_reports: 5 },
      isReadOnly: false,
      computedAt: Date.now(),
    };
  }
}
