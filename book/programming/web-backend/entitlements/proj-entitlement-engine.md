# ⚙️ Рушій ентайтлментів: конвеєр резолюції, кешування та облік квот

<preknowlist>
- [Ентайтлменти](topic:programming/entitlements) — комерційні права, булеві шлюзи, статичні ліміти та метричні квоти організації.
- [Черга задач](topic:programming/background-jobs) — асинхронне виконання фонових операцій і доставка подій між сервісами.
- [Ідемпотентність методів](topic:programming/api-idempotency) — збереження стану операцій при повторних викликах.
</preknowlist>

Коли користувач натискає кнопку в інтерфейсі або викликає метод API, сервер має за частки мілісекунди вирішити, чи дозволена ця дія з погляду комерційного контракту. Прямий запит до зовнішньої білінгової системи на кожному HTTP-запиті неприпустимий: мережева затримка стороннього API становить сотні мілісекунд, а будь-яка його недоступність паралізує весь бекенд. Навіть запит до власної реляційної бази даних на кожну операцію створює надлишкове навантаження під час пікового трафіку.

Для швидкого й надійного контролю тарифних можливостей будують автономний **рушій ентайтлментів** (англ. *entitlement engine*). Його завдання — попередньо скомпілювати всі шари комерційного договору організації в незмінний ефективний зліпок, кешувати його в оперативній пам'яті та надати швидкі примітиви для двох типів перевірок: миттєвих булевих шлюзів і потокобезпечного резервування метричних квот.

## Задача та архітектура рушія

Розглянемо платформу, де кожна організація (*tenant*) має комерційні параметри, що складаються з чотирьох незалежних рівнів:

1. **Базовий тарифний план** (наприклад, `free`, `pro`, `enterprise`), який задає стандартний набір увімкнених функцій і початкові ліміти.
2. **Докуповані пакети (Add-ons)**, які розширюють можливості базового плану (наприклад, додаткові місця користувачів або пакет обробки подій).
3. **Індивідуальні винятки контракту (Overrides)**, які менеджер із продажу погодив для конкретного клієнта (наприклад, виділений шлюз або збільшена квота запитів).
4. **Статус підписки та пільговий період**, що тимчасово модифікують доступ у разі невдалого списання коштів із банківської картки.

Рушій має розв'язати три інженерні проблеми:

- **Конвеєр резолюції (Resolution Pipeline):** об'єднати всі чотири рівні за правилами пріоритету й згенерувати єдиний нормалізований зліпок (*Effective Entitlements Snapshot*).
- **Дворівневе кешування з інвалідацією:** тримати зліпок у пам'яті інстансу застосунку (L1) та в розподіленому кеші Redis (L2), забезпечуючи оновлення за мілісекунди при зміні тарифу.
- **Атомарний облік квот (Check-and-Reserve):** для операцій, обмежених лімітом (наприклад, виклики API на місяць чи генерація звітів), перевірити наявність залишку й зарезервувати його без стану гонитви (*race condition*), надаючи механізм повернення квоти у разі збою подальшої обробки.

## Модель даних

Комерційний договір описується типізованими структурами. Розділимо визначення тарифу, доповнень та підсумкового зліпка:

```
[Базовий план] ──┐
[Add-ons]      ──┼─► [Компілятор резолюції] ─► [Ефективний зліпок] ─► [L1 / L2 Кеш]
[Overrides]    ──┤                                                         │
[Статус оплати] ─┘                                                         ▼
                                                                  [Шлюз перевірки]
```

Підсумковий зліпок містить три типи прав:
- `features`: асоціативний масив булевих прапорців (наприклад, `sso: true`, `audit_logs: true`).
- `limits`: статичні структурні ліміти цілочисельного типу (наприклад, `max_projects: 20`, `max_seats: 50`).
- `quotas`: періодичні метричні квоти з визначеним вікном скидання (наприклад, `monthly_api_calls: 500000`).

## Покроковий алгоритм роботи рушія

Робота рушія розбивається на чотири послідовні фази:

### 1. Компіляція та резолюція зліпка

Коли надходить запит на резолюцію для організації `tenant_id`, компілятор завантажує контракт організації та визначення тарифного плану:
1. Клонує базові карти можливостей плану: `features`, `limits`, `quotas`.
2. Послідовно ітерує за списком активних `activeAddonIds`, застосовуючи правила злиття:
   - Для булевих прапорців: логічне об'єднання або явне перевизначення.
   - Для числових лімітів і квот: накопичувальне додавання (`limits[k] += increment`).
