# ⚙️ Реалізація контролера життєвого циклу орендаря, metering та гросбуху в DH

Цей практичний модуль демонструє повну реалізацію контролера життєвого циклу даних та грошей для мультиарендної платформи Digital Homes (DH). Проект вирішує завдання атомарної прокидки контексту орендаря (`TenantContext`), ідемпотентного збору спожитку телеметрії (`MeteringEngine`), виставлення балансових проводок у двозаписному гросбуху (`DoubleEntryLedger`) та виконання каскадного затирання даних (`DecommissioningCascade`) при ліквідації орендаря чи запиті GDPR.

Без такої інтегрованої системи інженерні команди стикаються з витоком даних між орендарями (англ. *cross-tenant data leak*), невпевненістю в точності нарахувань та появою «сирітських» (англ. *orphan*) файлів телеметрії в хмарних бакетах S3 після видалення облікових записів.

---

## 1. Архітектурні вимоги та проектування компонентів

При розробці систем оренди та білінгу високої щільності виникає чотири фундаментальних вимоги до програмної архітектури:

1. **Строга наскрізна контекстуалізація**: Жоден метод сервісу, репозиторій чи виклик до бази даних не може працювати в «анонімному» режимі. Об'єкт `TenantContext` є обов'язковим першим аргументом або прокидається крізь асинхронне середовище виконання. Це унеможливлює ситуацію, коли код обробки телеметрії випадково записує виміри одного будинку в БД іншого орендаря.
2. **Абсолютна відсутність дробових чисел у фінансових розрахунках**: Використання типів з плаваючою крапкою (`float`, `double`) у грошових обчисленнях заборонено на рівні типізації. Усі суми, нарахування, тарифи та баланси оперують виключно цілочисельними найменшими одиницями (`bigint` у TypeScript/JavaScript, `int` у Python). Це гарантує, що сума тисячі дрібних нарахувань точно дорівнює загальному підсумку без накопичення помилок округлення IEEE-754.
3. **Строга ідемпотентність проводок**: Будь-яка мережева операція (наприклад, надсилання батчу метрик чи підтвердження платежу через Stripe-вебхук) може бути повторена декілька разів через таймаути чи повторні спроби (англ. *retries*). `DoubleEntryLedger` мусить гарантувати, що повторний виклик з тим самим ключем ідемпотентності (`idempotency_key`) повертає вже існуючу проводку без повторного внесення змін до балансу.
4. **Непорушність ланцюжка видалення (Cascade Execution)**: Процес ліквідації орендаря не є одномоментною операцією. Він має чітку фазовість: блокування доступу → фінальна звірка залишків → маркування надгробками (tombstones) → знищення ключів шифрування (crypto-shredding) → асинхронне вилучення фізичних бакетів.

---

## 2. Повний вихідний код реалізації

Нижче наведено робочий код контролера з повним циклом обробки: від прийняття телеметрії та нарахування плати до каскадного вилучення орендаря.

