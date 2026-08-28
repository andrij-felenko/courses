#include <stdint.h>
#include <stdbool.h>

#define ADC_FILTER_SIZE     32
#define DT_WINDOW_SEC       60

typedef enum {
    CHEM_LEAD_ACID,
    CHEM_NIMH
} battery_chem_t;

typedef enum {
    STATE_STANDBY,
    // Станція свинцю (IUoU)
    STATE_LA_BULK_CC,
    STATE_LA_ABSORPTION_CV,
    STATE_LA_FLOAT,
    // Станція NiMH
    STATE_NIMH_PRECHARGE,
    STATE_NIMH_FAST_CC,
    STATE_NIMH_TOP_OFF,
    STATE_NIMH_TRICKLE,
    // Аварія
    STATE_FAULT
} charger_state_t;

typedef enum {
    FAULT_NONE,
    FAULT_OVER_VOLTAGE,
    FAULT_OVER_TEMP,
    FAULT_TIMEOUT,
    FAULT_REVERSE_POLARITY
} charger_fault_t;

typedef struct {
    battery_chem_t chem;
    charger_state_t state;
    charger_fault_t fault;

    uint16_t capacity_mah;
    uint8_t  cell_count;

    // Фільтрація напруги
    uint32_t v_buffer[ADC_FILTER_SIZE];
    uint8_t  v_buf_idx;
    uint32_t v_filtered_mv;
    uint32_t v_peak_mv;

    // Відстеження температури (dT/dt)
    int16_t  t_history[DT_WINDOW_SEC];
    uint8_t  t_hist_idx;
    int16_t  t_current_c;
    int16_t  dt_dt_mdeg_per_sec;

    // Таймери станів
    uint32_t state_time_sec;
    uint32_t total_charge_sec;

    // Вихідні уставки для ШІМ-регулятора
    uint16_t target_v_mv;
    uint16_t target_i_ma;
} charger_fsm_t;

// Розрахунок температурно-компенсованої напруги для свинцю
static uint16_t la_calc_compensated_v(uint16_t base_mv, int16_t temp_c, uint8_t cells) {
    // Коефіцієнт -4 мВ/°C на комірку відносно 25 °C
    int32_t delta_t = (int32_t)temp_c - 25;
    int32_t comp_mv = -4 * (int32_t)cells * delta_t;
    int32_t result = (int32_t)base_mv + comp_mv;
    if (result < 10000) result = 10000;
    if (result > 16500) result = 16500;
    return (uint16_t)result;
}

void charger_init(charger_fsm_t *ch, battery_chem_t chem, uint16_t cap_mah, uint8_t cells) {
    ch->chem = chem;
    ch->state = STATE_STANDBY;
    ch->fault = FAULT_NONE;
    ch->capacity_mah = cap_mah;
    ch->cell_count = cells;
    ch->v_buf_idx = 0;
    ch->v_filtered_mv = 0;
    ch->v_peak_mv = 0;
    ch->t_hist_idx = 0;
    ch->state_time_sec = 0;
    ch->total_charge_sec = 0;
    ch->target_v_mv = 0;
    ch->target_i_ma = 0;
    for (int i = 0; i < ADC_FILTER_SIZE; ++i) ch->v_buffer[i] = 0;
    for (int i = 0; i < DT_WINDOW_SEC; ++i)   ch->t_history[i] = 25;
}

void charger_update_sensors(charger_fsm_t *ch, uint16_t raw_v_mv, int16_t raw_t_c) {
    ch->v_buffer[ch->v_buf_idx] = raw_v_mv;
    ch->v_buf_idx = (ch->v_buf_idx + 1) % ADC_FILTER_SIZE;

    uint32_t sum = 0;
    for (int i = 0; i < ADC_FILTER_SIZE; ++i) sum += ch->v_buffer[i];
    ch->v_filtered_mv = sum / ADC_FILTER_SIZE;

    ch->t_current_c = raw_t_c;
    int16_t old_t = ch->t_history[ch->t_hist_idx];
    ch->t_history[ch->t_hist_idx] = raw_t_c;
    ch->t_hist_idx = (ch->t_hist_idx + 1) % DT_WINDOW_SEC;

    // Градієнт за DT_WINDOW_SEC секунд у міліградусах на секунду
    ch->dt_dt_mdeg_per_sec = ((int32_t)(raw_t_c - old_t) * 1000) / DT_WINDOW_SEC;
}

