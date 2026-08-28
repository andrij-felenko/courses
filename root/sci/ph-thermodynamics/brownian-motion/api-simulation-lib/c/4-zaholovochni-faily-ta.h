#ifndef BROWNIAN_SIM_H
#define BROWNIAN_SIM_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Заповнює структуру конфігурації стандартними фізичними параметрами (вода, 300K, 1 мкм).
 * @param config Вказівник на структуру конфігурації.
 * @return BROWNIAN_SUCCESS або BROWNIAN_ERR_NULL_POINTER.
 */
int brownian_config_default(BrownianConfig *config);

/**
 * @brief Обчислює теоретичний коефіцієнт дифузії Стокса—Ейнштейна.
 * @param temperature_k Температура термостату, К.
 * @param viscosity_pas Динамічна в'язкість рідини, Па·с.
 * @param radius_m Гідродинамічний радіус частинки, м.
 * @param out_diff_coeff Вказівник на змінну для запису результату (м²/с).
 * @return BROWNIAN_SUCCESS або BROWNIAN_ERR_INVALID_PARAM.
 */
int brownian_calculate_theoretical_D(double temperature_k,
                                     double viscosity_pas,
                                     double radius_m,
                                     double *out_diff_coeff);

/**
 * @brief Запускає симуляцію ансамблю броунівських частинок.
 * @param config Вказівник на параметри конфігурації.
 * @param out_states Виділений буфер для зберігання станів.
 * @return BROWNIAN_SUCCESS або відповідний код помилки.
 */
int brownian_simulate_ensemble(const BrownianConfig *config,
                               BrownianState *out_states);

/**
 * @brief Обчислює ансамблевий MSD та виконує лінійний аналіз дифузії.
 * @param config Параметри симуляції.
 * @param states Буфер згенерованих станів.
 * @param out_result Структура результату.
 * @return BROWNIAN_SUCCESS або код помилки.
 */
int brownian_analyze_msd(const BrownianConfig *config,
                         const BrownianState *states,
                         BrownianMsdResult *out_result);

/**
 * @brief Звільняє динамічну пам'ять, виділену всередині структури BrownianMsdResult.
 * @param result Вказівник на структуру результату.
 */
void brownian_free_msd_result(BrownianMsdResult *result);

#ifdef __cplusplus
}
#endif

#endif /* BROWNIAN_SIM_H */
