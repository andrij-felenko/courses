#ifndef PSRAM_BENCHMARK_H
#define PSRAM_BENCHMARK_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура збереження результатів заміру пропускної здатності пам'яті.
 */
typedef struct {
    size_t buffer_size_bytes;       /*!< Розмір тестового буфера в байтах */
    double seq_write_speed_mbps;   /*!< Швидкість послідовного запису (МБ/с) */
    double seq_read_speed_mbps;    /*!< Швидкість послідовного зчитування (МБ/с) */
    double rand_write_speed_mbps;  /*!< Швидкість довільного запису (МБ/с) */
    double rand_read_speed_mbps;   /*!< Швидкість довільного зчитування (МБ/с) */
} psram_benchmark_result_t;

/**
 * @brief Перевіряє доступність та наявність ініціалізованої PSRAM у системі.
 *
 * @return true Якщо зовнішня пам'ять PSRAM виявлена та доступна.
 * @return false Якщо PSRAM відсутня або не налаштована в sdkconfig.
 */
bool psram_is_available(void);

/**
 * @brief Виводить у системний лог інформацію про загальний та вільний обсяг PSRAM.
 */
void psram_print_info(void);

/**
 * @brief Виділяє буфер заданого розміру у зовнішній пам'яті PSRAM.
 *
 * @param size Розмір буфера в байтах.
 * @return void* Вказівник на виділену пам'ять або NULL у разі помилки.
 */
void *psram_allocate_buffer(size_t size);

/**
 * @brief Звільняє раніше виділений буфер у PSRAM.
 *
 * @param ptr Вказівник на буфер для звільнення.
 */
void psram_free_buffer(void *ptr);

/**
 * @brief Проводить замір пропускної здатності PSRAM (послідовний та довільний доступ).
 *
 * @param buffer_size Розмір буфера для проведення тестування у байтах.
 * @param result Вказівник на структуру для збереження розрахованих результатів.
 * @return esp_err_t ESP_OK у разі успішного проходження тесту, або код помилки.
 */
esp_err_t psram_run_benchmark(size_t buffer_size, psram_benchmark_result_t *result);

#ifdef __cplusplus
}
#endif

#endif // PSRAM_BENCHMARK_H
