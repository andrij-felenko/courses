/* nff_stress_suite.h - C99 інтерфейс комплексу стрес-тестування NFF */
#ifndef NFF_STRESS_SUITE_H
#define NFF_STRESS_SUITE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define NFF_TEST_BUFFER_SIZE      (16U * 1024U) /* 16 КБ тестового буфера */
#define NFF_MAX_ERROR_LOG_ENTRIES 32U

/* Типи тестових стрес-патернів */
typedef enum {
    PATTERN_CHECKERBOARD = 0,
    PATTERN_WALKING_ONES,
    PATTERN_WALKING_ZEROS,
    PATTERN_BUS_INVERSION,
    PATTERN_PRBS31_RANDOM,
    PATTERN_COUNT
} stress_pattern_type_t;

/* Запис журналу знайденої інтермітуючої помилки */
typedef struct {
    uint32_t timestamp_ms;       /* Час виявлення збою */
    uint32_t memory_offset;      /* Зсув у тестовому буфері */
    uint32_t expected_val;       /* Очікуване значення */
    uint32_t actual_val;         /* Фактично прочитане значення */
    uint32_t xor_diff;           /* Маска спотворених бітів (Actual ^ Expected) */
    uint8_t  pattern_type;       /* Тип патерну, на якому виник збій */
    uint8_t  reserved[3];
} error_log_entry_t;

/* Підсумкова статистика стрес-сесії */
typedef struct {
    uint64_t total_cycles;       /* Загальна кількість виконаних проходів */
    uint64_t total_words_tested; /* Перевірено 32-бітних слів */
    uint32_t error_count;        /* Кількість зафіксованих бітових збоїв */
    uint32_t stuck_at_ones;      /* Помилки типу "залипання в 1" */
    uint32_t stuck_at_zeros;     /* Помилки типу "залипання в 0" */
    uint32_t bridge_faults;      /* Підозра на замикання сусідніх ліній */
    uint32_t duration_ms;        /* Тривалість тесту в мілісекундах */
    uint8_t  is_aborted;         /* Прапорець переривання через критичний збій */
    uint8_t  reserved[3];
} stress_stats_t;

/* Структура контексту стрес-двигуна */
typedef struct {
    uint32_t buffer[NFF_TEST_BUFFER_SIZE / sizeof(uint32_t)];
    error_log_entry_t error_log[NFF_MAX_ERROR_LOG_ENTRIES];
    stress_stats_t stats;
    uint32_t prbs_state;
    uint32_t start_time_ms;
} stress_suite_context_t;

/* Публічний API */
void nff_suite_init(stress_suite_context_t *ctx);
bool nff_suite_run_cycle(stress_suite_context_t *ctx, uint32_t current_time_ms);
void nff_suite_generate_report(const stress_suite_context_t *ctx, char *out_buffer, size_t max_len);
uint32_t nff_suite_get_error_count(const stress_suite_context_t *ctx);

#endif /* NFF_STRESS_SUITE_H */
