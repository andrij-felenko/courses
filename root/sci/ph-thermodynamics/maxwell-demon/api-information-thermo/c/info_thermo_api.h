/* info_thermo_api.h - Програмний інтерфейс розрахунку термодинаміки інформації (C) */
#ifndef INFO_THERMO_API_H
#define INFO_THERMO_API_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include <stdint.h>

/* Фізичні константи */
#define INFO_THERMO_KB          1.380649e-23
#define INFO_THERMO_ELEM_CHARGE 1.602176634e-19
#define INFO_THERMO_LN2         0.6931471805599453

/* Коди помилок API */
typedef enum {
    INFO_THERMO_OK = 0,
    INFO_THERMO_ERR_INVALID_TEMP = -1,
    INFO_THERMO_ERR_NEGATIVE_BITS = -2,
    INFO_THERMO_ERR_NULL_POINTER  = -3
} InfoThermoError;

/* Вхідні параметри інформаційного двигуна */
typedef struct {
    double temperature_K;     /* Температура теплостата, Кельвіни (> 0) */
    double mutual_info_bits;  /* Накопичена взаємна інформація, біти (>= 0) */
    double free_energy_diff_J;/* Зміна вільної енергії ΔF, Дж */
    double efficiency_factor; /* Коефіцієнт реальної ефективності (0.0 < eta <= 1.0) */
} InfoEngineParams;

/* Результати розрахунку термодинамічного балансу */
typedef struct {
    double max_work_theoretical_J; /* Теоретичний максимум вилученої роботи, Дж */
    double actual_work_extracted_J;/* Реально вилучена робота з урахуванням ккд, Дж */
    double min_erasure_heat_J;     /* Мінімальне тепло стирання Ландауера, Дж */
    double min_erasure_heat_meV;   /* Тепло стирання в меВ */
    double net_entropy_universe_JK;/* Чиста зміна ентропії Всесвіту, Дж/К (>= 0) */
} InfoEngineResult;

/**
 * @brief Обчислює термодинамічні межі вилучення роботи та стирання пам'яті.
 * @param params Вказівник на структуру із вхідними параметрами.
 * @param result Вказівник на структуру для збереження результатів.
 * @return INFO_THERMO_OK у разі успіху, або відповідний код помилки.
 */
InfoThermoError info_thermo_calculate(const InfoEngineParams *params, InfoEngineResult *result);

/**
 * @brief Обчислює межу Ландауера для заданої температури в електронвольтах.
 * @param temp_K Температура в Кельвінах.
 * @return Значення межі Ландауера в меВ, або -1.0 у разі некоректної температури.
 */
double info_thermo_landauer_limit_meV(double temp_K);

#ifdef __cplusplus
}
#endif

#endif /* INFO_THERMO_API_H */