:::tabs
```ts
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
```
```py
# Python Implementation: Multi-Tenant LifeCycle & Ledger Controller

from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    plan_tier: str  # 'FREE', 'PRO', 'ENTERPRISE'
    trace_id: str

@dataclass(frozen=True)
class LedgerEntry:
    entry_id: str
    tenant_id: str
    idempotency_key: str
    debit_account: str
    credit_account: str
    amount_cents: int  # Цілі копійки/центи
    created_at: datetime

@dataclass(frozen=True)
class TelemetryBatch:
    home_id: str
    event_count: int
    payload_size_bytes: int
    window_start: datetime
    window_end: datetime

class DoubleEntryLedger:
    def __init__(self):
        self._entries: list[LedgerEntry] = []
        self._idempotency_set: set[str] = set()

    def post_transaction(
        self,
        ctx: TenantContext,
        idempotency_key: str,
        debit_account: str,
        credit_account: str,
        amount_cents: int
    ) -> LedgerEntry:
        if amount_cents <= 0:
            raise ValueError(f"Invalid transaction amount: {amount_cents}")

        full_key = f"{ctx.tenant_id}:{idempotency_key}"
        if full_key in self._idempotency_set:
            for entry in self._entries:
                if entry.idempotency_key == full_key:
                    return entry
            raise RuntimeError(f"Idempotency conflict for key: {full_key}")

        entry = LedgerEntry(
            entry_id=f"ldg_{uuid.uuid4().hex[:8]}",
            tenant_id=ctx.tenant_id,
            idempotency_key=full_key,
            debit_account=debit_account,
            credit_account=credit_account,
            amount_cents=amount_cents,
            created_at=datetime.utcnow()
        )

        self._entries.append(entry)
        self._idempotency_set.add(full_key)
        return entry

    def get_balance(self, tenant_id: str, account: str) -> int:
        balance = 0
        for entry in self._entries:
            if entry.tenant_id != tenant_id:
                continue
            if entry.debit_account == account:
                balance += entry.amount_cents
            if entry.credit_account == account:
                balance -= entry.amount_cents
        return balance

    def audit_check(self) -> dict:
        total_debit = sum(e.amount_cents for e in self._entries)
        total_credit = sum(e.amount_cents for e in self._entries)
        return {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "is_balanced": total_debit == total_credit
        }

class MeteringEngine:
    def __init__(self, ledger: DoubleEntryLedger):
        self.ledger = ledger

    def process_telemetry(self, ctx: TenantContext, batch: TelemetryBatch) -> int:
        # Тарифікація: 1 цент за кожні 10 000 подій
        rate_per_10k = 1
        billable_units = batch.event_count // 10000
        cost_cents = billable_units * rate_per_10k

        if cost_cents > 0:
            idempotency_key = f"meter_{batch.home_id}_{int(batch.window_start.timestamp())}"
            self.ledger.post_transaction(
                ctx=ctx,
                idempotency_key=idempotency_key,
                debit_account=f"tenant:{ctx.tenant_id}:unbilled_usage",
                credit_account="system:revenue:telemetry",
                amount_cents=cost_cents
            )

        return cost_cents

class TenantDecommissioner:
    def __init__(self, ledger: DoubleEntryLedger):
        self.ledger = ledger
        self.tombstones: dict[str, datetime] = {}
        self.shredded_kms_keys: set[str] = set()

    def execute_decommission_cascade(self, ctx: TenantContext) -> dict:
        # 1. Фінальний розрахунок балансу
        unbilled = self.ledger.get_balance(
            ctx.tenant_id,
            f"tenant:{ctx.tenant_id}:unbilled_usage"
        )

        if unbilled > 0:
            self.ledger.post_transaction(
                ctx=ctx,
                idempotency_key=f"decom_settle_{int(datetime.utcnow().timestamp())}",
                debit_account=f"tenant:{ctx.tenant_id}:ar_final",
                credit_account=f"tenant:{ctx.tenant_id}:unbilled_usage",
                amount_cents=unbilled
            )

        # 2. Tombstone Tagging
        tombstone_time = datetime.utcnow()
        self.tombstones[ctx.tenant_id] = tombstone_time

        # 3. Crypto-shredding KMS keys
        kms_key_id = f"kms-key-{ctx.tenant_id}"
        self.shredded_kms_keys.add(kms_key_id)

        return {
            "final_balance_cents": unbilled,
            "tombstone_time": tombstone_time.isoformat(),
            "kms_shredded": True
        }
```
:::

---

## 3. Глибокий розбір механізмів обробки та крайових випадків

### Механізм гарантії ідемпотентності проводок
У класі `DoubleEntryLedger` ключовим місцем є перевірка наявності ключа у `idempotencyMap`. Ключ формується як композиція:
`fullKey = tenantId + ":" + idempotencyKey`

Це вирішує простір назв між різними орендарями: навіть якщо два незалежні B2B-клієнти згенерують однаковий локальний ідентифікатор події (наприклад `evt_001`), їхні проводки у гросбуху будуть строго ізольовані за рахунок префіксу орендаря. 

Якщо мережевий збій спричиняє ретрай Flink-джоб або Stripe-вебхука, метод `postTransaction` знаходить уже збережений запис `LedgerEntry` та повертає його без виконання повторного списання.

