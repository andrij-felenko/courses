#ifndef ALLAN_VARIANCE_H
#define ALLAN_VARIANCE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Результат розрахунку девіації Аллана для одного значення tau.
 */
typedef struct {
    double tau;          /**< Час усереднення, с */
    size_t m;            /**< Коефіцієнт кластеризації (довжина вікна у відліках) */
    double adev;         /**< Перекривна девіація Аллана (OADEV), од. вимірювання */
    double mdev;         /**< Модифікована девіація Аллана (MDEV), од. вимірювання */
    double edf;          /**< Еквівалентна кількість ступенів вільності (EDF) */
    double adev_lower;   /**< Нижня 95%-ва межа довірчого інтервалу ADEV */
    double adev_upper;   /**< Верхня 95%-ва межа довірчого інтервалу ADEV */
} AllanResult;

/**
 * @brief Розрахунок масиву префіксних сум фазового інтеграла (інтегрування часового ряду).
 *
 * @param y Вхідний масив відліків сенсора (наприклад, кутова швидкість у град/с).
 * @param n Кількість відліків у масиві y.
 * @param dt Період дискретизації сенсора, с.
 * @param theta_out Вихідний масив інтегральних сум фази довжиною (n + 1). Повинен бути виділений заздалегідь.
 */
void allan_compute_phase(const double *y, size_t n, double dt, double *theta_out);

/**
 * @brief Розрахунок перекривної девіації Аллана (OADEV) за фіксованого кроку m через префіксні суми фази.
 *
 * @param theta Масив префіксних сум фази довжиною (n + 1).
 * @param n Кількість початкових відліків y.
 * @param dt Період дискретизації, с.
 * @param m Розмір кластера у відліках.
 * @return Розраховане значення OADEV (квадратний корінь із OAVAR).
 */
double allan_compute_oadev(const double *theta, size_t n, double dt, size_t m);

/**
 * @brief Розрахунок модифікованої девіації Аллана (MDEV) за кроку m.
 *
 * @param theta Масив префіксних сум фази довжиною (n + 1).
 * @param n Кількість початкових відліків y.
 * @param dt Період дискретизації, с.
 * @param m Розмір кластера у відліках.
 * @return Розраховане значення MDEV.
 */
double allan_compute_mdev(const double *theta, size_t n, double dt, size_t m);

/**
 * @brief Оцінка ступенів вільності EDF та розрахунок 95%-го довірчого інтервалу за розподілом хі-квадрат.
 *
 * @param adev Точкова оцінка девіації Аллана.
 * @param n Кількість вихідних відліків.
 * @param m Розмір кластера у відліках.
 * @param out_edf Покажчик для запису розрахованого EDF.
 * @param out_lower Покажчик для запису нижньої межі (95%).
 * @param out_upper Покажчик для запису верхньої межі (95%).
 */
void allan_compute_confidence_interval(double adev, size_t n, size_t m,
                                       double *out_edf, double *out_lower, double *out_upper);

/**
 * @brief Повний розрахунок кривої девіації Аллана по логарифмічній сітці tau.
 *
 * @param y Вхідний часовий ряд вимірювань.
 * @param n Кількість відліків.
 * @param dt Період дискретизації, с.
 * @param m_list Масив коефіцієнтів кластеризації m.
 * @param num_taus Кількість точок tau у масиві m_list.
 * @param results_out Вихідний масив результатів розміром num_taus.
 * @return true у разі успішного розрахунку, false у разі невалідних вхідних параметрів.
 */
bool allan_analyze_pipeline(const double *y, size_t n, double dt,
                            const size_t *m_list, size_t num_taus,
                            AllanResult *results_out);

#ifdef __cplusplus
}
#endif

#endif /* ALLAN_VARIANCE_H */
