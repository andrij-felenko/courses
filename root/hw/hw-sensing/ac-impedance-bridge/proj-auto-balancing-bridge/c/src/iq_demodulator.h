#ifndef IQ_DEMODULATOR_H
#define IQ_DEMODULATOR_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Результат цифрового квадратурного детектування (I/Q вектори).
 */
typedef struct {
    double i; /**< Синфазна складова (In-phase) */
    double q; /**< Квадратурна складова (Quadrature) */
} iq_vector_t;

/**
 * @brief Фізичні результати обчислення комплексного імпедансу досліджуваного зразка.
 */
typedef struct {
    double r_real;       /**< Дійсна частина (активний опір R, Ом) */
    double x_imag;       /**< Уявна частина (реактивний опір X, Ом) */
    double z_magnitude;  /**< Модуль повного імпедансу |Z|, Ом */
    double phase_rad;    /**< Фазовий кут імпедансу, радіани */
    double phase_deg;    /**< Фазовий кут імпедансу, градуси */
    double dissipation;  /**< Тангенс кута втрат (D = |R / X|) */
    double quality_fac;  /**< Добротність (Q = |X / R|) */
} impedance_result_t;

/**
 * @brief Стан та параметри конфігурації квадратурного демодулятора.
 */
typedef struct {
    double sample_rate_hz;    /**< Частота дискретизації АЦП, Гц */
    double signal_freq_hz;    /**< Частота тестового синусоїдального сигналу, Гц */
    size_t samples_per_period; /**< Кількість відліків на один повний період */
    size_t total_samples;     /**< Кількість накопичених відліків у поточному вікні */
    
    /* Накопичувальні інтегратори напруги */
    double sum_v_i;
    double sum_v_q;
    
    /* Накопичувальні інтегратори струму */
    double sum_i_i;
    double sum_i_q;
} iq_demodulator_t;

/**
 * @brief Ініціалізація стану демодулятора для заданих параметрів частоти.
 * @param demod Вказівник на структуру стану.
 * @param sample_rate_hz Частота вибірок АЦП.
 * @param signal_freq_hz Частота вимірювального сигналу.
 * @return true у разі коректних параметрів, false якщо параметри неприпустимі.
 */
bool iq_demodulator_init(iq_demodulator_t *demod, double sample_rate_hz, double signal_freq_hz);

/**
 * @brief Скидання накопичувачів перед новим вимірювальним вікном.
 */
void iq_demodulator_reset(iq_demodulator_t *demod);

/**
 * @brief Потокова обробка пари відліків напруги та струму з АЦП.
 * @param demod Вказівник на структуру стану.
 * @param v_sample Миттєвий відлік напруги (В).
 * @param i_sample Миттєвий відлік струму (А).
 */
void iq_demodulator_feed(iq_demodulator_t *demod, double v_sample, double i_sample);

/**
 * @brief Пакетна обробка масиву відліків АЦП цілої кількості періодів.
 * @param demod Вказівник на стан.
 * @param v_samples Масив вибірок напруги.
 * @param i_samples Масив вибірок струму.
 * @param count Кількість вибірок у масивах.
 */
void iq_demodulator_process_block(iq_demodulator_t *demod, 
                                 const double *v_samples, 
                                 const double *i_samples, 
                                 size_t count);

/**
 * @brief Розрахунок комплексного імпедансу на основі накопичених I/Q інтегралів.
 * @param demod Вказівник на стан.
 * @param result Вихідна структура з обчисленими параметрами.
 * @return true якщо розрахунок успішний, false якщо струм занадто малий (ділення на 0).
 */
bool iq_demodulator_calculate(const iq_demodulator_t *demod, impedance_result_t *result);

#ifdef __cplusplus
}
#endif

#endif /* IQ_DEMODULATOR_H */
