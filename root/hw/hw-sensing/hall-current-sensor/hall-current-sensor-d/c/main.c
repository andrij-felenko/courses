#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/**
 * @brief Структура конфігурації та стану сенсора струму Холла.
 */
typedef struct {
    uint32_t adc_max_ticks;      /* Максимальне значення АЦП (4095 для 12-біт) */
    float    vref_volts;         /* Опорна напруга АЦП у вольтах (наприклад, 3.3f) */
    float    sensitivity_mv_a;   /* Чутливість сенсора в мВ/А (наприклад, 100.0f для 100 мВ/А) */
    float    zero_offset_volts;  /* Напруга спокою при I=0 (номінально VCC/2) */
    float    filter_alpha;       /* Коефіцієнт EMA фільтрації (0.01 .. 1.0) */
    float    filtered_current_a; /* Згладжене значення струму в амперах */
    bool     is_calibrated;      /* Прапорець успішного калібрування нуля */
} HallCurrentSensor;

/**
 * @brief Ініціалізація структури давача струму.
 */
void hall_sensor_init(HallCurrentSensor *sensor,
                      uint32_t adc_max_ticks,
                      float vref_volts,
                      float sensitivity_mv_a,
                      float filter_alpha)
{
    sensor->adc_max_ticks = adc_max_ticks;
    sensor->vref_volts = vref_volts;
    sensor->sensitivity_mv_a = sensitivity_mv_a;
    sensor->zero_offset_volts = vref_volts * 0.5f; /* За замовчуванням VCC / 2 */
    sensor->filter_alpha = (filter_alpha > 0.0f && filter_alpha <= 1.0f) ? filter_alpha : 0.1f;
    sensor->filtered_current_a = 0.0f;
    sensor->is_calibrated = false;
}

/**
 * @brief Автоматичне калібрування нуля струму за N відліками.
 * @note Викликається лише тоді, коли силове навантаження гарантовано вимкнено (I = 0).
 */
bool hall_sensor_calibrate_zero(HallCurrentSensor *sensor,
                                const uint16_t *adc_samples,
                                uint32_t sample_count)
{
    if (sample_count == 0 || adc_samples == 0) {
        return false;
    }

    uint64_t sum_ticks = 0;
    for (uint32_t i = 0; i < sample_count; ++i) {
        sum_ticks += adc_samples[i];
    }

    float avg_ticks = (float)sum_ticks / (float)sample_count;
    sensor->zero_offset_volts = (avg_ticks / (float)sensor->adc_max_ticks) * sensor->vref_volts;
    sensor->filtered_current_a = 0.0f;
    sensor->is_calibrated = true;

    return true;
}

/**
 * @brief Оновлення стану сенсора за новим відліком АЦП.
 * @param sensor Вказівник на структуру сенсора.
 * @param raw_adc_ticks Сирий код АЦП.
 * @return Миттєве нефільтроване значення струму в амперах.
 */
float hall_sensor_update(HallCurrentSensor *sensor, uint16_t raw_adc_ticks)
{
    /* Переведення коду АЦП у напругу */
    float v_measured = ((float)raw_adc_ticks / (float)sensor->adc_max_ticks) * sensor->vref_volts;

    /* Різниця напруги відносно каліброваного нуля (у мілівольтах) */
    float delta_v_mv = (v_measured - sensor->zero_offset_volts) * 1000.0f;

    /* Обчислення струму: I = (V_out - V_zero) / S */
    float raw_current_a = delta_v_mv / sensor->sensitivity_mv_a;

    /* Оновлення експоненційного фільтра IIR */
    sensor->filtered_current_a = (sensor->filter_alpha * raw_current_a) +
                                 ((1.0f - sensor->filter_alpha) * sensor->filtered_current_a);

    return raw_current_a;
}

/**
 * @brief Отримання поточного згладженого струму.
 */
float hall_sensor_get_filtered_current(const HallCurrentSensor *sensor)
{
    return sensor->filtered_current_a;
}
