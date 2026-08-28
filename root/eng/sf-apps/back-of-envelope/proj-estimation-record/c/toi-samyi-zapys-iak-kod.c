#include <stdint.h>
#include <stdio.h>

// ── Припущення оцінки — КОЖНЕ поле з одиницею й походженням ────────────
// Це і є «записані припущення»: щоб перерахувати, міняють ТУТ один рядок.
typedef struct {
    uint64_t records;       // шт     — скільки записів в індексі
    uint32_t key_bytes;     // Б      — розмір ключа (UUID/хеш за схемою)
    uint32_t ptr_bytes;     // Б      — розмір покажчика на запис (64-біт)
    uint32_t overhead_num;  // —      — накладні структури, чисельник…
    uint32_t overhead_den;  // —      … і знаменник: ×(num/den), напр. ×2 = 2/1
} IndexAssumptions;

// ── Розклад: з припущень → число (у байтах). Чиста, без побічних дій. ──
static uint64_t index_size_bytes(IndexAssumptions a) {
    uint64_t per_entry = (uint64_t)a.key_bytes + a.ptr_bytes;   // Б на запис
    uint64_t raw       = a.records * per_entry;                 // Б без накладних
    // множимо ДО ділення, щоб не втратити точність на цілих:
    return raw * a.overhead_num / a.overhead_den;               // Б з накладними
}
