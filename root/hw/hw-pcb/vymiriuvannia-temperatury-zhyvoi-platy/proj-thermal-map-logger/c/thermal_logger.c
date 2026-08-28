/**
 * @file thermal_logger.c
 * @brief Модуль збору багатоточкових температурних профілів та аналізу градієнтів PCB.
 * Стандарт: C99. Повна відсутність динамічного виділення пам'яті (MISRA C compliant).
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define THERMAL_MAX_CHANNELS      16
#define THERMAL_GRID_ROWS         4
#define THERMAL_GRID_COLS         4
#define THERMAL_HISTORY_DEPTH     8

#define THERMAL_SAFE_GRADIENT_MAX 1.5f  /* 1.5 °C/мм = 15.0 °C/см — поріг механічного ризику */
#define THERMAL_MAX_RISE_RATE     5.0f  /* 5.0 °C/с — поріг теплової втечі або КЗ */

/** @brief Тип вимірювального датчика каналу */
typedef enum {
    SENSOR_TYPE_THERMOCOUPLE_K   = 0,
    SENSOR_TYPE_DIGITAL_IC       = 1,
    SENSOR_TYPE_LWIR_RADIOMETRIC = 2
} sensor_type_t;

/** @brief Прапорці стану та попереджень теплової системи */
typedef enum {
    THERMAL_STAT_OK               = 0,
    THERMAL_STAT_WARN_HOTSPOT     = (1 << 0),
    THERMAL_STAT_WARN_GRADIENT    = (1 << 1),
    THERMAL_STAT_WARN_RUNAWAY     = (1 << 2),
    THERMAL_STAT_ERR_SENSOR_FAULT = (1 << 3)
} thermal_status_flags_t;

/** @brief Конфігурація та поточний стан вимірювального каналу */
typedef struct {
    uint8_t channel_id;
    char name[24];
    sensor_type_t type;
    float pos_x_mm;
    float pos_y_mm;
    float emissivity;         /* Коефіцієнт випромінювання поверхні (0.02 .. 1.00) */
    float psi_jt;             /* JEDEC JESD51 параметр Psi-JT (°C/Вт) */
    float p_diss_w;           /* Потужність втрат у компоненті (Вт) */
    float t_crit_c;           /* Гранична температура напівпровідникового кристала */
    float current_temp_c;     /* Виміряна температура поверхні */
    float junction_temp_c;    /* Розрахована температура кристала T_J */
    float rate_of_rise_cps;   /* Перша похідна нагріву dT/dt (°C/с) */
    float history[THERMAL_HISTORY_DEPTH];
    uint8_t history_idx;
    bool is_active;
    bool fault_detected;
} thermal_channel_t;

/** @brief Контекст теплового моніторингу друкованої плати */
typedef struct {
    thermal_channel_t channels[THERMAL_MAX_CHANNELS];
    size_t channel_count;
    float ambient_temp_c;
    float reflected_temp_c;   /* Опорна температура для радіометрії Стефана-Больцмана */
    float max_board_temp_c;
    float max_junction_temp_c;
    float max_gradient_c_per_mm;
    uint32_t status_flags;
    uint32_t sample_index;
    float temp_grid[THERMAL_GRID_ROWS][THERMAL_GRID_COLS];
    float grid_pitch_x_mm;
    float grid_pitch_y_mm;
} thermal_monitor_t;

/**
 * @brief Прецизійне поліноміальне наближення NIST ITS-90 для термопари типу K.
 * @param v_mv Сумарна термо-ЕРС у мілівольтах відносно віртуального нуля 0 °C.
 * @return Розрахована температура гарячого спаю в °C.
 */
static float thermocouple_k_nist_eval(float v_mv) {
    /* Коефіцієнти NIST ITS-90 для діапазону 0 °C .. 500 °C */
    static const double d[10] = {
        0.0,
        2.508355e1,
        7.860106e-2,
        -2.503131e-1,
        8.315270e-2,
        -1.228034e-2,
        9.804036e-4,
        -4.413030e-5,
        1.057734e-6,
        -1.052755e-8
    };

    if (v_mv < -6.0f || v_mv > 55.0f) {
        return -999.0f; /* Обрив кола або некоректний вхідний сигнал */
    }

    double temp = 0.0;
    double v_pow = 1.0;
    for (int i = 1; i < 10; ++i) {
        v_pow *= (double)v_mv;
        temp += d[i] * v_pow;
    }
    return (float)temp;
}

/**
 * @brief Оцінка ЕРС холодного спаю для компенсації CJC.
 * @param t_cjc_c Температура клемного блоку в °C.
 * @return Термо-ЕРС у мілівольтах.
 */
static float thermocouple_k_cjc_emf(float t_cjc_c) {
    const float seebeck_nominal = 0.0405f; /* мВ/°C для діапазону 15..45 °C */
    return t_cjc_c * seebeck_nominal;
}

