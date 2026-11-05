#ifndef OSCILLOSCOPE_TRACE_H
#define OSCILLOSCOPE_TRACE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Дискретна вибірка сигналу з цифрового осцилографа.
 */
typedef struct {
    double time_s;     /* Часова мітка відліку в секундах */
    double voltage_v;  /* Миттєве значення напруги у вольтах */
} sample_point_t;

/**
 * @brief Напрямок перехідного процесу (нахил фронту сигналу).
 */
typedef enum {
    EDGE_SLOPE_RISING = 0, /* Наростаючий фронт (перехід від базової лінії до полиці) */
    EDGE_SLOPE_FALLING     /* Спадний фронт (перехід від верхнього рівня до бази) */
} edge_slope_t;

/**
 * @brief Буфер часової послідовності оцифрованої осцилограми.
 */
typedef struct {
    sample_point_t *samples; /* Динамічний масив вибірок */
    size_t count;            /* Поточна кількість відліків */
    size_t capacity;         /* Виділена місткість буфера */
} oscilloscope_trace_t;

/**
 * @brief Ініціалізація структури осцилограми з резервуванням початкової місткості.
 * @param trace Вказівник на структуру осцилограми.
 * @param initial_capacity Початковий резерв кількості відліків (якщо 0, призначається 64).
 * @return true у разі успіху, false при помилці виділення пам'яті або нульовому вказівнику.
 */
bool trace_init(oscilloscope_trace_t *trace, size_t initial_capacity);

/**
 * @brief Звільнення динамічної пам'яті буфера осцилограми.
 * @param trace Вказівник на структуру осцилограми.
 */
void trace_free(oscilloscope_trace_t *trace);

/**
 * @brief Очищення вибірок осцилограми без вивільнення виділеної пам'яті.
 * @param trace Вказівник на структуру осцилограми.
 */
void trace_clear(oscilloscope_trace_t *trace);

/**
 * @brief Додавання нового відліку (часова мітка, напруга) до осцилограми.
 * @param trace Вказівник на структуру осцилограми.
 * @param time_s Часова мітка в секундах.
 * @param voltage_v Напруга у вольтах.
 * @return true якщо точку успішно додано, false у разі помилки виділення пам'яті.
 */
bool trace_add_sample(oscilloscope_trace_t *trace, double time_s, double voltage_v);

/**
 * @brief Перевірка строгої монотонності часової шкали вибірки (відсутність інверсій та збігів).
 * @param trace Вказівник на осцилограму.
 * @return true якщо time[i] > time[i-1] для всіх точок; false у разі порушення або помилки.
 */
bool trace_validate_monotonicity(const oscilloscope_trace_t *trace);

/**
 * @brief Фільтрація поодиноких імпульсних викидів АЦП (spikes) амплітудним фільтром сусідів.
 * @param trace Вказівник на осцилограму.
 * @param max_spike_delta_v Поріг амплітудного стрибка для детекції викиду (у вольтах).
 */
void trace_filter_outliers(oscilloscope_trace_t *trace, double max_spike_delta_v);

/**
 * @brief Визначення квазістаціонарних рівнів напруги (базової лінії 0% та верхньої полиці 100%).
 * @param trace Вказівник на осцилограму.
 * @param out_baseline_v Вихідний вказівник для напруги базової лінії (0%).
 * @param out_steady_v Вихідний вказівник для напруги полиці імпульсу (100%).
 * @return true якщо рівні успішно обчислено та амплітуда достатня, false інакше.
 */
bool trace_calculate_amplitude_levels(const oscilloscope_trace_t *trace,
                                      double *out_baseline_v,
                                      double *out_steady_v);

/**
 * @brief Субдискретне визначення часової мітки перетину заданої напруги лінійною інтерполяцією.
 * @param trace Вказівник на осцилограму.
 * @param target_voltage Цільовий пороговий рівень напруги у вольтах.
 * @param slope Очікуваний напрямок перетину фронту (наростаючий або спадний).
 * @param out_time_s Вихідний вказівник для розрахованого моменту часу.
 * @return true якщо знайдено перетин рівня, false якщо поріг не перетинається сигналом.
 */
bool trace_find_threshold_crossing_time(const oscilloscope_trace_t *trace,
                                        double target_voltage,
                                        edge_slope_t slope,
                                        double *out_time_s);

/**
 * @brief Обчислення часу наростання фронту сигналу (rise time) між відносними рівнями.
 * @param trace Вказівник на осцилограму.
 * @param lower_fraction Нижня частка амплітуди (типово 0.10 для 10%).
 * @param upper_fraction Верхня частка амплітуди (типово 0.90 для 90%).
 * @param out_rise_time_s Вихідний вказівник для розрахованої тривалості наростання у секундах.
 * @return true у разі успішного розрахунку, false якщо фронт некоректний або відсутній.
 */
bool trace_calculate_rise_time(const oscilloscope_trace_t *trace,
                               double lower_fraction,
                               double upper_fraction,
                               double *out_rise_time_s);

#ifdef __cplusplus
}
#endif

#endif /* OSCILLOSCOPE_TRACE_H */
