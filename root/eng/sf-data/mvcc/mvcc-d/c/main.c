#include <stdint.h>
#include <stdbool.h>

typedef uint32_t TransactionId;

typedef struct {
    TransactionId xmin;
    TransactionId xmax;
    TransactionId *xip_list;
    uint32_t xip_count;
} Snapshot;

typedef struct {
    TransactionId t_xmin;
    TransactionId t_xmax;
    uint16_t t_infomask;
} HeapTupleHeader;

bool HeapTupleSatisfiesSnapshot(HeapTupleHeader *tuple, Snapshot *snap, TransactionId current_xid) {
    // 1. Якщо кортеж створено нашою ж транзакцією — він видимий
    if (tuple->t_xmin == current_xid) {
        if (tuple->t_xmax == current_xid) return false; // Ми ж його і видалили
        return true;
    }

    // 2. Якщо транзакція-творець з майбутнього або ще активна — кортеж невидимий
    if (tuple->t_xmin >= snap->xmax) return false;
    for (uint32_t i = 0; i < snap->xip_count; ++i) {
        if (tuple->t_xmin == snap->xip_list[i]) return false;
    }

    // 3. Перевірка видалення кортежу (t_xmax)
    if (tuple->t_xmax == 0) return true; // Рядок ніхто не видаляв
    if (tuple->t_xmax == current_xid) return false; // Видалено нами
    if (tuple->t_xmax >= snap->xmax) return true; // Видалення відбулося в майбутньому

    for (uint32_t i = 0; i < snap->xip_count; ++i) {
        if (tuple->t_xmax == snap->xip_list[i]) return true; // Видалення ще не зафіксовано
    }

    // Якщо видалення зафіксовано в минулому — кортеж для нас мертвий
    return false;
}
