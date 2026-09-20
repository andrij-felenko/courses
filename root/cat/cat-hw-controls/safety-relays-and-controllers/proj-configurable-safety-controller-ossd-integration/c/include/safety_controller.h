#ifndef SAFETY_CONTROLLER_H
#define SAFETY_CONTROLLER_H

#include "safety_types.h"

// Константи часових параметрів системи безпеки (у мілісекундах)
#define SAFETY_DISCREPANCY_TIMEOUT_MS  50U    // Максимально допустимий час неузгодженості OSSD A/B
#define SAFETY_EDM_TIMEOUT_MS          200U   // Таймаут спрацювання НЗ-контактів контакторів
#define SAFETY_MUTING_MAX_GAP_MS       3000U  // Максимальне часове вікно між спрацюванням M1 та M2
#define SAFETY_TEST_PULSE_MAX_TICKS    3U     // Кількість тактів для відфільтровування тестових імпульсів

// Функції ініціалізації та обробки контролера безпеки
void safety_controller_init(safety_controller_t *ctrl);

// Потактова обробка сигналів OSSD з фільтрацією тестових спалахів та перевіркою неузгодженості
void safety_process_ossd(safety_controller_t *ctrl, bool raw_a, bool raw_b, uint32_t delta_ms);

// Контроль зворотного зв'язку силових контакторів EDM
void safety_process_edm(safety_controller_t *ctrl, bool feedback_nc, uint32_t delta_ms);

// Перевірка часових вікон та послідовності датчиків Muting
void safety_process_muting(safety_controller_t *ctrl, bool sensor_m1, bool sensor_m2, uint32_t system_time_ms);

// Головний крок автомата станів безпеки
void safety_controller_update(safety_controller_t *ctrl, uint32_t delta_ms, uint32_t system_time_ms);

#endif // SAFETY_CONTROLLER_H
