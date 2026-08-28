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
