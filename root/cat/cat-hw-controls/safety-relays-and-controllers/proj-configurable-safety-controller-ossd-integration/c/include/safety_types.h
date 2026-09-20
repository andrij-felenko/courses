#ifndef SAFETY_TYPES_H
#define SAFETY_TYPES_H

#include <stdint.h>
#include <stdbool.h>

// Стан безпеки контролера (Safety State)
typedef enum {
    SAFETY_STATE_OK = 0,          // Штатний нормальний стан (безпечна робота)
    SAFETY_STATE_MUTING_ACTIVE,   // Активний режим мутингу (маскування світлової завіси)
    SAFETY_STATE_TRIPPED,         // Спрацювання захисту (виходи розімкнені)
    SAFETY_STATE_FAULT_CROSS_SHORT,// Помилка: перехресне коротке замикання OSSD
    SAFETY_STATE_FAULT_EDM_TIMEOUT, // Помилка: залипання/таймаут силового контактора (EDM)
    SAFETY_STATE_FAULT_MUTING_SEQ  // Помилка: порушення часового вікна або послідовності Muting
} safety_state_t;

// Структура для зберігання та фільтрації двоканальних сигналів OSSD
typedef struct {
    bool channel_a_raw;        // Сирий аналоговий/дискретний сигнал каналу A
    bool channel_b_raw;        // Сирий аналоговий/дискретний сигнал каналу B
    bool channel_a_filtered;   // Фільтрований сигнал каналу A (ігнорування коротких тестових спалахів)
    bool channel_b_filtered;   // Фільтрований сигнал каналу B
    uint8_t test_pulse_counter_a; // Лічильник коротких тестових імпульсів 0 В каналу A
    uint8_t test_pulse_counter_b; // Лічильник коротких тестових імпульсів 0 В каналу B
    uint32_t discrepancy_timer_ms; // Таймер неузгодженості між каналами A та B
    bool fault_cross_short;    // Прапорець виявлення перехресного замикання
} safety_ossd_t;

// Структура моніторингу зовнішніх пристроїв (External Device Monitoring - EDM)
typedef struct {
    bool edm_feedback_nc;      // Вхід зворотного зв'язку (НЗ-контакти силових контакторів)
    bool expected_state;       // Очікуваний стан (true = контактори мають бути відключені / NC замкнені)
    uint32_t edm_timer_ms;     // Таймер вимірювання затримки спрацювання контакторів
    uint32_t max_allowed_delay_ms; // Максимально допустима затримка контактора (напр. 200 мс)
    bool edm_fault;            // Прапорець апаратної відмови контактора
} safety_edm_t;

// Структура контролю часових вікон мутингу (Muting)
typedef struct {
    bool sensor_m1;            // Вхідний датчик мутингу M1
    bool sensor_m2;            // Вхідний датчик мутингу M2
    bool muting_active;        // Активний статус дозволеного маскування завіси
    uint32_t m1_activation_time_ms; // Час спрацювання датчика M1
    uint32_t m2_activation_time_ms; // Час спрацювання датчика M2
    uint32_t max_sequence_gap_ms;  // Максимальний допуск затримки між M1 та M2 (напр. 3000 мс)
    bool muting_fault;         // Прапорець помилки часового вікна мутингу
} safety_muting_t;

// Головний контекст контролера безпеки
typedef struct {
    safety_state_t state;      // Поточний загальний стан контролера
    safety_ossd_t ossd;        // Підсистема OSSD
    safety_edm_t edm;          // Підсистема EDM
    safety_muting_t muting;    // Підсистема Muting
    bool ossd_output_enable;   // Підсумковий вихід дозволу роботи (OSSD_OUT)
} safety_controller_t;

#endif // SAFETY_TYPES_H
