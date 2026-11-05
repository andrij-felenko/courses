/**
 * @file pogo_pin_monitor.h
 * @brief Інтерфейс модуля моніторингу стабільності контакту Pogo Pin та обліку мікророзривів.
 */

#ifndef POGO_PIN_MONITOR_H
#define POGO_PIN_MONITOR_H

#include <stdint.h>
#include <stdbool.h>

#define POGO_MAX_EVENTS 64

/**
 * @brief Конфігурація параметрів виявлення мікророзривів.
 */
typedef struct {
    uint32_t min_glitch_duration_us;  ///< Мінімальна тривалість розриву для реєстрації (мкс)
    uint32_t debounce_filter_us;     ///< Поріг відсікання високочастотного шуму (мкс)
    uint32_t sampling_period_ms;     ///< Період опитування або таймера (мс)
} pogo_config_t;

/**
 * @brief Статистика роботи та надійності контакту.
 */
typedef struct {
    uint32_t total_cycles;            ///< Загальна кількість перевірок або періодів випробування
    uint32_t contact_open_events;     ///< Кількість зафіксованих подій розмикання контакту
    uint32_t total_downtime_us;       ///< Сумарна тривалість перебування у розімкненому стані (мкс)
    uint32_t max_glitch_duration_us;  ///< Найдовший зафіксований мікророзрив (мкс)
    double contact_loss_percent;      ///< Відсоток часу відсутності надійного електричного контакту
} pogo_stats_t;

/**
 * @brief Стан монітора Pogo Pin.
 */
typedef struct {
    pogo_config_t config;             ///< Налаштування монітора
    pogo_stats_t stats;               ///< Накопичена статистика
    bool current_contact_state;       ///< Поточний фізичний стан: true - замкнено, false - розімкнено
    uint32_t last_transition_timestamp_us; ///< Часова мітка останньої зміни стану (мкс)
} pogo_monitor_t;

/**
 * @brief Ініціалізує контекст монітора Pogo Pin.
 */
void pogo_monitor_init(pogo_monitor_t *monitor, const pogo_config_t *config);

/**
 * @brief Обробник зміни логічного рівня на контакті (виклик із переривання GPIO).
 * @param monitor Вказівник на структуру монітора.
 * @param pin_state Поточний стан входу: true - логічний нуль/земля (замкнено), false - розімкнено.
 * @param current_timestamp_us Поточний час таймера у мікросекундах.
 */
void pogo_monitor_handle_edge(pogo_monitor_t *monitor, bool pin_state, uint32_t current_timestamp_us);

/**
 * @brief Оновлює відсоток втрати контакту та завершує розрахунок статистики.
 */
void pogo_monitor_update_stats(pogo_monitor_t *monitor, uint32_t total_test_duration_ms);

/**
 * @brief Виводить підсумковий діагностичний звіт про вібростійкість контакту.
 */
void pogo_monitor_print_report(const pogo_monitor_t *monitor);

#endif /* POGO_PIN_MONITOR_H */
