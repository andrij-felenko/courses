#include <stdint.h>
#include <stdbool.h>

/* Коди станів заряду та безпеки батареї */
typedef enum {
    BATTERY_STATE_OK = 0,
    BATTERY_STATE_LOW_WARNING,
    BATTERY_STATE_CRITICAL,
    BATTERY_STATE_EMERGENCY_BROWNOUT
} battery_state_t;

/* Конфігурація монітора живлення */
typedef struct {
    uint8_t  cell_count;            /* Кількість послідовних банок (наприклад, 6 для 6S) */
    float    capacity_mah;          /* Паспортна номінальна ємність батареї (мАг) */
    float    r_internal_total_ohm;  /* Оцінений внутрішній опір усього пакета (Ом) */
    float    cell_warn_mv;          /* Поріг попередження (мВ на банку, наприклад 3500) */
    float    cell_crit_mv;          /* Критичний поріг (мВ на банку, наприклад 3300) */
    float    cell_emergency_mv;     /* Поріг апаратного браунауту (мВ на банку, наприклад 3000) */
    float    filter_alpha_v;        /* Коефіцієнт згладжування напруги EMA (0.0..1.0) */
    float    filter_alpha_i;        /* Коефіцієнт згладжування струму EMA (0.0..1.0) */
    float    dt_sec;                /* Період оновлення в секундах (наприклад, 0.02 для 50 Гц) */
    uint16_t debounce_limit_ticks;  /* Кількість тактів утримання перед зміною стану */
} battery_config_t;

/* Стан та робочі змінні монітора */
typedef struct {
    battery_config_t config;
    float            v_filtered_mv;      /* Відфільтрована напруга клем (мВ) */
    float            i_filtered_ma;      /* Відфільтрований струм навантаження (мА) */
    float            v_ocv_est_mv;       /* Скомпенсована напруга розімкненого кола (мВ) */
    float            cell_ocv_mv;        /* Напруга на одну банку з компенсацією (мВ) */
    float            consumed_mah;       /* Інтегрована витрачена ємність (мАг) */
    float            remaining_percent;  /* Розрахований залишок ємності (0..100 %) */
    battery_state_t  current_state;      /* Поточний стан безпеки */
    uint16_t         warning_ticks;      /* Лічильник дебаунсу тривоги */
    uint16_t         critical_ticks;     /* Лічильник дебаунсу аварії */
    bool             initialized;
} battery_monitor_t;

/**
 * @brief Ініціалізація структури монітора живлення
 */
void battery_monitor_init(battery_monitor_t *bm, const battery_config_t *cfg) {
    if (!bm || !cfg) return;
    bm->config = *cfg;
    bm->v_filtered_mv     = 0.0f;
    bm->i_filtered_ma     = 0.0f;
    bm->v_ocv_est_mv      = 0.0f;
    bm->cell_ocv_mv       = 0.0f;
    bm->consumed_mah      = 0.0f;
    bm->remaining_percent = 100.0f;
    bm->current_state     = BATTERY_STATE_OK;
    bm->warning_ticks     = 0;
    bm->critical_ticks    = 0;
    bm->initialized       = false;
}

/**
 * @brief Періодичний крок оновлення монітора (виклик з таймера, наприклад 50 Гц)
 * @param v_raw_mv Сире виміряне значення напруги на клемах з АЦП (мВ)
 * @param i_raw_ma Сире виміряне значення струму через шунт з АЦП (мА)
 */
battery_state_t battery_monitor_update(battery_monitor_t *bm, float v_raw_mv, float i_raw_ma) {
    if (!bm) return BATTERY_STATE_OK;

    /* Первинна ініціалізація фільтра початковими вимірами */
    if (!bm->initialized) {
        bm->v_filtered_mv = v_raw_mv;
        bm->i_filtered_ma = i_raw_ma;
        bm->initialized = true;
    } else {
        /* Експоненційне згладжування шумів комутації (EMA) */
        bm->v_filtered_mv = bm->config.filter_alpha_v * v_raw_mv + 
                            (1.0f - bm->config.filter_alpha_v) * bm->v_filtered_mv;
        bm->i_filtered_ma = bm->config.filter_alpha_i * i_raw_ma + 
                            (1.0f - bm->config.filter_alpha_i) * bm->i_filtered_ma;
    }

    /* Струм не може бути від'ємним для розрахунку компенсації розряду */
    float active_current_ma = (bm->i_filtered_ma > 0.0f) ? bm->i_filtered_ma : 0.0f;

    /* Чисельне інтегрування витраченого заряду (Кулонівський лічильник) */
    float mah_delta = (active_current_ma * bm->config.dt_sec) / 3600.0f;
    bm->consumed_mah += mah_delta;

    /* Розрахунок залишку у відсотках */
    if (bm->config.capacity_mah > 0.0f) {
        float rem = (bm->config.capacity_mah - bm->consumed_mah) / bm->config.capacity_mah * 100.0f;
        bm->remaining_percent = (rem < 0.0f) ? 0.0f : ((rem > 100.0f) ? 100.0f : rem);
    }

    /* Компенсація падіння напруги: V_ocv = V_term + I · R_int */
    float v_drop_mv = (active_current_ma * bm->config.r_internal_total_ohm);
    bm->v_ocv_est_mv = bm->v_filtered_mv + v_drop_mv;

    /* Розрахунок скомпенсованої напруги на окрему банку */
    if (bm->config.cell_count > 0) {
        bm->cell_ocv_mv = bm->v_ocv_est_mv / (float)bm->config.cell_count;
    } else {
        bm->cell_ocv_mv = bm->v_ocv_est_mv;
    }

    /* Скінченний автомат захисту з часовим дебаунсом */
    if (bm->cell_ocv_mv <= bm->config.cell_emergency_mv) {
        /* Миттєвий аварійний стан при загрозі відключення MCU */
        bm->current_state = BATTERY_STATE_EMERGENCY_BROWNOUT;
    } else if (bm->cell_ocv_mv <= bm->config.cell_crit_mv) {
        bm->critical_ticks++;
        if (bm->critical_ticks >= bm->config.debounce_limit_ticks) {
            bm->current_state = BATTERY_STATE_CRITICAL;
        }
    } else if (bm->cell_ocv_mv <= bm->config.cell_warn_mv) {
        bm->warning_ticks++;
        bm->critical_ticks = 0;
        if (bm->warning_ticks >= bm->config.debounce_limit_ticks) {
            bm->current_state = BATTERY_STATE_LOW_WARNING;
        }
    } else {
        /* Напруга в нормі — плавне скидання лічильників */
        if (bm->warning_ticks > 0) bm->warning_ticks--;
        if (bm->critical_ticks > 0) bm->critical_ticks--;
        if (bm->warning_ticks == 0 && bm->critical_ticks == 0) {
            bm->current_state = BATTERY_STATE_OK;
        }
    }

    return bm->current_state;
}
