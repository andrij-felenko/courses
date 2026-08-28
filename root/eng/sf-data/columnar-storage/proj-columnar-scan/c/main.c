#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define VECTOR_SIZE 1024
#define TOTAL_ROWS 1000000

/* ── Рядкове представлення (NSM) ─────────────────────────────────────────── */
typedef struct {
    int64_t user_id;
    int32_t amount;
    char status[16];
    char description[64]; /* супутнє баластне поле для імітації реального кортежу */
} RowRecord;

typedef struct {
    RowRecord* rows;
    size_t count;
} RowTable;

/* ── Стовпцеве представлення (DSM) ───────────────────────────────────────── */
typedef struct {
    int64_t* user_id;      /* Стовпець 0: int64 */
    int32_t* amount;       /* Стовпець 1: int32 */
    uint8_t* status_id;    /* Стовпець 2: 8-бітні індекси словника */
    char** dictionary;     /* Словник текстових статусів */
    size_t dict_size;
    size_t count;
} ColumnarTable;

/* Результуючий кортеж після проекції */
typedef struct {
    int64_t user_id;
    int32_t amount;
    const char* status;
} ProjectedResult;

/* ── Генерація тестового набору даних ───────────────────────────────────── */
static const char* STATUS_NAMES[] = { "PENDING", "PAID", "CANCELLED", "REFUNDED" };
#define STATUS_COUNT 4

static void generate_test_data(RowTable* rt, ColumnarTable* ct, size_t n) {
    rt->count = n;
    rt->rows = (RowRecord*)malloc(sizeof(RowRecord) * n);

    ct->count = n;
    ct->user_id = (int64_t*)malloc(sizeof(int64_t) * n);
    ct->amount = (int32_t*)malloc(sizeof(int32_t) * n);
    ct->status_id = (uint8_t*)malloc(sizeof(uint8_t) * n);
    ct->dict_size = STATUS_COUNT;
    ct->dictionary = (char**)malloc(sizeof(char*) * STATUS_COUNT);

    for (size_t i = 0; i < STATUS_COUNT; ++i) {
        ct->dictionary[i] = strdup(STATUS_NAMES[i]);
    }

    srand(42);
    for (size_t i = 0; i < n; ++i) {
        int64_t uid = 1000000 + (int64_t)i;
        int32_t amt = rand() % 1000;
        uint8_t st = rand() % STATUS_COUNT;

        /* Заповнення рядкової таблиці */
        rt->rows[i].user_id = uid;
        rt->rows[i].amount = amt;
        snprintf(rt->rows[i].status, sizeof(rt->rows[i].status), "%s", STATUS_NAMES[st]);
        snprintf(rt->rows[i].description, sizeof(rt->rows[i].description), "Transaction payload item #%zu", i);

        /* Заповнення стовпцевої таблиці */
        ct->user_id[i] = uid;
        ct->amount[i] = amt;
        ct->status_id[i] = st;
    }
}

/* ── 1. Рядкове сканування (Tuple-at-a-time) ─────────────────────────────── */
size_t scan_row_oriented(const RowTable* t, int32_t min_amt, const char* target_status) {
    size_t matched_count = 0;
    for (size_t i = 0; i < t->count; ++i) {
        /* Кожна ітерація звертається до полів однієї структури.
           Кеш-лінія завантажує всі 96 байтів кортежу */
        if (t->rows[i].amount > min_amt) {
            if (strcmp(t->rows[i].status, target_status) == 0) {
                matched_count++;
            }
        }
    }
    return matched_count;
}

/* ── 2. Векторизоване стовпцеве сканування з пізньою матеріалізацією ─────── */
size_t scan_columnar_vectorized(const ColumnarTable* t, int32_t min_amt, const char* target_status) {
    size_t matched_count = 0;

    /* Словникова оптимізація: перетворюємо рядок на 8-бітний ID на початку запиту */
    uint8_t target_id = 0xFF;
    for (size_t i = 0; i < t->dict_size; ++i) {
        if (strcmp(t->dictionary[i], target_status) == 0) {
            target_id = (uint8_t)i;
            break;
        }
    }
    if (target_id == 0xFF) return 0; /* статусу немає в словнику */

    /* Локальний буфер індексів для блоку (Selection Vector) */
    uint16_t selection_vector[VECTOR_SIZE];

    /* Обробка стовпців блоками розміром VECTOR_SIZE (ідеально поміщається в L1-кеш) */
    for (size_t block_start = 0; block_start < t->count; block_start += VECTOR_SIZE) {
        size_t block_size = t->count - block_start;
        if (block_size > VECTOR_SIZE) block_size = VECTOR_SIZE;

        size_t sel_count = 0;
        const int32_t* amt_chunk = &t->amount[block_start];
        const uint8_t* st_chunk = &t->status_id[block_start];

        /* Етап 1: Векторизована фільтрація за стовпцями без зчитування user_id */
        for (size_t i = 0; i < block_size; ++i) {
            /* Щільні суміжні масиви: компілятор генерує SIMD-інструкції без розгалужень */
            bool match = (amt_chunk[i] > min_amt) & (st_chunk[i] == target_id);
            if (match) {
                selection_vector[sel_count++] = (uint16_t)i;
            }
        }

        /* Етап 2: Пізня матеріалізація лише для рядків, що пройшли всі фільтри */
        for (size_t j = 0; j < sel_count; ++j) {
            size_t idx = block_start + selection_vector[j];
            int64_t uid = t->user_id[idx];
            int32_t amt = t->amount[idx];
            (void)uid; (void)amt; /* емуляція виводу проекції */
            matched_count++;
        }
    }

    return matched_count;
}

static void free_resources(RowTable* rt, ColumnarTable* ct) {
    free(rt->rows);
    free(ct->user_id);
    free(ct->amount);
    free(ct->status_id);
    for (size_t i = 0; i < ct->dict_size; ++i) {
        free(ct->dictionary[i]);
    }
    free(ct->dictionary);
}

int main(void) {
    RowTable rt;
    ColumnarTable ct;
    printf("Генерація %d тестових транзакцій...\n", TOTAL_ROWS);
    generate_test_data(&rt, &ct, TOTAL_ROWS);

    int32_t filter_amt = 500;
    const char* filter_status = "PAID";

    /* Замір рядкового сканера */
    clock_t t0 = clock();
    size_t count_row = scan_row_oriented(&rt, filter_amt, filter_status);
    clock_t t1 = clock();
    double time_row_ms = (double)(t1 - t0) * 1000.0 / CLOCKS_PER_SEC;

    /* Замір стовпцевого векторизованого сканера */
    clock_t t2 = clock();
    size_t count_col = scan_columnar_vectorized(&ct, filter_amt, filter_status);
    clock_t t3 = clock();
    double time_col_ms = (double)(t3 - t2) * 1000.0 / CLOCKS_PER_SEC;

    printf("\n=== Результати сканування ===\n");
    printf("Рядковий підхід (NSM):      %zu збігів за %.2f мс\n", count_row, time_row_ms);
    printf("Стовпцевий векторизований:  %zu збігів за %.2f мс\n", count_col, time_col_ms);
    printf("Прискорення:                %.2fx\n", time_row_ms / (time_col_ms > 0 ? time_col_ms : 0.001));

    free_resources(&rt, &ct);
    return 0;
}