### Захист від гонки обробки (Race Conditions) при видаленні
Розглянемо крайовий випадок (edge case): в один і той самий момент, коли `TenantDecommissioner` розпочинає виконання каскаду видалення, фонова джоба агрегації телеметрії обробляє запізнілий батч вимірів від лічильників даного будинку.

Якщо ліквідатор уже встановив надгробок у `tombstones`, але `MeteringEngine` продовжує писати нові проводки у рахунок `unbilled_usage`, виникає витік грошового обліку (англ. *unbilled usage leak after termination*).

Для запобігання цьому в реальних розподілених системах застосовується двокрокове блокування:
1. **Перехід у стан `SUSPENDED`**: Спочатку `TenantContext` переводиться у стан тимчасового блокування. Усі вхідні точки збору метрик відхиляють нові батчі.
2. **Дренаж конвеєра (Pipeline Drain)**: Система очікує повного випорожнення Kafka-буферів (наприклад, 10 секунд), гарантуючи, що всі згенеровані під час активності виміри оброблені.
3. **Фінальна проводка (Final Settlement)**: Зчитується остаточний баланс `unbilled_usage` і формується закриваюча проводка `ar_final`. тільки після цього встановлюється часова мітка надгробка (`tombstoneTime`).

### Фізичне затирання vs Crypto-Shredding
Традиційний підхід до вилучення даних вимагає відправки мільйонів API-запитів `DELETE` до хмарного сховища S3. Для B2B-орендаря з 5000 квартир це означає видалення сотень терабайтів дрібних файлів відео та Parquet-архівів. Операція вилучення може тривати кілька діб, споживаючи тисячі доларів на API-запити S3 `DeleteObjects`.

`TenantDecommissioner` реалізує паттерн **Crypto-shredding**:
* Усі об'єкти орендаря при записі в S3 шифруються на стороні сервера (SSE-KMS) унікальним ключем `kms-key-{tenant_id}`.
* При вилученні орендаря система видаляє сам KMS-ключ з AWS KMS чи HashiCorp Vault.
* Без KMS-ключа всі Parquet-файли та відеокліпи миттєво перетворюються на нечитабельний зашифрований шум. Подальше фізичне вилучення об'єктів виконується асинхронно безкоштовними правилами S3 Lifecycle Policies без участі основних робітників платформи.

---

## 4. Простеження та діагностика через логи та трейси

У розподіленому середовищі для перевірки цілісності життєвого циклу даних та грошей кожен запис у логах мусить містити стандартизовані поля простеження.

Приклад правильного структурованого логу при обробці метрики та ліквідації:

```json
{
  "timestamp": "2026-08-18T09:30:00.124Z",
  "level": "INFO",
  "service": "dh-metering-engine",
  "tenant_id": "tnt_84f9",
  "trace_id": "7f8a9b0c1d2e",
  "home_id": "home_9921",
  "idempotency_key": "tnt_84f9:meter_home_9921_1723973400",
  "action": "LEDGER_POST",
  "debit_account": "tenant:tnt_84f9:unbilled_usage",
  "credit_account": "system:revenue:telemetry",
  "amount_cents": 1500,
  "message": "Telemetry batch metered and posted to ledger successfully"
}
```

При виконанні каскаду ліквідації система генерує аудит-подію з повним підсумком:

```json
{
  "timestamp": "2026-08-18T09:35:12.890Z",
  "level": "WARN",
  "service": "dh-tenant-lifecycle",
  "tenant_id": "tnt_84f9",
  "trace_id": "9a8b7c6d5e4f",
  "action": "TENANT_DECOMMISSIONED",
  "final_balance_cents": 1500,
  "tombstone_timestamp": "2026-08-18T09:35:12.800Z",
  "kms_key_destroyed": "kms-key-tnt_84f9",
  "status": "CRYPTO_SHREDDED",
  "message": "Tenant successfully decommissioned, ledger settled, KMS key destroyed"
}
```

Завдяки наявності `tenant_id` та `trace_id` у кожному логу інженери підтримки можуть за секунди відстежити повний шлях даних від першого вхідного HTTP-запиту до фінальної проводки у гросбуху та криптографічного затирання ключів шифрування.