3. Накладає персональні контрактні винятки `customFeatureOverrides`, `customLimitOverrides` та `customQuotaOverrides`.
4. Оцінює статус оплати `status`. Якщо статус дорівнює `past_due`, перевіряє поточний час проти `gracePeriodEndsAt`. Якщо пільговий термін вичерпано, виставляє прапорець `isReadOnly = true`.
5. Присвоює монотонну мітку версії на основі `updatedAt.getTime()` і записує результат у локальний кеш інстансу.

### 2. Швидка перевірка булевого права

Виклик `checkFeature(tenantId, featureKey)`:
- Отримує зліпок із локального L1-кешу (якщо запис протух, оновлює з L2/БД).
- Якщо `snapshot.isReadOnly == true`, повертає `false` для всіх операцій модифікації.
- Повертає булеве значення `snapshot.features[featureKey]`. Затримка: менше 0.1 мілісекунди.

### 3. Атомарне резервування квоти (Two-Phase Quota Reservation)

Для метричних операцій виклик `checkAndReserveQuota(tenantId, metricKey, amount)` виконує двофазний протокол:
- **Фаза перевірки та резервування:** виконується атомарний Lua-скрипт у Redis, який порівнює поточний лічильник із лімітом зі зліпка. Якщо квота є, лічильник збільшується на `amount`, і повертається унікальний ідентифікатор транзакції `reservationId`.
- **Фаза фіксації або відкату:**
  - Якщо обробник бізнес-логіки завершився успішно, резервація вважається підтвердженою.
  - Якщо в процесі виконання сталася помилка (наприклад, помилка бази даних або таймаут мережі), викликається `releaseQuota(tenantId, metricKey, reservationId, amount)`, що атомарно повертає списані одиниці назад у лічильник.

## Робочий код рушія

Нижче наведено повну реалізацію рушія двома мовами — TypeScript та Go. Код містить конвеєр резолюції, кеш-менеджер з підтримкою інвалідації через події, шлюз швидкої перевірки булевих прапорців та атомарний механізм резервування квот.

