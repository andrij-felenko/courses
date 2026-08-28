#ifndef TRAFFIC_SHAPER_H
#define TRAFFIC_SHAPER_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct shaper_internal shaper_t;

/**
 * Створення та ініціалізація нового екземпляра Token Bucket Shaper.
 * 
 * @param config Вказівник на структуру конфігурації.
 * @return Вказівник на створений екземпляр або NULL при помилці.
 */
shaper_t* shaper_create(const shaper_config_t *config);

/**
 * Звільнення пам'яті та ресурсів шейпера.
 */
void shaper_destroy(shaper_t *shaper);

/**
 * Перераховує баланс жетонів на основі поточного таймера високої точності.
 * 
 * @param shaper Екземпляр шейпера.
 * @param now_us Поточний час у мікросекундах.
 */
void shaper_update_tokens(shaper_t *shaper, uint64_t now_us);

/**
 * Головний метод обробки пакету.
 * 
 * @param shaper Екземпляр шейпера.
 * @param packet_len_bytes Довжина вхідного пакета у байтах.
 * @param now_us Поточний час у мікросекундах.
 * @return Код результату (SHAPER_OK, SHAPER_QUEUED, SHAPER_DROP_*).
 */
int shaper_process_packet(shaper_t *shaper, size_t packet_len_bytes, uint64_t now_us);

/**
 * Обчислює час затримки у мікросекундах, необхідний для накопичення жетонів під пакет.
 */
uint64_t shaper_get_wait_time_us(const shaper_t *shaper, size_t packet_len_bytes, uint64_t now_us);

/**
 * Повертає поточний баланс жетонів (у байтах).
 */
uint64_t shaper_get_tokens(const shaper_t *shaper);

#ifdef __cplusplus
}
#endif

#endif // TRAFFIC_SHAPER_H
