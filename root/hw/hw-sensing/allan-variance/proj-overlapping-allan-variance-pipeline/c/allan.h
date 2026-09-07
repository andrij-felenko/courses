#ifndef ALLAN_H
#define ALLAN_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Типи домінуючого стохастичного шуму для розрахунку ступенів вільності EDF.
 */
typedef enum {
    ALLAN_NOISE_WFM = 0,  /* Білий шум частоти / кутове випадкове блукання (ARW) */
    ALLAN_NOISE_FFM,      /* Флікер-шум частоти / нестабільність зсуву нуля (BI) */
    ALLAN_NOISE_RWFM      /* Випадкове блукання частоти / блукання швидкості (RRW) */
} allan_noise_type_t;

/**
 * @brief Структура одиничної точки результату розрахунку девіації Аллана.
 */
typedef struct {
    double tau;           /* Інтервал усереднення (кластер) у секундах */
    double adev;          /* Оцінка девіації Аллана */
    double adev_min;      /* Нижня довірча межа (95% за хі-квадрат) */
    double adev_max;      /* Верхня довірча межа (95% за хі-квадрат) */
    double edf;           /* Еквівалентні ступені вільності (EDF) */
    size_t num_pairs;     /* Фактична кількість перекривних різниць */
} allan_point_t;

/**
 * @brief Обчислення одновимірного масиву інтегральних префіксних сум (фазових даних).
 * 
 * @param rate Масив кутової швидкості або частотних відліків y_k довжиною n.
 * @param n Кількість відліків вибірки.
 * @param dt Період дискретизації вихідного сигналу tau0 в секундах.
 * @param phase Вихідний масив інтегрованих фазових відліків x_k довжиною (n + 1).
 */
void allan_cumsum(const double *rate, size_t n, double dt, double *phase);

/**
 * @brief Апроксимація числа еквівалентних ступенів вільності (EDF).
 * 
 * @param n Кількість відліків у вихідній послідовності.
 * @param m Множник кластеризації (tau = m * dt).
 * @param noise Тип домінуючого шуму.
 * @return Розраховане число EDF (не менше 1.0).
 */
double allan_approx_edf(size_t n, size_t m, allan_noise_type_t noise);

/**
 * @brief Розрахунок 95% довірчого інтервалу девіації Аллана через розподіл хі-квадрат.
 * 
 * @param adev Точкова оцінка девіації Аллана.
 * @param edf Кількість ступенів вільності.
 * @param ci_min Вказівник на вихідну нижню межу.
 * @param ci_max Вказівник на вихідну верхню межу.
 */
void allan_confidence_interval(double adev, double edf, double *ci_min, double *ci_max);

/**
 * @brief Обчислення точки перекривної девіації Аллана (OAVAR) за час O(N) з O(1) на пару.
 * 
 * @param phase Масив інтегрованих фазових даних довжиною n_phase = N + 1.
 * @param n_phase Довжина масиву phase.
 * @param dt Базовий період дискретизації tau0.
 * @param m Коефіцієнт кластеризації.
 * @param out Структура для запису результату.
 * @return 0 при успіху, -1 при некоректних аргументах.
 */
int allan_calc_oavar(const double *phase, size_t n_phase, double dt, size_t m, allan_point_t *out);

/**
 * @brief Обчислення точки модифікованої девіації Аллана (MVAR).
 * 
 * @param phase Масив інтегрованих фазових даних довжиною n_phase = N + 1.
 * @param n_phase Довжина масиву phase.
 * @param dt Базовий період дискретизації tau0.
 * @param m Коефіцієнт кластеризації.
 * @param out Структура для запису результату.
 * @return 0 при успіху, -1 при некоректних аргументах.
 */
int allan_calc_mvar(const double *phase, size_t n_phase, double dt, size_t m, allan_point_t *out);

#ifdef __cplusplus
}
#endif

#endif /* ALLAN_H */