void charger_tick_1s(charger_fsm_t *ch, uint16_t measured_i_ma) {
    ch->state_time_sec++;
    ch->total_charge_sec++;

    // Загальний захист за максимальною температурою (> 55 °C)
    if (ch->t_current_c > 55) {
        ch->state = STATE_FAULT;
        ch->fault = FAULT_OVER_TEMP;
        ch->target_v_mv = 0;
        ch->target_i_ma = 0;
        return;
    }

    switch (ch->state) {
        case STATE_STANDBY:
            if (ch->v_filtered_mv > 500) {
                ch->state_time_sec = 0;
                if (ch->chem == CHEM_LEAD_ACID) {
                    ch->state = STATE_LA_BULK_CC;
                    ch->target_i_ma = ch->capacity_mah / 10; // 0.1C
                    ch->target_v_mv = la_calc_compensated_v(2400 * ch->cell_count, ch->t_current_c, ch->cell_count);
                } else {
                    if (ch->v_filtered_mv < 1000 * ch->cell_count) {
                        ch->state = STATE_NIMH_PRECHARGE;
                        ch->target_i_ma = ch->capacity_mah / 10;
                    } else {
                        ch->state = STATE_NIMH_FAST_CC;
                        ch->target_i_ma = (ch->capacity_mah * 7) / 10; // 0.7C
                    }
                    ch->v_peak_mv = ch->v_filtered_mv;
                }
            }
            break;

        // ── СВИНЕЦЬ (IUoU) ──
        case STATE_LA_BULK_CC: {
            uint16_t v_abs_target = la_calc_compensated_v(2400 * ch->cell_count, ch->t_current_c, ch->cell_count);
            ch->target_v_mv = v_abs_target;
            ch->target_i_ma = ch->capacity_mah / 10;

            if (ch->v_filtered_mv >= v_abs_target) {
                ch->state = STATE_LA_ABSORPTION_CV;
                ch->state_time_sec = 0;
            }
            if (ch->state_time_sec > 14 * 3600) { // 14 годин ліміт
                ch->state = STATE_FAULT;
                ch->fault = FAULT_TIMEOUT;
            }
            break;
        }

        case STATE_LA_ABSORPTION_CV: {
            uint16_t v_abs_target = la_calc_compensated_v(2400 * ch->cell_count, ch->t_current_c, ch->cell_count);
            ch->target_v_mv = v_abs_target;

            // Перехід на Float за спадом струму < C/50 або таймером 4 години
            if (measured_i_ma < (ch->capacity_mah / 50) || ch->state_time_sec > 4 * 3600) {
                ch->state = STATE_LA_FLOAT;
                ch->state_time_sec = 0;
            }
            break;
        }

        case STATE_LA_FLOAT: {
            uint16_t v_flt_target = la_calc_compensated_v(2260 * ch->cell_count, ch->t_current_c, ch->cell_count);
            ch->target_v_mv = v_flt_target;
            ch->target_i_ma = ch->capacity_mah / 20; // обмеження струму
            break;
        }

        // ── NiMH ──
        case STATE_NIMH_PRECHARGE:
            if (ch->v_filtered_mv >= 1000 * ch->cell_count) {
                ch->state = STATE_NIMH_FAST_CC;
                ch->state_time_sec = 0;
                ch->target_i_ma = (ch->capacity_mah * 7) / 10; // 0.7C
                ch->v_peak_mv = ch->v_filtered_mv;
            }
            if (ch->state_time_sec > 30 * 60) {
                ch->state = STATE_FAULT;
                ch->fault = FAULT_TIMEOUT;
            }
            break;

        case STATE_NIMH_FAST_CC:
            if (ch->v_filtered_mv > ch->v_peak_mv) {
                ch->v_peak_mv = ch->v_filtered_mv;
            }

            // Критерії термінації: -dV >= 4 мВ на комірку АБО dT/dt >= 1.0 °C/хв (16.6 м°C/с)
            uint32_t dv_threshold = 4 * ch->cell_count;
            bool neg_dv = (ch->v_peak_mv > ch->v_filtered_mv + dv_threshold);
            bool temp_slope = (ch->dt_dt_mdeg_per_sec >= 17 && ch->state_time_sec > 300);

            if (neg_dv || temp_slope) {
                ch->state = STATE_NIMH_TOP_OFF;
                ch->state_time_sec = 0;
                ch->target_i_ma = ch->capacity_mah / 10; // 0.1C дозаряд
            }
            if (ch->state_time_sec > 2 * 3600) { // 2 години захисний ліміт
                ch->state = STATE_FAULT;
                ch->fault = FAULT_TIMEOUT;
            }
            break;

        case STATE_NIMH_TOP_OFF:
            if (ch->state_time_sec >= 30 * 60) { // 30 хвилин дозаряду
                ch->state = STATE_NIMH_TRICKLE;
                ch->state_time_sec = 0;
                ch->target_i_ma = ch->capacity_mah / 35; // C/35 краплинний підзаряд
            }
            break;

        case STATE_NIMH_TRICKLE:
            ch->target_i_ma = ch->capacity_mah / 35;
            break;

        case STATE_FAULT:
            ch->target_v_mv = 0;
            ch->target_i_ma = 0;
            break;
    }
}
