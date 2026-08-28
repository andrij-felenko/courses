/**
 * @file event_filter.h
 * @brief Публічний контракт модуля фільтрації дискретних подій N-з-M
 * @version 2.4.0
 */

#ifndef EVENT_FILTER_H
#define EVENT_FILTER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Максимальна довжина вікна для багатослівного фільтра в бітах */
#define EVENT_FILTER_MAX_MULTIWORD_BITS  1024U
#define EVENT_FILTER_WORD_BITS           32U
#define EVENT_FILTER_WORDS_CAPACITY      (EVENT_FILTER_MAX_MULTIWORD_BITS / EVENT_FILTER_WORD_BITS)

/**
 * @brief Діагностичні прапорці стану вимірювального каналу
 */
typedef enum {
    EVENT_FILTER_STATUS_OK              = 0x00, /**< Канал функціонує нормально */
    EVENT_FILTER_STATUS_STUCK_ACTIVE    = 0x01, /**< Зафіксовано залипання в активному стані */
    EVENT_FILTER_STATUS_STUCK_INACTIVE  = 0x02, /**< Зафіксовано залипання в пасивному стані */
    EVENT_FILTER_STATUS_HIGH_NOISE_WARN = 0x04  /**< Високий рівень імпульсного шуму */
} event_filter_status_t;

/**
 * @brief Структура параметрів ініціалізації фільтра N-з-M
 */
typedef struct {
    uint16_t m_window;          /**< Розмір ковзного вікна (кількість відліків) */
    uint16_t n_on;              /**< Поріг активації: кількість 1 >= N_on перемикає вихід у 1 */
    uint16_t n_off;             /**< Поріг деактивації: кількість 1 <= N_off скидає вихід у 0 */
    uint32_t max_dwell_samples; /**< Максимальна кількість відліків без зміни стану до аварії (0 = вимкнено) */
} event_filter_config_t;

/**
 * @brief Дескриптор стану швидкісного однослівного фільтра (M <= 32)
 */
typedef struct {
    uint32_t history;           /**< Бітовий зсувний регістр історії відліків */
    uint32_t window_mask;       /**< Маска активних бітів вікна: (1 << M) - 1 */
    uint32_t dwell_counter;     /**< Лічильник відліків у поточному стані */
    uint32_t max_dwell_samples; /**< Поріг фіксації залипання */
    uint32_t glitch_count;      /**< Лічильник відкинутих шумових сплесків */
    uint8_t  m_window;          /**< Розмір вікна M (1..32) */
    uint8_t  n_on;              /**< Поріг активації */
    uint8_t  n_off;             /**< Поріг деактивації */
    uint8_t  status_flags;      /**< Поточні прапорці діагностики */
    bool     output_state;      /**< Поточний валідний відфільтрований стан */
} event_filter_fast32_t;

/**
 * @brief Дескриптор стану багатослівного фільтра для великих вікон (M від 65 до 1024)
 */
typedef struct {
    uint32_t words[EVENT_FILTER_WORDS_CAPACITY]; /**< Статичний бітовий масив історії */
    uint32_t dwell_counter;     /**< Лічильник перебування в незмінному стані */
    uint32_t max_dwell_samples; /**< Поріг фіксації залипання */
    uint32_t glitch_count;      /**< Лічильник придушених завад */
    uint16_t m_window;          /**< Загальна довжина вікна в бітах */
    uint16_t n_on;              /**< Поріг активації */
    uint16_t n_off;             /**< Поріг деактивації */
    uint16_t head_index;        /**< Циклічний покажчик позиції запису нового біта */
    uint16_t current_popcount;  /**< Поточна кількість одиниць у вікні (O(1) трекінг) */
    uint8_t  status_flags;      /**< Діагностичні прапорці */
    bool     output_state;      /**< Поточний стан виходу */
} event_filter_multiword_t;

/* --- Публічний API швидкісного фільтра (M <= 32) --- */

void event_filter_fast32_init(event_filter_fast32_t *f, 
                              const event_filter_config_t *cfg, 
                              bool initial_raw_level);

bool event_filter_fast32_update(event_filter_fast32_t *f, bool raw_sample);

bool event_filter_fast32_get_state(const event_filter_fast32_t *f);

uint8_t event_filter_fast32_get_count(const event_filter_fast32_t *f);

uint8_t event_filter_fast32_get_diagnostics(const event_filter_fast32_t *f, uint32_t *out_glitches);

/* --- Публічний API багатослівного фільтра (M до 1024) --- */

void event_filter_multiword_init(event_filter_multiword_t *f, 
                                 const event_filter_config_t *cfg, 
                                 bool initial_raw_level);

bool event_filter_multiword_update(event_filter_multiword_t *f, bool raw_sample);

bool event_filter_multiword_get_state(const event_filter_multiword_t *f);

uint16_t event_filter_multiword_get_count(const event_filter_multiword_t *f);

#ifdef __cplusplus
}
#endif

#endif /* EVENT_FILTER_H */
