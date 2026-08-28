#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define NUM_RECORDS 100000

// 1. Schema-on-write: Бінарна структура з фіксованими зміщеннями
typedef struct {
    uint32_t id;
    float temperature;
    uint32_t timestamp;
    char status[8];
} write_record_t;

// 2. Schema-on-read: Сирий текстовий буфер
typedef struct {
    char raw_data[64];
} read_record_t;

// Schema-on-read парсер температури на льоту
bool extract_temperature(const char *raw, float *out_temp) {
    const char *key = "temp=";
    const char *pos = strstr(raw, key);
    if (!pos) return false;

    pos += strlen(key);
    *out_temp = (float)strtod(pos, NULL);
    return true;
}

int main(void) {
    write_record_t *write_db = malloc(sizeof(write_record_t) * NUM_RECORDS);
    read_record_t *read_db = malloc(sizeof(read_record_t) * NUM_RECORDS);

    if (!write_db || !read_db) {
        printf("Memory allocation failed.\n");
        return 1;
    }

    // Заповнення тестових даних
    for (int i = 0; i < NUM_RECORDS; ++i) {
        // Schema-on-write ініціалізація
        write_db[i].id = (uint32_t)i;
        write_db[i].temperature = 20.0f + (float)(i % 100) * 0.1f;
        write_db[i].timestamp = 1700000000 + (uint32_t)i;
        strncpy(write_db[i].status, "ACTIVE", 7);

        // Schema-on-read ініціалізація
        snprintf(read_db[i].raw_data, 63, "id=%d;temp=%.2f;ts=%u;status=ACTIVE", 
                 i, write_db[i].temperature, write_db[i].timestamp);
    }

    // --- ТЕСТ 1: Schema-on-write Агрегація ---
    clock_t start_w = clock();
    double sum_w = 0.0;
    for (int i = 0; i < NUM_RECORDS; ++i) {
        sum_w += write_db[i].temperature;
    }
    clock_t end_w = clock();
    double time_w = (double)(end_w - start_w) / CLOCKS_PER_SEC * 1000.0;

    // --- ТЕСТ 2: Schema-on-read Агрегація ---
    clock_t start_r = clock();
    double sum_r = 0.0;
    for (int i = 0; i < NUM_RECORDS; ++i) {
        float temp = 0.0f;
        if (extract_temperature(read_db[i].raw_data, &temp)) {
            sum_r += temp;
        }
    }
    clock_t end_r = clock();
    double time_r = (double)(end_r - start_r) / CLOCKS_PER_SEC * 1000.0;

    printf("=== Результати бенчмарку (%d записів) ===\n", NUM_RECORDS);
    printf("Schema-on-write час: %.3f мс (Сума: %.1f)\n", time_w, sum_w);
    printf("Schema-on-read  час: %.3f мс (Сума: %.1f)\n", time_r, sum_r);
    printf("Прискорення Schema-on-write: %.1fx\n", time_r / (time_w > 0.001 ? time_w : 0.001));

    free(write_db);
    free(read_db);
    return 0;
}