/**
 * @brief Радіометрична корекція оптичних показів за законом Стефана-Больцмана.
 * @param t_app_c Уявна температура з матриці тепловізора (°C).
 * @param emissivity Коефіцієнт випромінювання тестової зони.
 * @param t_refl_c Температура навколишніх відбиваючих об'єктів (°C).
 * @return Істинна відновлена температура поверхні (°C).
 */
static float radiometric_stefan_boltzmann_correct(float t_app_c, float emissivity, float t_refl_c) {
    if (emissivity < 0.02f) {
        emissivity = 0.02f;
    }

    float t_app_k = t_app_c + 273.15f;
    float t_refl_k = t_refl_c + 273.15f;

    float w_app = powf(t_app_k, 4.0f);
    float w_refl = powf(t_refl_k, 4.0f);

    float w_obj = (w_app - (1.0f - emissivity) * w_refl) / emissivity;
    if (w_obj <= 0.0f) {
        return t_refl_c;
    }

    return powf(w_obj, 0.25f) - 273.15f;
}

/**
 * @brief Ініціалізація структури теплового моніторингу.
 */
void thermal_monitor_init(thermal_monitor_t *mon, float ambient_c, float grid_dx_mm, float grid_dy_mm) {
    if (!mon) return;
    memset(mon, 0, sizeof(thermal_monitor_t));
    mon->ambient_temp_c = ambient_c;
    mon->reflected_temp_c = ambient_c;
    mon->grid_pitch_x_mm = grid_dx_mm;
    mon->grid_pitch_y_mm = grid_dy_mm;
}

/**
 * @brief Реєстрація нового каналу вимірювання на платі.
 */
bool thermal_monitor_add_channel(thermal_monitor_t *mon, const thermal_channel_t *ch) {
    if (!mon || !ch || mon->channel_count >= THERMAL_MAX_CHANNELS) {
        return false;
    }
    mon->channels[mon->channel_count] = *ch;
    mon->channels[mon->channel_count].channel_id = (uint8_t)mon->channel_count;
    mon->channels[mon->channel_count].is_active = true;
    mon->channel_count++;
    return true;
}

/**
 * @brief Обробка одного такту вимірювань для вказаного каналу.
 */
void thermal_monitor_process_sample(thermal_monitor_t *mon, size_t idx, float raw_val, float dt_sec) {
    if (!mon || idx >= mon->channel_count) return;
    thermal_channel_t *ch = &mon->channels[idx];
    if (!ch->is_active) return;

    float computed_t = 0.0f;

    switch (ch->type) {
        case SENSOR_TYPE_THERMOCOUPLE_K: {
            float v_cjc = thermocouple_k_cjc_emf(mon->ambient_temp_c);
            float v_total = raw_val + v_cjc;
            computed_t = thermocouple_k_nist_eval(v_total);
            if (computed_t < -100.0f) {
                ch->fault_detected = true;
                return;
            }
            break;
        }
        case SENSOR_TYPE_LWIR_RADIOMETRIC: {
            computed_t = radiometric_stefan_boltzmann_correct(raw_val, ch->emissivity, mon->reflected_temp_c);
            break;
        }
        case SENSOR_TYPE_DIGITAL_IC:
        default: {
            computed_t = raw_val;
            break;
        }
    }

    /* Оцінка похідної dT/dt через ковзне вікно */
    if (dt_sec > 0.001f && ch->current_temp_c > 0.0f) {
        ch->rate_of_rise_cps = (computed_t - ch->current_temp_c) / dt_sec;
    }

    ch->current_temp_c = computed_t;
    ch->history[ch->history_idx] = computed_t;
    ch->history_idx = (uint8_t)((ch->history_idx + 1) % THERMAL_HISTORY_DEPTH);

    /* Розрахунок кристала T_J за JESD51 */
    ch->junction_temp_c = ch->current_temp_c + (ch->psi_jt * ch->p_diss_w);
}

/**
 * @brief Оновлення просторового розподілу та чисельне диференціювання градієнтів.
 */
