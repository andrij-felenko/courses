#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define WAL_MAGIC 0x57414C31 /* "WAL1" */

typedef enum {
    REC_BEGIN  = 0x01,
    REC_INSERT = 0x02,
    REC_UPDATE = 0x03,
    REC_DELETE = 0x04,
    REC_COMMIT = 0x05,
    REC_ABORT  = 0x06
} RecordType;

typedef struct {
    uint8_t  type;
    uint32_t length;
    uint64_t lsn;
    uint64_t xid;
    uint32_t table_id;
    uint64_t pk;
    uint64_t timestamp;
    char    *before_data;
    char    *after_data;
} ChangeRecord;

typedef struct {
    uint64_t      xid;
    uint64_t      begin_lsn;
    uint64_t      begin_ts;
    ChangeRecord *records;
    size_t        count;
    size_t        capacity;
} TxBuffer;

typedef struct {
    TxBuffer **tx_table;
    size_t     tx_capacity;
    uint64_t   last_confirmed_lsn;
} CdcEngine;

CdcEngine* cdc_create(size_t max_concurrent_tx) {
    CdcEngine *engine = (CdcEngine*)calloc(1, sizeof(CdcEngine));
    if (!engine) return NULL;
    engine->tx_capacity = max_concurrent_tx;
    engine->tx_table = (TxBuffer**)calloc(max_concurrent_tx, sizeof(TxBuffer*));
    if (!engine->tx_table) {
        free(engine);
        return NULL;
    }
    return engine;
}

static TxBuffer* cdc_find_or_create_tx(CdcEngine *engine, uint64_t xid) {
    size_t empty_idx = engine->tx_capacity;
    for (size_t i = 0; i < engine->tx_capacity; ++i) {
        if (engine->tx_table[i] && engine->tx_table[i]->xid == xid) {
            return engine->tx_table[i];
        }
        if (!engine->tx_table[i] && empty_idx == engine->tx_capacity) {
            empty_idx = i;
        }
    }
    if (empty_idx == engine->tx_capacity) return NULL;

    TxBuffer *tx = (TxBuffer*)calloc(1, sizeof(TxBuffer));
    if (!tx) return NULL;
    tx->xid = xid;
    tx->capacity = 16;
    tx->records = (ChangeRecord*)calloc(tx->capacity, sizeof(ChangeRecord));
    if (!tx->records) {
        free(tx);
        return NULL;
    }
    engine->tx_table[empty_idx] = tx;
    return tx;
}

static void cdc_free_tx(CdcEngine *engine, uint64_t xid) {
    for (size_t i = 0; i < engine->tx_capacity; ++i) {
        if (engine->tx_table[i] && engine->tx_table[i]->xid == xid) {
            TxBuffer *tx = engine->tx_table[i];
            for (size_t j = 0; j < tx->count; ++j) {
                free(tx->records[j].before_data);
                free(tx->records[j].after_data);
            }
            free(tx->records);
            free(tx);
            engine->tx_table[i] = NULL;
            return;
        }
    }
}

static void cdc_emit_event(const ChangeRecord *rec, uint64_t commit_lsn, uint64_t commit_ts) {
    const char *op_str = "UNKNOWN";
    if (rec->type == REC_INSERT) op_str = "c"; /* create */
    else if (rec->type == REC_UPDATE) op_str = "u"; /* update */
    else if (rec->type == REC_DELETE) op_str = "d"; /* delete */

    printf("{\"op\":\"%s\",\"lsn\":%llu,\"commit_lsn\":%llu,\"xid\":%llu,\"table_id\":%u,\"pk\":%llu,\"ts\":%llu,",
           op_str, (unsigned long long)rec->lsn, (unsigned long long)commit_lsn,
           (unsigned long long)rec->xid, rec->table_id,
           (unsigned long long)rec->pk, (unsigned long long)commit_ts);

    printf("\"before\":%s%s%s,",
           rec->before_data ? "\"" : "", rec->before_data ? rec->before_data : "null", rec->before_data ? "\"" : "");
    printf("\"after\":%s%s%s}\n",
           rec->after_data ? "\"" : "", rec->after_data ? rec->after_data : "null", rec->after_data ? "\"" : "");
}