:::tabs
```ts
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
```
```go
package entitlements

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type FeatureKey string
type MetricKey string

const (
	FeatureSSO               FeatureKey = "sso"
	FeatureCustomDomains     FeatureKey = "custom_domains"
	FeatureAuditLogs         FeatureKey = "audit_logs"
	FeatureAdvancedAnalytics FeatureKey = "advanced_analytics"
	FeatureExportCSV         FeatureKey = "export_csv"

	MetricMonthlyAPICalls MetricKey = "monthly_api_calls"
	MetricStorageBytes    MetricKey = "storage_bytes"
	MetricMonthlyReports  MetricKey = "monthly_reports"
)

type SubscriptionStatus string

const (
	StatusActive   SubscriptionStatus = "active"
	StatusTrialing SubscriptionStatus = "trialing"
	StatusPastDue  SubscriptionStatus = "past_due"
	StatusCanceled SubscriptionStatus = "canceled"
	StatusUnpaid   SubscriptionStatus = "unpaid"
)

type PlanDefinition struct {
	ID       string
	Name     string
	Features map[FeatureKey]bool
	Limits   map[string]int64
	Quotas   map[MetricKey]int64
}

type AddonDefinition struct {
	ID               string
	FeatureOverrides map[FeatureKey]bool
	LimitIncrements  map[string]int64
	QuotaIncrements  map[MetricKey]int64
}

type TenantContract struct {
	TenantID               string
	PlanID                 string
	ActiveAddonIDs         []string
	CustomFeatureOverrides map[FeatureKey]bool
	CustomLimitOverrides   map[string]int64
	CustomQuotaOverrides   map[MetricKey]int64
	Status                 SubscriptionStatus
	GracePeriodEndsAt      *time.Time
	UpdatedAt              time.Time
}

type EffectiveSnapshot struct {
	TenantID   string
	Version    int64
	Features   map[FeatureKey]bool
	Limits     map[string]int64
	Quotas     map[MetricKey]int64
	IsReadOnly bool
	ComputedAt time.Time
}

type QuotaReservationResult struct {
	Allowed       bool
	ReservationID string
	CurrentUsage  int64
	Limit         int64
	Remaining     int64
}

type IContractStore interface {
	GetPlan(ctx context.Context, planID string) (*PlanDefinition, error)
	GetAddon(ctx context.Context, addonID string) (*AddonDefinition, error)
	GetTenantContract(ctx context.Context, tenantID string) (*TenantContract, error)
}

type IQuotaStore interface {
	CheckAndReserve(ctx context.Context, tenantID string, metric MetricKey, amount, limit int64, windowSec int) (bool, int64, string, error)
	Release(ctx context.Context, tenantID string, metric MetricKey, reservationID string, amount int64) error
	GetUsage(ctx context.Context, tenantID string, metric MetricKey) (int64, error)
}

type cacheEntry struct {
	snapshot  *EffectiveSnapshot
	expiresAt time.Time
}

type EntitlementEngine struct {
	contractStore IContractStore
	quotaStore    IQuotaStore
	l1Cache       map[string]cacheEntry
	mu            sync.RWMutex
	l1TTL         time.Duration
}

func NewEntitlementEngine(cs IContractStore, qs IQuotaStore) *EntitlementEngine {
	return &EntitlementEngine{
		contractStore: cs,
		quotaStore:    qs,
		l1Cache:       make(map[string]cacheEntry),
		l1TTL:         15 * time.Second,
	}
}

func (e *EntitlementEngine) ResolveSnapshot(ctx context.Context, tenantID string) (*EffectiveSnapshot, error) {
	contract, err := e.contractStore.GetTenantContract(ctx, tenantID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch tenant contract: %w", err)
	}
	if contract == nil {
		return e.defaultFreeSnapshot(tenantID), nil
	}

	basePlan, err := e.contractStore.GetPlan(ctx, contract.PlanID)
	if err != nil || basePlan == nil {
		return nil, fmt.Errorf("base plan not found: %s", contract.PlanID)
	}

	features := make(map[FeatureKey]bool)
	for k, v := range basePlan.Features {
		features[k] = v
	}
	limits := make(map[string]int64)
	for k, v := range basePlan.Limits {
		limits[k] = v
	}
	quotas := make(map[MetricKey]int64)
	for k, v := range basePlan.Quotas {
		quotas[k] = v
	}

	// 2. Накладання докупованих пакетів (Addons)
	for _, addonID := range contract.ActiveAddonIDs {
		addon, err := e.contractStore.GetAddon(ctx, addonID)
		if err != nil || addon == nil {
			continue
		}
		for k, v := range addon.FeatureOverrides {
			features[k] = v
		}
		for k, v := range addon.LimitIncrements {
			limits[k] += v
		}
		for k, v := range addon.QuotaIncrements {
			quotas[k] += v
		}
	}

	// 3. Накладання індивідуальних винятків (Overrides)
	for k, v := range contract.CustomFeatureOverrides {
		features[k] = v
	}
	for k, v := range contract.CustomLimitOverrides {
		limits[k] = v
	}
	for k, v := range contract.CustomQuotaOverrides {
		quotas[k] = v
	}

	// 4. Перевірка платіжного статусу
	now := time.Now()
	isReadOnly := false
	if contract.Status == StatusPastDue {
		if contract.GracePeriodEndsAt == nil || contract.GracePeriodEndsAt.Before(now) {
			isReadOnly = true
		}
	} else if contract.Status == StatusCanceled || contract.Status == StatusUnpaid {
		isReadOnly = true
	}

	snapshot := &EffectiveSnapshot{
		TenantID:   tenantID,
		Version:    contract.UpdatedAt.UnixNano(),
		Features:   features,
		Limits:     limits,
		Quotas:     quotas,
		IsReadOnly: isReadOnly,
		ComputedAt: now,
	}

	e.mu.Lock()
	e.l1Cache[tenantID] = cacheEntry{
		snapshot:  snapshot,
		expiresAt: now.Add(e.l1TTL),
	}
	e.mu.Unlock()

	return snapshot, nil
}

func (e *EntitlementEngine) GetEffectiveSnapshot(ctx context.Context, tenantID string) (*EffectiveSnapshot, error) {
	e.mu.RLock()
	entry, found := e.l1Cache[tenantID]
	e.mu.RUnlock()

	if found && time.Now().Before(entry.expiresAt) {
		return entry.snapshot, nil
	}
	return e.ResolveSnapshot(ctx, tenantID)
}

func (e *EntitlementEngine) InvalidateCache(tenantID string) {
	e.mu.Lock()
	delete(e.l1Cache, tenantID)
	e.mu.Unlock()
}

func (e *EntitlementEngine) CheckFeature(ctx context.Context, tenantID string, feature FeatureKey) (bool, error) {
	snap, err := e.GetEffectiveSnapshot(ctx, tenantID)
	if err != nil {
		return false, err
	}
	if snap.IsReadOnly {
		return false, nil
	}
	return snap.Features[feature], nil
}

func (e *EntitlementEngine) CheckAndReserveQuota(
	ctx context.Context,
	tenantID string,
	metric MetricKey,
	amount int64,
	windowSec int,
) (*QuotaReservationResult, error) {
	snap, err := e.GetEffectiveSnapshot(ctx, tenantID)
	if err != nil {
		return nil, err
	}
	if snap.IsReadOnly {
		return &QuotaReservationResult{Allowed: false}, nil
	}

	limit, exists := snap.Quotas[metric]
	if !exists || limit <= 0 {
		return &QuotaReservationResult{Allowed: false, Limit: 0}, nil
	}

	allowed, newUsage, resID, err := e.quotaStore.CheckAndReserve(ctx, tenantID, metric, amount, limit, windowSec)
	if err != nil {
		return nil, err
	}

	if !allowed {
		return &QuotaReservationResult{
			Allowed:      false,
			CurrentUsage: newUsage,
			Limit:        limit,
			Remaining:    0,
		}, nil
	}

	rem := limit - newUsage
	if rem < 0 {
		rem = 0
	}

	return &QuotaReservationResult{
		Allowed:       true,
		ReservationID: resID,
		CurrentUsage:  newUsage,
		Limit:         limit,
		Remaining:     rem,
	}, nil
}

func (e *EntitlementEngine) ReleaseQuota(ctx context.Context, tenantID string, metric MetricKey, resID string, amount int64) error {
	return e.quotaStore.Release(ctx, tenantID, metric, resID, amount)
}

func (e *EntitlementEngine) defaultFreeSnapshot(tenantID string) *EffectiveSnapshot {
	return &EffectiveSnapshot{
		TenantID: tenantID,
		Version:  1,
		Features: map[FeatureKey]bool{
			FeatureSSO:               false,
			FeatureCustomDomains:     false,
			FeatureAuditLogs:         false,
			FeatureAdvancedAnalytics: false,
			FeatureExportCSV:         true,
		},
		Limits: map[string]int64{
			"max_projects": 3,
			"max_seats":    2,
		},
		Quotas: map[MetricKey]int64{
			MetricMonthlyAPICalls: 1000,
			MetricStorageBytes:    100 * 1024 * 1024,
			MetricMonthlyReports:  5,
		},
		IsReadOnly: false,
		ComputedAt: time.Now(),
	}
}
```
:::