void thermal_monitor_compute_field(thermal_monitor_t *mon) {
    if (!mon) return;

    mon->status_flags = THERMAL_STAT_OK;
    mon->max_board_temp_c = -273.15f;
    mon->max_junction_temp_c = -273.15f;
    mon->max_gradient_c_per_mm = 0.0f;

    /* Скидання вузлів сітки до фонового значення */
    for (int r = 0; r < THERMAL_GRID_ROWS; ++r) {
        for (int c = 0; c < THERMAL_GRID_COLS; ++c) {
            mon->temp_grid[r][c] = mon->ambient_temp_c;
        }
    }

    /* Інтерполяція точок на топологічну сітку */
    for (size_t i = 0; i < mon->channel_count; ++i) {
        const thermal_channel_t *ch = &mon->channels[i];
        if (!ch->is_active || ch->fault_detected) continue;

        if (ch->current_temp_c > mon->max_board_temp_c) {
            mon->max_board_temp_c = ch->current_temp_c;
        }
        if (ch->junction_temp_c > mon->max_junction_temp_c) {
            mon->max_junction_temp_c = ch->junction_temp_c;
        }

        if (ch->junction_temp_c >= ch->t_crit_c) {
            mon->status_flags |= THERMAL_STAT_WARN_HOTSPOT;
        }
        if (ch->rate_of_rise_cps >= THERMAL_MAX_RISE_RATE) {
            mon->status_flags |= THERMAL_STAT_WARN_RUNAWAY;
        }

        int col = (int)(ch->pos_x_mm / mon->grid_pitch_x_mm);
        int row = (int)(ch->pos_y_mm / mon->grid_pitch_y_mm);
        if (row >= 0 && row < THERMAL_GRID_ROWS && col >= 0 && col < THERMAL_GRID_COLS) {
            mon->temp_grid[row][col] = ch->current_temp_c;
        }
    }

    /* Чисельний розрахунок градієнта |grad T| методом центральних різниць */
    for (int r = 0; r < THERMAL_GRID_ROWS; ++r) {
        for (int c = 0; c < THERMAL_GRID_COLS; ++c) {
            float dt_dx = 0.0f;
            float dt_dy = 0.0f;

            if (c > 0 && c < THERMAL_GRID_COLS - 1) {
                dt_dx = (mon->temp_grid[r][c + 1] - mon->temp_grid[r][c - 1]) / (2.0f * mon->grid_pitch_x_mm);
            } else if (c == 0 && THERMAL_GRID_COLS > 1) {
                dt_dx = (mon->temp_grid[r][1] - mon->temp_grid[r][0]) / mon->grid_pitch_x_mm;
            }

            if (r > 0 && r < THERMAL_GRID_ROWS - 1) {
                dt_dy = (mon->temp_grid[r + 1][c] - mon->temp_grid[r - 1][c]) / (2.0f * mon->grid_pitch_y_mm);
            } else if (r == 0 && THERMAL_GRID_ROWS > 1) {
                dt_dy = (mon->temp_grid[1][c] - mon->temp_grid[0][c]) / mon->grid_pitch_y_mm;
            }

            float grad = sqrtf(dt_dx * dt_dx + dt_dy * dt_dy);
            if (grad > mon->max_gradient_c_per_mm) {
                mon->max_gradient_c_per_mm = grad;
            }
        }
    }

    if (mon->max_gradient_c_per_mm >= THERMAL_SAFE_GRADIENT_MAX) {
        mon->status_flags |= THERMAL_STAT_WARN_GRADIENT;
    }

    mon->sample_index++;
}

/**
 * @brief Форматоване виведення телеметрії теплового стану плати.
 */
void thermal_monitor_print_summary(const thermal_monitor_t *mon) {
    if (!mon) return;

    printf("\n=== ПРОТОКОЛ ТЕПЛОВОГО МОНІТОРИНГУ ПЛАТИ [#%u] ===\n", (unsigned int)mon->sample_index);
    printf("Фон: %.1f °C | Макс T_Board: %.1f °C | Макс T_Junction: %.1f °C\n",
           mon->ambient_temp_c, mon->max_board_temp_c, mon->max_junction_temp_c);
    printf("Піковий просторовий градієнт: %.2f °C/мм (%.1f °C/см)\n",
           mon->max_gradient_c_per_mm, mon->max_gradient_c_per_mm * 10.0f);

    printf("Стан системи: [%s%s%s%s]\n",
           (mon->status_flags == 0) ? " НОРМА " : "",
           (mon->status_flags & THERMAL_STAT_WARN_HOTSPOT) ? " [ПЕРЕГРІВ КРИСТАЛА] " : "",
           (mon->status_flags & THERMAL_STAT_WARN_GRADIENT) ? " [НЕБЕЗПЕЧНИЙ ГРАДІЄНТ] " : "",
           (mon->status_flags & THERMAL_STAT_WARN_RUNAWAY) ? " [ТЕПЛОВИЙ РОЗГІН dT/dt] " : "");

    printf("--------------------------------------------------------------------------------\n");
    printf("ID | Контрольна точка     | Тип  | T_поверхні | T_Кристала | Швидк.dT/dt | Втрати P\n");
    printf("---+----------------------+------+------------+------------+-------------+---------\n");

    for (size_t i = 0; i < mon->channel_count; ++i) {
        const thermal_channel_t *ch = &mon->channels[i];
        const char *t_desc = (ch->type == SENSOR_TYPE_THERMOCOUPLE_K) ? "Терм.K" :
                             (ch->type == SENSOR_TYPE_LWIR_RADIOMETRIC) ? "LWIR  " : "Цифр. ";

        printf("%02u | %-20s | %s | %7.1f °C  | %8.1f °C  | %+6.2f °C/s | %4.2f Вт %s\n",
               (unsigned int)ch->channel_id, ch->name, t_desc,
               ch->current_temp_c, ch->junction_temp_c, ch->rate_of_rise_cps, ch->p_diss_w,
               (ch->junction_temp_c >= ch->t_crit_c) ? "(!)" : "   ");
    }
    printf("--------------------------------------------------------------------------------\n");
}
