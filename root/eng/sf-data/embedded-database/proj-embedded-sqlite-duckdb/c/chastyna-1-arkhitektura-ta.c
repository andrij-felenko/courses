#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <sqlite3.h>

#define DB_PATH "embedded_storage.db"
#define NUM_READERS 4

/* Конфігурація з'єднання: WAL, синхронізація NORMAL, таймаут 5000 мс */
static sqlite3* open_configured_connection(int flags) {
    sqlite3 *db = NULL;
    int rc = sqlite3_open_v2(DB_PATH, &db, flags, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка відкриття БД: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return NULL;
    }

    /* Налаштування очікування при блокуванні файлу */
    sqlite3_busy_timeout(db, 5000);

    /* Увімкнення журналу WAL та оптимізації синхронізації */
    char *err_msg = NULL;
    rc = sqlite3_exec(db, "PRAGMA journal_mode=WAL;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка встановлення WAL: %s\n", err_msg);
        sqlite3_free(err_msg);
    }
    sqlite3_exec(db, "PRAGMA synchronous=NORMAL;", NULL, NULL, NULL);

    return db;
}

/* Потік-записувач: виконує періодичні вставки у транзакціях */
void* writer_thread(void *arg) {
    (void)arg;
    sqlite3 *db = open_configured_connection(SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_NOMUTEX);
    if (!db) return NULL;

    const char *sql_insert = "INSERT INTO sensor_payloads (device_id, payload) VALUES (?, ?);";
    sqlite3_stmt *stmt = NULL;
    sqlite3_prepare_v3(db, sql_insert, -1, 0, &stmt, NULL);

    uint8_t buffer[64];
    for (int i = 0; i < 100; ++i) {
        memset(buffer, (uint8_t)i, sizeof(buffer));

        /* Явний початок транзакції запису для запобігання авто-комітам на кожен рядок */
        sqlite3_exec(db, "BEGIN IMMEDIATE TRANSACTION;", NULL, NULL, NULL);
        sqlite3_reset(stmt);
        sqlite3_bind_int(stmt, 1, 1000 + i);
        sqlite3_bind_blob(stmt, 2, buffer, sizeof(buffer), SQLITE_STATIC);

        if (sqlite3_step(stmt) != SQLITE_DONE) {
            fprintf(stderr, "Помилка запису: %s\n", sqlite3_errmsg(db));
        }
        sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return NULL;
}

/* Потік-читач: демонструє Zero-Copy доступ до BLOB-даних */
void* reader_thread(void *arg) {
    int thread_id = *(int*)arg;
    sqlite3 *db = open_configured_connection(SQLITE_OPEN_READONLY | SQLITE_OPEN_NOMUTEX);
    if (!db) return NULL;

    const char *sql_select = "SELECT id, device_id, payload FROM sensor_payloads ORDER BY id DESC LIMIT 5;";
    sqlite3_stmt *stmt = NULL;
    sqlite3_prepare_v3(db, sql_select, -1, 0, &stmt, NULL);

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        int dev_id = sqlite3_column_int(stmt, 1);
        
        /* Zero-copy: отримання прямого покажчика у внутрішній кеш сторінки */
        const void *blob_ptr = sqlite3_column_blob(stmt, 2);
        int blob_size = sqlite3_column_bytes(stmt, 2);

        /* Пряма обробка байтів за адресою без виклику malloc() */
        uint8_t first_byte = (blob_size > 0 && blob_ptr) ? *((const uint8_t*)blob_ptr) : 0;
        (void)first_byte;
        (void)id;
        (void)dev_id;
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return NULL;
}
