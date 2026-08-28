#ifndef ALARM_RATIONALIZER_H
#define ALARM_RATIONALIZER_H

#include "alarm_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура диспетчера тривог.
 */
typedef struct {
    AlarmConfig_t configs[MAX_ALARMS];
    AlarmRuntime_t runtimes[MAX_ALARMS];
    size_t count;
    uint32_t current_sys_state;

    /* Метрики частоти тривог за ковзне вікно (Alarm Flood Detector) */
    uint64_t rate_history[MAX_ALARMS * 2];
    size_t rate_head;
    size_t rate_tail;
    size_t alarms_in_rate_window;
    bool is_alarm_flood_active;

    /* Статистика надійності HMI */
    uint32_t total_trips;
    uint32_t total_acks;
    uint32_t total_suppressions;
    uint32_t total_chatter_events;
} AlarmRationalizer_t;

/**
 * @brief Ініціалізація диспетчера тривог.
 */
void alarm_rationalizer_init(AlarmRationalizer_t *ar);

/**
 * @brief Реєстрація раціоналізованої конфігурації тривоги.
 * @return true при успішній реєстрації, false якщо перевищено MAX_ALARMS.
 */
bool alarm_rationalizer_register(AlarmRationalizer_t *ar, const AlarmConfig_t *cfg);

/**
 * @brief Встановлення поточного експлуатаційного стану системи.
 */
void alarm_rationalizer_set_system_state(AlarmRationalizer_t *ar, uint32_t sys_state, uint64_t now_ms);

/**
 * @brief Оновлення вхідного значення сигналу для конкретної тривоги.
 */
void alarm_rationalizer_update_value(AlarmRationalizer_t *ar, uint16_t alarm_id, float value, uint64_t now_ms);

/**
 * @brief Головна функція такту обчислення автомата станів тривог за ISA-18.2.
 */
void alarm_rationalizer_process(AlarmRationalizer_t *ar, uint64_t now_ms);

/**
 * @brief Квитування (підтвердження) тривоги оператором.
 */
bool alarm_rationalizer_ack(AlarmRationalizer_t *ar, uint16_t alarm_id, uint64_t now_ms);

/**
 * @brief Тимчасове відкладення тривоги (Shelve) оператором на вказану тривалість.
 */
bool alarm_rationalizer_shelve(AlarmRationalizer_t *ar, uint16_t alarm_id, uint32_t duration_ms, uint64_t now_ms);

/**
 * @brief Ручне повернення тривоги з відкладеного стану (Unshelve).
 */
bool alarm_rationalizer_unshelve(AlarmRationalizer_t *ar, uint16_t alarm_id, uint64_t now_ms);

/**
 * @brief Отримання списку активних непідтверджених та підтверджених тривог для відображення на HMI.
 * @param out_ids Буфер для збереження ID тривог.
 * @param max_out Розмір вихідного буфера.
 * @return Кількість записаних тривог (відсортованих за спаданням пріоритету).
 */
size_t alarm_rationalizer_get_active_hmi_alarms(const AlarmRationalizer_t *ar, uint16_t *out_ids, size_t max_out);

#ifdef __cplusplus
}
#endif

#endif /* ALARM_RATIONALIZER_H */
