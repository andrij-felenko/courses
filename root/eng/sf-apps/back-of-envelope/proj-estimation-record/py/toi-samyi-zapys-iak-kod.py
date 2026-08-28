from dataclasses import dataclass

# ── Припущення оцінки — КОЖНЕ поле з одиницею й походженням ────────────
# Це і є «записані припущення»: щоб перерахувати, міняють ТУТ один рядок.
@dataclass
class IndexAssumptions:
    records: int        # шт  — скільки записів в індексі
    key_bytes: int      # Б   — розмір ключа (UUID/хеш за схемою)
    ptr_bytes: int      # Б   — розмір покажчика на запис (64-біт)
    overhead_num: int   # —   — накладні структури, чисельник…
    overhead_den: int   # —   … і знаменник: ×(num/den), напр. ×2 = 2/1

# ── Розклад: з припущень → число (у байтах). Чиста, без побічних дій. ──
def index_size_bytes(a: IndexAssumptions) -> int:
    per_entry = a.key_bytes + a.ptr_bytes   # Б на запис
    raw       = a.records * per_entry        # Б без накладних
    # множимо ДО ділення, щоб не втратити точність на цілих (// — цілочисельне):
    return raw * a.overhead_num // a.overhead_den   # Б з накладними
