#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_LOG_RECORDS 512
#define MAX_PAGES 16
#define MAX_TX 32

typedef uint64_t lsn_t;
typedef uint32_t xid_t;

typedef enum {
    LOG_UPDATE = 1,
    LOG_COMMIT = 2,
    LOG_ABORT = 3,
    LOG_CLR = 4
} log_type_t;

typedef struct {
    lsn_t lsn;
    lsn_t prev_lsn;
    lsn_t undo_next_lsn;
    xid_t xid;
    log_type_t type;
    uint32_t page_id;
    int32_t old_val;
    int32_t new_val;
} wal_record_t;

typedef struct {
    uint32_t page_id;
    lsn_t page_lsn;
    int32_t data;
} db_page_t;

typedef struct {
    wal_record_t log[MAX_LOG_RECORDS];
    size_t log_count;
    lsn_t next_lsn;
    lsn_t flushed_lsn;
    db_page_t pages[MAX_PAGES];
    lsn_t last_tx_lsn[MAX_TX];
} wal_engine_t;

wal_engine_t* wal_engine_create(void) {
    wal_engine_t *eng = (wal_engine_t*)calloc(1, sizeof(wal_engine_t));
    eng->next_lsn = 100;
    for (uint32_t i = 0; i < MAX_PAGES; ++i) {
        eng->pages[i].page_id = i;
        eng->pages[i].page_lsn = 0;
        eng->pages[i].data = 0;
    }
    return eng;
}

void wal_engine_destroy(wal_engine_t *eng) {
    if (eng) free(eng);
}

lsn_t wal_append(wal_engine_t *eng, xid_t xid, log_type_t type, uint32_t page_id, int32_t old_v, int32_t new_v, lsn_t undo_next) {
    lsn_t lsn = eng->next_lsn++;
    wal_record_t *rec = &eng->log[eng->log_count++];
    rec->lsn = lsn;
    rec->prev_lsn = eng->last_tx_lsn[xid % MAX_TX];
    rec->undo_next_lsn = undo_next;
    rec->xid = xid;
    rec->type = type;
    rec->page_id = page_id;
    rec->old_val = old_v;
    rec->new_val = new_v;

    eng->last_tx_lsn[xid % MAX_TX] = lsn;
    return lsn;
}

void wal_flush(wal_engine_t *eng, lsn_t upto_lsn) {
    if (upto_lsn > eng->flushed_lsn) {
        eng->flushed_lsn = upto_lsn;
    }
}

void wal_update_page(wal_engine_t *eng, xid_t xid, uint32_t page_id, int32_t new_val) {
    int32_t old_val = eng->pages[page_id].data;
    lsn_t lsn = wal_append(eng, xid, LOG_UPDATE, page_id, old_val, new_val, 0);

    // Модифікація сторінки в Buffer Pool
    eng->pages[page_id].data = new_val;
    eng->pages[page_id].page_lsn = lsn;
}

void wal_commit_tx(wal_engine_t *eng, xid_t xid) {
    lsn_t commit_lsn = wal_append(eng, xid, LOG_COMMIT, 0, 0, 0, 0);
    // Гарантія надійності: синхронне скидання журналу на диск
    wal_flush(eng, commit_lsn);
}

void aries_recovery(wal_engine_t *eng) {
    printf("=== Старт відновлення ARIES ===\n");

    // 1. ФАЗА АНАЛІЗУ (Analysis Phase)
    bool active_tx[MAX_TX] = {false};
    lsn_t last_active_lsn[MAX_TX] = {0};

    for (size_t i = 0; i < eng->log_count; ++i) {
        wal_record_t *rec = &eng->log[i];
        if (rec->type == LOG_UPDATE || rec->type == LOG_CLR) {
            active_tx[rec->xid % MAX_TX] = true;
            last_active_lsn[rec->xid % MAX_TX] = rec->lsn;
        } else if (rec->type == LOG_COMMIT || rec->type == LOG_ABORT) {
            active_tx[rec->xid % MAX_TX] = false;
        }
    }

    // 2. ФАЗА НАКАТУВАННЯ (Redo Phase - Repeating History)
    printf("Фаза Redo: повторення історії...\n");
    for (size_t i = 0; i < eng->log_count; ++i) {
        wal_record_t *rec = &eng->log[i];
        if (rec->type == LOG_UPDATE || rec->type == LOG_CLR) {
            db_page_t *p = &eng->pages[rec->page_id];
            // Ідемпотентне застосування змін
            if (rec->lsn > p->page_lsn) {
                p->data = rec->new_val;
                p->page_lsn = rec->lsn;
                printf("  Сторінка %u оновлена до значення %d (LSN %llu)\n", p->page_id, p->data, (unsigned long long)rec->lsn);
            }
        }
    }

    // 3. ФАЗА СКАСУВАННЯ (Undo Phase)
    printf("Фаза Undo: відкат активних транзакцій...\n");
    for (uint32_t t = 0; t < MAX_TX; ++t) {
        if (active_tx[t]) {
            lsn_t curr_lsn = last_active_lsn[t];
            while (curr_lsn > 0) {
                // Пошук запису в журналі
                wal_record_t *rec = NULL;
                for (size_t i = 0; i < eng->log_count; ++i) {
                    if (eng->log[i].lsn == curr_lsn) {
                        rec = &eng->log[i];
                        break;
                    }
                }
                if (!rec) break;

                if (rec->type == LOG_UPDATE) {
                    // Створення CLR запису
                    lsn_t clr_lsn = wal_append(eng, rec->xid, LOG_CLR, rec->page_id, rec->new_val, rec->old_val, rec->prev_lsn);
                    db_page_t *p = &eng->pages[rec->page_id];
                    p->data = rec->old_val;
                    p->page_lsn = clr_lsn;
                    printf("  Відкат операції tx %u на сторінці %u: відновлено %d (CLR LSN %llu)\n", rec->xid, p->page_id, p->data, (unsigned long long)clr_lsn);
                    curr_lsn = rec->prev_lsn;
                } else if (rec->type == LOG_CLR) {
                    curr_lsn = rec->undo_next_lsn;
                } else {
                    curr_lsn = rec->prev_lsn;
                }
            }
            wal_append(eng, t, LOG_ABORT, 0, 0, 0, 0);
        }
    }
    printf("=== Відновлення ARIES успішно завершено ===\n");
}
