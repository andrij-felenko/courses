#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_ENTRIES 1024
#define KEY_LEN 32
#define VAL_LEN 64
#define WAL_MAGIC 0x57414C31  /* "WAL1" у двійковому форматі */

/* ── Бінарний заголовок запису в журналі WAL ─────────────────────────────── */
#pragma pack(push, 1)
typedef struct {
    uint32_t magic;         /* Магічне число валідації формату */
    uint64_t lsn;           /* Монотонний Log Sequence Number */
    uint64_t timestamp_ms;  /* Час транзакції (UTC Epoch мілісекунди) */
    uint8_t  op_type;       /* 1 = INSERT/UPDATE, 2 = DELETE, 3 = TRUNCATE */
    uint32_t payload_len;   /* Довжина корисного навантаження */
    uint32_t crc32;         /* Контрольна сума CRC32 корисного навантаження */
} WalRecordHeader;

typedef struct {
    char key[KEY_LEN];
    char value[VAL_LEN];
} WalPayload;
#pragma pack(pop)

/* ── Стан бази даних у пам'яті (Key-Value Store) ─────────────────────────── */
typedef struct {
    char key[KEY_LEN];
    char value[VAL_LEN];
    bool is_active;
} DbEntry;

typedef struct {
    DbEntry entries[MAX_ENTRIES];
    size_t count;
    uint64_t last_applied_lsn;
    uint64_t last_applied_ts;
} Database;

/* ── Таблиця та обчислення контрольної суми CRC32 ────────────────────────── */
static uint32_t crc32_table[256];
static bool crc_initialized = false;

static void init_crc32_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int j = 0; j < 8; j++) {
            c = (c & 1) ? (0xEDB88320L ^ (c >> 1)) : (c >> 1);
        }
        crc32_table[i] = c;
    }
    crc_initialized = true;
}

static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    if (!crc_initialized) init_crc32_table();
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc = crc32_table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFF;
}

/* ── Операції над станом бази даних ──────────────────────────────────────── */
static void db_init(Database *db) {
    memset(db, 0, sizeof(Database));
}

static void db_put(Database *db, const char *key, const char *value) {
    for (size_t i = 0; i < db->count; i++) {
        if (strcmp(db->entries[i].key, key) == 0) {
            strncpy(db->entries[i].value, value, VAL_LEN - 1);
            db->entries[i].value[VAL_LEN - 1] = '\0';
            db->entries[i].is_active = true;
            return;
        }
    }
    if (db->count < MAX_ENTRIES) {
        strncpy(db->entries[db->count].key, key, KEY_LEN - 1);
        strncpy(db->entries[db->count].value, value, VAL_LEN - 1);
        db->entries[db->count].is_active = true;
        db->count++;
    }
}

static void db_delete(Database *db, const char *key) {
    for (size_t i = 0; i < db->count; i++) {
        if (strcmp(db->entries[i].key, key) == 0) {
            db->entries[i].is_active = false;
            return;
        }
    }
}

static void db_truncate(Database *db) {
    for (size_t i = 0; i < db->count; i++) {
        db->entries[i].is_active = false;
    }
}

