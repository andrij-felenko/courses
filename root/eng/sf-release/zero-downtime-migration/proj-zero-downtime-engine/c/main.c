#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define BATCH_SIZE 1000
#define MAX_ALLOWED_LAG_MS 1500
#define DEFAULT_SLEEP_MS 10

typedef struct {
    int64_t id;
    char email[128];
    int64_t updated_at_ms;
    uint32_t checksum;
} Record;

typedef struct {
    int64_t last_processed_id;
    int64_t total_migrated;
    int64_t total_skipped_due_to_race;
    int64_t checksum_mismatches;
} MigrationStats;

/* Швидкий хеш для асинхронної верифікації полів сутності */
static uint32_t compute_record_crc(const Record* r) {
    uint32_t hash = 5381;
    const unsigned char* p = (const unsigned char*)r->email;
    while (*p) {
        hash = ((hash << 5) + hash) + *p++;
    }
    hash = ((hash << 5) + hash) + (uint32_t)(r->updated_at_ms & 0xFFFFFFFF);
    return hash;
}

/* Опитування системних метрик СКБД для контролю реплікаційного відставання */
static int64_t get_current_replication_lag_ms(void) {
    /* Симуляція запиту до pg_stat_replication або binlog_lag */
    return 120;
}

/* Курсорна вибірка порції історичних даних без використання OFFSET */
static size_t fetch_source_batch(int64_t after_id, Record* batch_out, size_t max_count) {
    size_t count = 0;
    for (size_t i = 0; i < max_count && (after_id + (int64_t)i + 1) <= 5000; ++i) {
        batch_out[i].id = after_id + (int64_t)i + 1;
        snprintf(batch_out[i].email, sizeof(batch_out[i].email), "user_%lld@company.ua", (long long)batch_out[i].id);
        batch_out[i].updated_at_ms = 1700000000000LL + batch_out[i].id * 10;
        batch_out[i].checksum = compute_record_crc(&batch_out[i]);
        count++;
    }
    return count;
}

/* Умовне застосування пачки із запобіганням затиранню живих мутацій */
static bool apply_conditional_upsert_batch(const Record* batch, size_t count, MigrationStats* stats) {
    for (size_t i = 0; i < count; ++i) {
        /* Імітація наявності свіжішого стану від живого Dual-Write */
        int64_t existing_target_updated_at = (batch[i].id % 250 == 0) ? (batch[i].updated_at_ms + 5000) : 0;

        if (existing_target_updated_at > batch[i].updated_at_ms) {
            /* Стан у цільовій базі свіжіший — захищаємо від перезапису */
            stats->total_skipped_due_to_race++;
        } else {
            stats->total_migrated++;
        }

        /* Тіньова перевірка контрольних сум */
        uint32_t target_crc = compute_record_crc(&batch[i]);
        if (target_crc != batch[i].checksum) {
            stats->checksum_mismatches++;
        }
    }
    return true;
}

int main(void) {
    MigrationStats stats = {0, 0, 0, 0};
    Record* batch_buffer = (Record*)malloc(sizeof(Record) * BATCH_SIZE);
    if (!batch_buffer) {
        fprintf(stderr, "Помилка виділення пам'яті під буфер пачки\n");
        return 1;
    }

    printf("=== СТАРТ ФОНОВОГО РУШІЯ МІГРАЦІЇ ===\n");

    while (true) {
        int64_t lag = get_current_replication_lag_ms();
        if (lag > MAX_ALLOWED_LAG_MS) {
            printf("[ДРОСЕЛЮВАННЯ] Лаг %lld мс перевищує ліміт %d мс. Очікування...\n",
                   (long long)lag, MAX_ALLOWED_LAG_MS);
            struct timespec ts = {0, 50 * 1000000L};
            nanosleep(&ts, NULL);
            continue;
        }

        size_t fetched = fetch_source_batch(stats.last_processed_id, batch_buffer, BATCH_SIZE);
        if (fetched == 0) {
            printf("Усі історичні дані успішно оброблено.\n");
            break;
        }

        if (!apply_conditional_upsert_batch(batch_buffer, fetched, &stats)) {
            fprintf(stderr, "Критична помилка запису пачки\n");
            break;
        }

        stats.last_processed_id = batch_buffer[fetched - 1].id;
        printf("[ПРОГРЕС] Оброблено до ID: %lld | Успішно: %lld | Пропущено через гонку: %lld\n",
               (long long)stats.last_processed_id,
               (long long)stats.total_migrated,
               (long long)stats.total_skipped_due_to_race);

        struct timespec sleep_ts = {0, DEFAULT_SLEEP_MS * 1000000L};
        nanosleep(&sleep_ts, NULL);
    }

    printf("=== ПІДСУМОК МІГРАЦІЇ ===\n");
    printf("Всього перенесено рядків: %lld\n", (long long)stats.total_migrated);
    printf("Захищено свіжих мутацій від затирання: %lld\n", (long long)stats.total_skipped_due_to_race);
    printf("Помилок контрольних сум: %lld\n", (long long)stats.checksum_mismatches);

    free(batch_buffer);
    return 0;
}