bool cdc_process_record(CdcEngine *engine, const uint8_t *buf, size_t buf_len) {
    if (buf_len < 21) return false;

    uint8_t type = buf[0];
    uint32_t len = *(const uint32_t*)(buf + 1);
    uint64_t lsn = *(const uint64_t*)(buf + 5);
    uint64_t xid = *(const uint64_t*)(buf + 13);

    if (buf_len < len) return false;
    const uint8_t *payload = buf + 21;

    if (type == REC_BEGIN) {
        TxBuffer *tx = cdc_find_or_create_tx(engine, xid);
        if (!tx) return false;
        tx->begin_lsn = lsn;
        tx->begin_ts = *(const uint64_t*)(payload);
        return true;
    }

    if (type == REC_ABORT) {
        /* Відкат транзакції: очищуємо буфер без генерації подій */
        cdc_free_tx(engine, xid);
        return true;
    }

    if (type == REC_COMMIT) {
        TxBuffer *tx = cdc_find_or_create_tx(engine, xid);
        if (!tx) return false;

        uint64_t commit_lsn = *(const uint64_t*)(payload);
        uint64_t commit_ts = *(const uint64_t*)(payload + 8);

        /* Випромінюємо всі накопичені події підтвердженої транзакції */
        for (size_t i = 0; i < tx->count; ++i) {
            cdc_emit_event(&tx->records[i], commit_lsn, commit_ts);
        }

        engine->last_confirmed_lsn = commit_lsn;
        cdc_free_tx(engine, xid);
        return true;
    }

    /* Обробка мутацій рядків: накопичення у буфер транзакції */
    TxBuffer *tx = cdc_find_or_create_tx(engine, xid);
    if (!tx) return false;

    if (tx->count >= tx->capacity) {
        size_t new_cap = tx->capacity * 2;
        ChangeRecord *new_recs = (ChangeRecord*)realloc(tx->records, new_cap * sizeof(ChangeRecord));
        if (!new_recs) return false;
        tx->records = new_recs;
        tx->capacity = new_cap;
    }

    ChangeRecord *rec = &tx->records[tx->count++];
    memset(rec, 0, sizeof(ChangeRecord));
    rec->type = type;
    rec->lsn = lsn;
    rec->xid = xid;
    rec->table_id = *(const uint32_t*)(payload);
    rec->pk = *(const uint64_t*)(payload + 4);

    if (type == REC_INSERT) {
        uint32_t data_len = *(const uint32_t*)(payload + 12);
        rec->after_data = (char*)calloc(data_len + 1, 1);
        if (rec->after_data) memcpy(rec->after_data, payload + 16, data_len);
    } else if (type == REC_UPDATE) {
        uint32_t old_len = *(const uint32_t*)(payload + 12);
        rec->before_data = (char*)calloc(old_len + 1, 1);
        if (rec->before_data) memcpy(rec->before_data, payload + 16, old_len);

        uint32_t new_len = *(const uint32_t*)(payload + 16 + old_len);
        rec->after_data = (char*)calloc(new_len + 1, 1);
        if (rec->after_data) memcpy(rec->after_data, payload + 20 + old_len, new_len);
    } else if (type == REC_DELETE) {
        uint32_t old_len = *(const uint32_t*)(payload + 12);
        rec->before_data = (char*)calloc(old_len + 1, 1);
        if (rec->before_data) memcpy(rec->before_data, payload + 16, old_len);
    }

    return true;
}

void cdc_destroy(CdcEngine *engine) {
    if (!engine) return;
    for (size_t i = 0; i < engine->tx_capacity; ++i) {
        if (engine->tx_table[i]) {
            TxBuffer *tx = engine->tx_table[i];
            for (size_t j = 0; j < tx->count; ++j) {
                free(tx->records[j].before_data);
                free(tx->records[j].after_data);
            }
            free(tx->records);
            free(tx);
        }
    }
    free(engine->tx_table);
    free(engine);
}