static void db_dump(const Database *db) {
    printf("=== СТАН БАЗИ ДАНИХ (Останній LSN: %llu) ===
", (unsigned long long)db->last_applied_lsn);
    for (size_t i = 0; i < db->count; i++) {
        if (db->entries[i].is_active) {
            printf("  [%s] => "%s"
", db->entries[i].key, db->entries[i].value);
        }
    }
    printf("==================================================
");
}

/* ── Координатор Point-in-Time Recovery ──────────────────────────────────── */
static int pitr_apply_wal(Database *db, const char *wal_filepath, uint64_t target_stop_ts_ms) {
    FILE *fp = fopen(wal_filepath, "rb");
    if (!fp) {
        perror("Не вдалося відкрити файл журналу WAL");
        return -1;
    }

    WalRecordHeader hdr;
    WalPayload payload;
    int records_applied = 0;

    while (fread(&hdr, sizeof(WalRecordHeader), 1, fp) == 1) {
        if (hdr.magic != WAL_MAGIC) {
            fprintf(stderr, "Помилка: Пошкоджений магічний заголовок WAL на позиції %ld
", ftell(fp));
            fclose(fp);
            return -2;
        }

        if (hdr.payload_len != sizeof(WalPayload)) {
            fprintf(stderr, "Помилка: Некоректний розмір корисного навантаження: %u
", hdr.payload_len);
            fclose(fp);
            return -3;
        }

        if (fread(&payload, sizeof(WalPayload), 1, fp) != 1) {
            fprintf(stderr, "Помилка: Неочікуваний кінець файлу при читанні даних
");
            fclose(fp);
            return -4;
        }

        /* Перевірка контрольної суми CRC32 */
        uint32_t expected_crc = calculate_crc32((const uint8_t *)&payload, sizeof(WalPayload));
        if (expected_crc != hdr.crc32) {
            fprintf(stderr, "Помилка CRC32 у записі LSN=%llu (очікувалось 0x%08X, отримано 0x%08X)
",
                    (unsigned long long)hdr.lsn, expected_crc, hdr.crc32);
            fclose(fp);
            return -5;
        }

        /* Критерій зупинки PITR: чи не перевищено цільовий час? */
        if (hdr.timestamp_ms > target_stop_ts_ms) {
            printf(">> [PITR ЗУПИНКА] Досягнуто часової межі: %llu ms > Target: %llu ms. Пропуск запису LSN=%llu.
",
                   (unsigned long long)hdr.timestamp_ms, (unsigned long long)target_stop_ts_ms, (unsigned long long)hdr.lsn);
            break;
        }

        /* REDO операція: застосування зміни */
        if (hdr.op_type == 1) {
            db_put(db, payload.key, payload.value);
        } else if (hdr.op_type == 2) {
            db_delete(db, payload.key);
        } else if (hdr.op_type == 3) {
            db_truncate(db);
        }

        db->last_applied_lsn = hdr.lsn;
        db->last_applied_ts = hdr.timestamp_ms;
        records_applied++;
    }

    fclose(fp);
    return records_applied;
}

int main(void) {
    printf("=== ДЕМОНСТРАЦІЯ РУШІЯ POINT-IN-TIME RECOVERY (C) ===
");
    
    Database db;
    db_init(&db);

    /* 1. Імітуємо розгортання базового знімка від 02:00:00 (100000 ms) */
    printf("[1] Відновлення базового знімка (Base Snapshot)...
");
    db_put(&db, "user:101", "Alice (Account: 500)");
    db_put(&db, "user:102", "Bob (Account: 1200)");
    db.last_applied_lsn = 1000;
    db_dump(&db);

    /* 2. Створюємо тестовий бінарний файл WAL із послідовністю дій */
    const char *wal_file = "test_wal_segment.bin";
    FILE *wfp = fopen(wal_file, "wb");
    if (!wfp) return 1;

    WalRecordHeader h;
    WalPayload p;

    /* Запис 1 (14:00:00 = 150000 ms): Поповнення балансу Alice */
    h.magic = WAL_MAGIC;
    h.lsn = 1001;
    h.timestamp_ms = 150000;
    h.op_type = 1;
    h.payload_len = sizeof(WalPayload);
    strncpy(p.key, "user:101", KEY_LEN);
    strncpy(p.value, "Alice (Account: 750)", VAL_LEN);
    h.crc32 = calculate_crc32((const uint8_t*)&p, sizeof(WalPayload));
    fwrite(&h, sizeof(h), 1, wfp);
    fwrite(&p, sizeof(p), 1, wfp);

    /* Запис 2 (14:27:03 = 154000 ms): Створення нового клієнта Charlie */
    h.lsn = 1002;
    h.timestamp_ms = 154000;
    h.op_type = 1;
    strncpy(p.key, "user:103", KEY_LEN);
    strncpy(p.value, "Charlie (Account: 300)", VAL_LEN);
    h.crc32 = calculate_crc32((const uint8_t*)&p, sizeof(WalPayload));
    fwrite(&h, sizeof(h), 1, wfp);
    fwrite(&p, sizeof(p), 1, wfp);

    /* Запис 3 (14:27:05 = 156000 ms - КАТАСТРОФА): Руйнівний TRUNCATE */
    h.lsn = 1003;
    h.timestamp_ms = 156000;
    h.op_type = 3;
    strncpy(p.key, "*", KEY_LEN);
    strncpy(p.value, "TRUNCATE_ALL", VAL_LEN);
    h.crc32 = calculate_crc32((const uint8_t*)&p, sizeof(WalPayload));
    fwrite(&h, sizeof(h), 1, wfp);
    fwrite(&p, sizeof(p), 1, wfp);

    fclose(wfp);
    printf("[2] Згенеровано потік WAL з 3 транзакціями (включаючи катастрофічний TRUNCATE о 156000 ms)
");

    /* 3. Виконуємо PITR із зупинкою на 155000 ms (між Charlie та TRUNCATE) */
    uint64_t target_time = 155000;
    printf("[3] Запуск PITR до цільового часу: %llu ms...
", (unsigned long long)target_time);
    
    int applied = pitr_apply_wal(&db, wal_file, target_time);
    printf("Успішно застосовано записів WAL: %d
", applied);

    /* 4. Фінальний стан: Чарлі доданий, баланс Аліси оновлений, а TRUNCATE проігноровано! */
    db_dump(&db);

    remove(wal_file);
    return 0;
}
