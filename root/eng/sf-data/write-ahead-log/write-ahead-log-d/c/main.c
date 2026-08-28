#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

typedef uint64_t LSN;

typedef struct {
    LSN lsn;
    LSN prev_lsn;
    LSN undo_next_lsn;
    uint32_t xid;
    uint32_t type;
    uint32_t page_id;
    int32_t new_val;
} WalRecord;

void aries_redo_scan(WalRecord *log, size_t count, int32_t *pages, LSN *page_lsns) {
    for (size_t i = 0; i < count; ++i) {
        WalRecord *rec = &log[i];
        // Перевірка ідемпотентності: застосовуємо лише якщо LSN запису новіший за PageLSN
        if (rec->lsn > page_lsns[rec->page_id]) {
            pages[rec->page_id] = rec->new_val;
            page_lsns[rec->page_id] = rec->lsn;
            printf("Redo: застосовано LSN %llu до сторінки %u\n", (unsigned long long)rec->lsn, rec->page_id);
        }
    }
}
