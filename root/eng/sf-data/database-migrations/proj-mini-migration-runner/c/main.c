#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_MIGRATIONS 64
#define MAX_NAME_LEN 64
#define MAX_SQL_LEN 256

typedef struct {
    uint32_t version;
    char name[MAX_NAME_LEN];
    uint32_t checksum;
    char up_sql[MAX_SQL_LEN];
    char down_sql[MAX_SQL_LEN];
    bool applied;
} migration_t;

typedef struct {
    migration_t applied_history[MAX_MIGRATIONS];
    size_t history_count;
    bool advisory_lock_held;
} migration_db_context_t;

// Простий розрахунок хешу CRC32/Adler для перевірки цілісності файлу
uint32_t calculate_checksum(const char *sql) {
    uint32_t hash = 5381;
    int c;
    while ((c = *sql++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

bool db_acquire_advisory_lock(migration_db_context_t *ctx) {
    if (ctx->advisory_lock_held) {
        return false; // Блокування вже утримується іншим процесом
    }
    ctx->advisory_lock_held = true;
    printf("[Lock] Отримано розподілене блокування Advisory Lock (ID: 0xDEADBEEF)\n");
    return true;
}

void db_release_advisory_lock(migration_db_context_t *ctx) {
    ctx->advisory_lock_held = false;
    printf("[Lock] Блокування Advisory Lock успішно звільнено\n");
}

bool run_migrations(migration_db_context_t *ctx, migration_t *available, size_t count) {
    if (!db_acquire_advisory_lock(ctx)) {
        fprintf(stderr, "[Error] Не вдалося отримати блокування: паралельний запуск мігратора!\n");
        return false;
    }

    printf("=== Перевірка цілісності історії схеми ===\n");

    // 1. Валідація вже застосованих міграцій (Checksum verification)
    for (size_t i = 0; i < ctx->history_count; ++i) {
        migration_t *hist = &ctx->applied_history[i];
        bool found = false;
        for (size_t j = 0; j < count; ++j) {
            if (available[j].version == hist->version) {
                found = true;
                uint32_t current_hash = calculate_checksum(available[j].up_sql);
                if (current_hash != hist->checksum) {
                    fprintf(stderr, "[CRITICAL] Порушення цілісності: файл міграції v%u (%s) був змінений після застосування!\n", hist->version, hist->name);
                    db_release_advisory_lock(ctx);
                    return false;
                }
                break;
            }
        }
        if (!found) {
            fprintf(stderr, "[CRITICAL] Історія містить версію v%u, якої немає у вихідному коді!\n", hist->version);
            db_release_advisory_lock(ctx);
            return false;
        }
    }

    // 2. Накатування нових версій
    printf("=== Застосування нових міграцій ===\n");
    for (size_t i = 0; i < count; ++i) {
        migration_t *m = &available[i];
        bool already_applied = false;
        for (size_t j = 0; j < ctx->history_count; ++j) {
            if (ctx->applied_history[j].version == m->version) {
                already_applied = true;
                break;
            }
        }

        if (!already_applied) {
            printf("[START] Транзакція v%u: %s\n", m->version, m->name);
            printf("  SQL: %s\n", m->up_sql);

            // Реєстрація в метатаблиці
            m->checksum = calculate_checksum(m->up_sql);
            m->applied = true;
            ctx->applied_history[ctx->history_count++] = *m;

            printf("[COMMIT] Міграція v%u успішно зафіксована\n", m->version);
        }
    }

    db_release_advisory_lock(ctx);
    printf("=== Схема бази даних в актуальному стані ===\n");
    return true;
}