## Детальний розбір реалізації мовами TypeScript та Go

Порівняння реалізацій демонструє кілька важливих архітектурних нюансів керування пам'яттю та паралелізмом у різних середовищах виконання:

1. **Керування локальним кешем L1:**
   - У **TypeScript** середовище Node.js працює в однопотоковому циклі подій (*Event Loop*), тому доступ до структури `Map` не вимагає м'ютексів. Для керування терміном життя записів зберігається абсолютна мітка часу `expiresAt`, яка порівнюється з `Date.now()` при читанні.
   - У **Go** інстанс веб-сервера обробляє тисячі паралельних горутин одночасно. Спільний доступ до карти `l1Cache` захищається м'ютексом `sync.RWMutex`. Читання кешу використовує легке блокування `mu.RLock()`, що дозволяє сотням горутин одночасно перевіряти права без очікування, а запис та інвалідація захоплюють ексклюзивне блокування `mu.Lock()`.

2. **Обробка відсутності контракту (Graceful Defaulting):**
   - Метод `buildDefaultFreeSnapshot` (або `defaultFreeSnapshot` у Go) гарантує, що навіть за повної відсутності запису в базі даних або при створенні нового акаунта система не падає з винятком `NullPointerException`, а автоматично надає безпечний мінімальний набір прав безкоштовного тарифу.

3. **Незмінність об'єкта зліпка:**
   - Метод `ResolveSnapshot` створює абсолютно новий екземпляр `EffectiveSnapshot` і замінює посилання в кеші атомарно. Жодна інша горутина, яка в цей момент тримає вказівник на попередній зліпок, не зазнає пошкодження даних під час читання (*Data Race*).

## Атомарне резервування квот у Redis (Lua-скрипт)

