#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_KEYS 1024
#define WAL_PATH "minidb.wal"

typedef enum {
    LOG_BEGIN = 1,
    LOG_UPDATE = 2,
    LOG_COMMIT = 3,
    LOG_ABORT = 4
} LogType;

typedef struct {
    uint64_t lsn;
    uint64_t txn_id;
    uint32_t type;
    uint32_t key;
    int32_t old_val;
    int32_t new_val;
} WalRecord;

typedef struct {
    int32_t val;
    uint64_t page_lsn;
    uint64_t lock_owner; // 0 = unlocked, >0 = txn_id
} TableEntry;

typedef struct {
    TableEntry entries[MAX_KEYS];
    int wal_fd;
    uint64_t next_lsn;
    uint64_t next_txn_id;
} Engine;

bool engine_init(Engine *eng) {
    memset(eng->entries, 0, sizeof(eng->entries));
    eng->next_lsn = 1;
    eng->next_txn_id = 1;
    eng->wal_fd = open(WAL_PATH, O_CREAT | O_RDWR | O_APPEND, 0644);
    return eng->wal_fd >= 0;
}

void engine_close(Engine *eng) {
    if (eng->wal_fd >= 0) {
        fsync(eng->wal_fd);
        close(eng->wal_fd);
        eng->wal_fd = -1;
    }
}

uint64_t append_wal(Engine *eng, uint64_t txn_id, LogType type,
                    uint32_t key, int32_t old_v, int32_t new_v, bool flush) {
    WalRecord rec = {
        .lsn = eng->next_lsn++,
        .txn_id = txn_id,
        .type = (uint32_t)type,
        .key = key,
        .old_val = old_v,
        .new_val = new_v
    };
    write(eng->wal_fd, &rec, sizeof(rec));
    if (flush) {
        fsync(eng->wal_fd);
    }
    return rec.lsn;
}

uint64_t txn_begin(Engine *eng) {
    uint64_t tid = eng->next_txn_id++;
    append_wal(eng, tid, LOG_BEGIN, 0, 0, 0, false);
    return tid;
}

bool txn_update(Engine *eng, uint64_t tid, uint32_t key, int32_t new_v) {
    if (key >= MAX_KEYS) return false;
    TableEntry *entry = &eng->entries[key];

    // Песимістичне блокування (2PL): перевірка власника замка
    if (entry->lock_owner != 0 && entry->lock_owner != tid) {
        return false; // Конфлікт блокування
    }
    entry->lock_owner = tid;

    int32_t old_v = entry->val;
    // Запис у WAL ПЕРЕД зміною даних у пам'яті (Undo/Redo Invariant)
    uint64_t lsn = append_wal(eng, tid, LOG_UPDATE, key, old_v, new_v, false);

    entry->val = new_v;
    entry->page_lsn = lsn;
    return true;
}

void txn_commit(Engine *eng, uint64_t tid) {
    // Надійний запис COMMIT у WAL із викликом fsync (Durability)
    append_wal(eng, tid, LOG_COMMIT, 0, 0, 0, true);

    // Звільнення блокувань (Strict 2PL)
    for (uint32_t k = 0; k < MAX_KEYS; ++k) {
        if (eng->entries[k].lock_owner == tid) {
            eng->entries[k].lock_owner = 0;
        }
    }
}

void txn_abort(Engine *eng, uint64_t tid) {
    // Скасування: читаємо WAL у зворотному напрямку для відкату змін цієї транзакції
    off_t cur = lseek(eng->wal_fd, 0, SEEK_END);
    off_t pos = cur;
    WalRecord rec;

    while (pos >= (off_t)sizeof(WalRecord)) {
        pos -= sizeof(WalRecord);
        lseek(eng->wal_fd, pos, SEEK_SET);
        if (read(eng->wal_fd, &rec, sizeof(rec)) == sizeof(rec)) {
            if (rec.txn_id == tid && rec.type == LOG_UPDATE) {
                if (rec.key < MAX_KEYS) {
                    eng->entries[rec.key].val = rec.old_val;
                }
            }
        }
    }
    lseek(eng->wal_fd, cur, SEEK_SET);

    append_wal(eng, tid, LOG_ABORT, 0, 0, 0, true);

    for (uint32_t k = 0; k < MAX_KEYS; ++k) {
        if (eng->entries[k].lock_owner == tid) {
            eng->entries[k].lock_owner = 0;
        }
    }
}

// Трифазне відновлення після аварійного збою
void engine_recover(Engine *eng) {
    int fd = open(WAL_PATH, O_RDONLY);
    if (fd < 0) return;

    // Фаза 1: Аналіз активних транзакцій
    #define MAX_TXNS 256
    uint64_t active_txns[MAX_TXNS];
    int active_cnt = 0;

    WalRecord rec;
    uint64_t max_lsn = 0;
    uint64_t max_tid = 0;

    while (read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
        if (rec.lsn > max_lsn) max_lsn = rec.lsn;
        if (rec.txn_id > max_tid) max_tid = rec.txn_id;

        if (rec.type == LOG_BEGIN) {
            if (active_cnt < MAX_TXNS) active_txns[active_cnt++] = rec.txn_id;
        } else if (rec.type == LOG_COMMIT || rec.type == LOG_ABORT) {
            for (int i = 0; i < active_cnt; ++i) {
                if (active_txns[i] == rec.txn_id) {
                    active_txns[i] = active_txns[--active_cnt];
                    break;
                }
            }
        }
    }

    // Фаза 2: REDO (повторення всіх змін)
    lseek(fd, 0, SEEK_SET);
    while (read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
        if (rec.type == LOG_UPDATE && rec.key < MAX_KEYS) {
            eng->entries[rec.key].val = rec.new_val;
            eng->entries[rec.key].page_lsn = rec.lsn;
        }
    }

    // Фаза 3: UNDO (скасування незафіксованих транзакцій)
    for (int i = 0; i < active_cnt; ++i) {
        uint64_t bad_tid = active_txns[i];
        off_t pos = lseek(fd, 0, SEEK_END);
        while (pos >= (off_t)sizeof(WalRecord)) {
            pos -= sizeof(WalRecord);
            lseek(fd, pos, SEEK_SET);
            if (read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
                if (rec.txn_id == bad_tid && rec.type == LOG_UPDATE) {
                    if (rec.key < MAX_KEYS) {
                        eng->entries[rec.key].val = rec.old_val;
                    }
                }
            }
        }
    }

    close(fd);
    eng->next_lsn = max_lsn + 1;
    eng->next_txn_id = max_tid + 1;
}
