#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Конфігурація та калібрувальні коефіцієнти датчика Холла */
typedef struct {
    float sens_v_per_tesla;     /* Базова чутливість S0 при 25°C (В/Тл) */
    float temp_coeff_alpha;     /* Лінійний температурний коефіцієнт (1/°C) */
    float temp_coeff_beta;      /* Квадратичний температурний коефіцієнт (1/°C^2) */
    float t_cal_celsius;        /* Температура калібрування (типово 25.0°C) */
    float coupling_tesla_per_a; /* Магнітний зв'язок осердя/плати (Тл/А) */
    float b_op_threshold_mt;    /* Порог спрацьовування перемикача B_OP (мТл) */
    float b_rp_threshold_mt;    /* Порог відпускання перемикача B_RP (мТл) */
} hall_calib_t;

/* Стан та результат вимірювання драйвера */
typedef struct {
    hall_calib_t calib;
    float zero_offset_volts;    /* Калібрований нуль поля (В) */
    bool switch_state;          /* Поточний логічний стан перемикача */
    float filtered_b_field_mt;  /* Згладжене значення поля (мТл) */
    float filtered_current_a;   /* Згладжене значення струму (А) */
    float ema_alpha;            /* Коефіцієнт ФНЧ (0.01..1.0) */
} hall_sensor_t;

/**
 * Ініціалізація структури драйвера датчика Холла
 */
void hall_init(hall_sensor_t *dev, const hall_calib_t *calib, float ema_alpha) {
    if (!dev || !calib) return;
    dev->calib = *calib;
    dev->zero_offset_volts = 0.0f;
    dev->switch_state = false;
    dev->filtered_b_field_mt = 0.0f;
    dev->filtered_current_a = 0.0f;
    dev->ema_alpha = (ema_alpha > 0.0f && ema_alpha <= 1.0f) ? ema_alpha : 0.2f;
}

/**
 * Встановлення поточної напруги нульового поля (Tara / Zero-field Offset)
 */
void hall_set_zero_offset(hall_sensor_t *dev, float zero_volts) {
    if (dev) {
        dev->zero_offset_volts = zero_volts;
    }
}

/**
 * Обробка 4-фазного зчитування напруг обертання струму та оновлення даних
 *
 * @param v_phases Масив із 4 напруг (В) для фаз [0°, 90°, 180°, 270°]
 * @param temp_c   Поточна температура кристала (°C)
 * @param out_b_mt Вказівник для повернення магнітного поля (мТл)
 * @param out_i_a  Вказівник для повернення виміряного струму (А)
 * @return true у разі успішного розрахунку
 */
bool hall_process_sample(hall_sensor_t *dev,
                         const float v_phases[4],
                         float temp_c,
                         float *out_b_mt,
                         float *out_i_a) {
    if (!dev || !v_phases) return false;

    /* 1. Демодуляція 4-фазного обертання струму (Spinning Current Demodulation) */
    float v_hall = (v_phases[0] - v_phases[1] + v_phases[2] - v_phases[3]) * 0.25f;

    /* Віднімання залишкового зміщення нуля */
    float v_signal = v_hall - dev->zero_offset_volts;

    /* 2. Поліноміальна температурна компенсація чутливості */
    float dt = temp_c - dev->calib.t_cal_celsius;
    float temp_gain_factor = 1.0f + (dev->calib.temp_coeff_alpha * dt)
                                  + (dev->calib.temp_coeff_beta * dt * dt);

    if (temp_gain_factor < 0.1f) {
        temp_gain_factor = 0.1f; /* Захист від ділення на нуль */
    }

    float sens_actual = dev->calib.sens_v_per_tesla * temp_gain_factor;

    /* 3. Розрахунок магнітної індукції B (в Теслах та мТл) */
    float b_tesla = v_signal / sens_actual;
    float b_mt = b_tesla * 1000.0f;

    /* Розрахунок струму I (в Амперах) */
    float current_a = 0.0f;
    if (dev->calib.coupling_tesla_per_a > 1e-9f) {
        current_a = b_tesla / dev->calib.coupling_tesla_per_a;
    }

    /* 4. Експоненційне згладжування результатів (ЕМА ФНЧ) */
    dev->filtered_b_field_mt = dev->filtered_b_field_mt +
        dev->ema_alpha * (b_mt - dev->filtered_b_field_mt);

    dev->filtered_current_a = dev->filtered_current_a +
        dev->ema_alpha * (current_a - dev->filtered_current_a);

    /* 5. Логіка перемикача з магнітним гістерезисом */
    if (!dev->switch_state) {
        if (dev->filtered_b_field_mt >= dev->calib.b_op_threshold_mt) {
            dev->switch_state = true;
        }
    } else {
        if (dev->filtered_b_field_mt <= dev->calib.b_rp_threshold_mt) {
            dev->switch_state = false;
        }
    }

    if (out_b_mt) *out_b_mt = dev->filtered_b_field_mt;
    if (out_i_a) *out_i_a = dev->filtered_current_a;

    return true;
}