Метрична квота не може перевірятися двома послідовними командами «прочитай лічильник» та «збільш лічильник»: за високої конкурентності паралельні запити одночасно прочитають однакове залишене значення й перевищать ліміт (*Time-of-Check to Time-of-Use*, TOCTOU).

Щоб перевірка та списання виконувалися неподільно, використовують Lua-скрипт у Redis:

```lua
-- KEYS[1] = назва ключа лічильника, наприклад "quota:org_982:monthly_api_calls:2026-08"
-- ARGV[1] = запитувана кількість (amount)
-- ARGV[2] = максимальний ліміт (limit)
-- ARGV[3] = TTL вікна в секундах (windowSec)

local current = redis.call('GET', KEYS[1])
local usage = 0
if current then
    usage = tonumber(current)
end

local requested = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])

if usage + requested > limit then
    -- Перевищення ліміту: повертаємо 0 (заборонено) і поточне значення
    return {0, usage}
else
    -- Ліміт не вичерпано: збільшуємо лічильник атомарно
    local new_val = redis.call('INCRBY', KEYS[1], requested)
    if not current then
        redis.call('EXPIRE', KEYS[1], tonumber(ARGV[3]))
    end
    return {1, new_val}
end
```

Цей скрипт гарантує, що операція `check-and-reserve` виконується на рівні ядра Redis як єдина неподільна транзакція. Час виконання становить менше 1 мілісекунди.

### Робота в кластерному середовищі Redis (Hash Tags)

У розподілених кластерах Redis (Redis Cluster) ключі розподіляються між різними шардами (слотами хешування). Якщо Lua-скрипт або мульти-команда звертається до кількох ключів, усі вони обов'язково повинні належати одному слоту, інакше Redis поверне помилку `CROSSSLOT Keys in request don't hash to the same slot`.

Щоб гарантувати розміщення всіх лічильників та блокувань конкретної організації на одному шарді кластера, у назві ключів застосовують фігурні дужки (*Hash Tags*):

```
quota:{org_982bca10}:monthly_api_calls:2026-08
lock:{org_982bca10}:singleflight
```

Redis обчислює хеш-слот виключно за рядком усередині дужок `{org_982bca10}`, забезпечуючи локальність даних і безпечне виконання скриптів.

## Вбудовування в HTTP-конвеєр (Middleware Guard)

Розглянемо, як рушій інтегрується в HTTP-сервер для автоматичного захисту маршрутів:

```ts
import { Request, Response, NextFunction } from "express";
import { EntitlementEngine, FeatureKey } from "./entitlement-engine";

export function requireFeature(engine: EntitlementEngine, feature: FeatureKey) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const tenantId = req.headers["x-tenant-id"] as string;
    if (!tenantId) {
      return res.status(401).json({ error: "Missing tenant identification" });
    }

    const allowed = await engine.checkFeature(tenantId, feature);
    if (!allowed) {
      return res.status(403).json({
        type: "https://api.example.com/errors/feature-gated",
        title: "Feature Gated by Subscription",
        status: 403,
        detail: `The feature '${feature}' is not included in your active subscription tier.`,
        code: "feature_gated",
        feature,
      });
    }

    next();
  };
}
```

Коли клієнт звертається до захищеного ендпоінта `POST /api/v1/export/audit-logs`, проміжний шар перевіряє право за частки мікросекунди з локального L1-кешу. Якщо тариф не дозволяє цю операцію, запит відсікається ще до виконання важкого коду бази даних.

## Захист від лавини запитів: патерн Single-Flight

Коли тисячі паралельних клієнтів надсилають запити для однієї організації в момент інвалідації кешу, виникає небезпека «ефекту собачої зграї» (*Cache Stampede*).

Для запобігання дублюванню важких обчислень компіляції використовують механізм дедуплікації запитів (*Single-Flight*):

```go
type Call struct {
	wg  sync.WaitGroup
	val *EffectiveSnapshot
	err error
}

type Group struct {
	mu sync.Mutex
	m  map[string]*Call
}

