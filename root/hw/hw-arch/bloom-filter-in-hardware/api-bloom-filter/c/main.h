#ifndef SYSTEM_BLOOM_FILTER_H
#define SYSTEM_BLOOM_FILTER_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Коди результатів системних операцій
typedef enum {
    BLOOM_OK                = 0,
    BLOOM_ERR_INVALID_ARGS  = -1,
    BLOOM_ERR_OUT_OF_MEMORY = -2,
    BLOOM_ERR_CORRUPT_DATA  = -3,
    BLOOM_ERR_IO            = -4
} bloom_status_t;

// Параметри створення та конфігурації фільтра
typedef struct {
    size_t   expected_entries; // Очікувана кількість унікальних ключів (n)
    double   target_fp_rate;   // Цільова ймовірність хибного спрацьовування (p)
    uint32_t seed;             // Базовий seed для генерації гешів
    bool     cache_aligned;    // Вирівнювання блоків за межею 64 байтів
} bloom_config_t;

// Непрозора структура внутрішнього стану фільтра
typedef struct bloom_filter bloom_filter_t;

// Створення нового екземпляра фільтра у динамічній пам'яті
bloom_status_t bloom_create(const bloom_config_t *config, bloom_filter_t **out_filter);

// Додавання байтового буфера довільної довжини
void bloom_add_bytes(bloom_filter_t *filter, const void *data, size_t len);

// Швидкісний шлях для додавання 64-розрядного цілочисельного ключа
void bloom_add_u64(bloom_filter_t *filter, uint64_t key);

// Перевірка присутності ключа за байтовим буфером (true — ймовірно є, false — 100% немає)
bool bloom_contains_bytes(const bloom_filter_t *filter, const void *data, size_t len);

// Швидкісний шлях для перевірки 64-розрядного цілочисельного ключа
bool bloom_contains_u64(const bloom_filter_t *filter, uint64_t key);

// Скидання всіх розрядів масиву в 0 (очищення фільтра)
void bloom_reset(bloom_filter_t *filter);

// Отримання необхідного розміру буфера для повної бінарної серіалізації
size_t bloom_serialized_size(const bloom_filter_t *filter);

// Серіалізація стану фільтра в байтовий масив
bloom_status_t bloom_serialize(const bloom_filter_t *filter, void *buffer, size_t buf_size);

// Відновлення фільтра з раніше серіалізованого бінарного буфера
bloom_status_t bloom_deserialize(const void *buffer, size_t buf_size, bloom_filter_t **out_filter);

// Звільнення виділених ресурсів та пам'яті фільтра
void bloom_destroy(bloom_filter_t *filter);

#ifdef __cplusplus
}
#endif

#endif // SYSTEM_BLOOM_FILTER_H