func (g *Group) Do(key string, fn func() (*EffectiveSnapshot, error)) (*EffectiveSnapshot, error) {
	g.mu.Lock()
	if g.m == nil {
		g.m = make(map[string]*Call)
	}
	if c, ok := g.m[key]; ok {
		g.mu.Unlock()
		c.wg.Wait()
		return c.val, c.err
	}
	c := new(Call)
	c.wg.Add(1)
	g.m[key] = c
	g.mu.Unlock()

	c.val, c.err = fn()
	c.wg.Done()

	g.mu.Lock()
	delete(g.m, key)
	g.mu.Unlock()

	return c.val, c.err
}
```

Завдяки структурі `Group`, перший запит ініціює виклик `fn()`, а решта 999 паралельних горутин просто блокуються на `c.wg.Wait()`, отримуючи готовий результат першого обчислення без жодного додаткового запиту до бази даних.

## Тестування конкурентності та інваріантів

Надійність рушія перевіряють багатопотоковими тестами, які емулюють агресивну конкуренцію за залишок квоти:

```go
func TestConcurrentQuotaReservation(t *testing.T) {
	// Ліміт квоти — рівно 10 одиниць
	limit := int64(10)
	var successfulReservations int64

	var wg sync.WaitGroup
	workers := 50 // 50 паралельних запитів одночасно

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			res, err := engine.CheckAndReserveQuota(ctx, "org_test", MetricMonthlyAPICalls, 1, 3600)
			if err == nil && res.Allowed {
				atomic.AddInt64(&successfulReservations, 1)
			}
		}()
	}
	wg.Wait()

	if successfulReservations != limit {
		t.Fatalf("Expected exactly %d successful reservations, got %d (overselling defect!)", limit, successfulReservations)
	}
}
```

Цей тест доводить, що за будь-якої кількості паралельних запитів система гарантує суворе дотримання комерційного ліміту без жодного овербукінгу чи стану гонитви.

## Спостережуваність та метрики продуктивності

Для моніторингу працездатності рушія в системі збору метрик (Prometheus) реєструють чотири ключові лічильники:

```
# Загальна кількість перевірок за функціями та результатами
entitlement_evaluations_total{feature="sso", result="allowed"}
entitlement_evaluations_total{feature="sso", result="denied"}

# Ефективність кешування L1 та L2
entitlement_cache_hits_total{layer="l1"}
entitlement_cache_misses_total{layer="l1"}

# Кількість спроб резервування та вичерпань квот
entitlement_quota_reservations_total{metric="monthly_api_calls", status="success"}
entitlement_quota_reservations_total{metric="monthly_api_calls", status="exhausted"}
```

Моніторинг співвідношення `cache_hits / (cache_hits + cache_misses)` дозволяє переконатися, що відсоток влучань у локальний кеш перевищує 99.5%, гарантуючи мінімальну затримку обробки запитів.

## Пастки та крайові випадки

1. **Лавина запитів при інвалідації кешу (*Cache Stampede / Dog-piling*):** коли клієнт оновлює тариф або докуповує пакети, платіжний сервіс публікує подію інвалідації кешу. Якщо в цей момент на сервер надходять сотні одночасних запитів від користувачів цієї організації, усі вони виявлять відсутність зліпка в кеші й одночасно кинуться перераховувати його в реляційній базі даних. Для захисту від цієї проблеми застосовують блокування злиття запитів (*Single-Flight pattern*), коли лише один потік виконує `resolveSnapshot`, а решта паралельних потоків очікує завершення його роботи й використовує вже скомпільований результат.
2. **Падіння інфраструктури лічильників (*Redis Failure Modes*):** якщо кластер Redis тимчасово недоступний через мережеве розбиття (*network partition*) чи перезапуск, рушій повинен мати наперед визначену політику деградації:
   - Для критичних операцій читання — *fail-open* (пропустити запит, зафіксувавши системне попередження в логах і метриках).
   - Для високовитратних або лінійних платних послуг (наприклад, виклик платної LLM чи відправка платних SMS) — *fail-closed* або тимчасова буферизація запитів у черзі з поверненням клієнту статусу `202 Accepted`.
3. **Компенсаційні транзакції при збоях downstream-сервісів:** якщо квоту було успішно зарезервовано, але під час виконання бізнес-обробника сталася фатальна помилка (наприклад, сторонній сервіс відхилив запит або база даних повернула таймаут транзакції), викликається метод `releaseQuota`. Це запобігає «згорянню» платних одиниць клієнта через внутрішні збої інфраструктури постачальника.
4. **Різниця часових поясів при скиданні розрахункових періодів:** ключі лічильників у Redis формуються з урахуванням року та місяця. Якщо дата скидання рахується за локальним часом клієнта замість фіксованого стандарту UTC, можуть виникати розбіжності між фактичним білінговим циклом інвойсу та інтервалом лічильника квоти. Усі ключі лічильників повинні формуватися суворо за часовим поясом UTC.
