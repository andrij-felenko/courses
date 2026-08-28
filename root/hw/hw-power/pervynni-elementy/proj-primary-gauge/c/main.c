#include <stdint.h>
#include <stdbool.h>

/* Тип хімічної системи первинного елемента */
typedef enum {
    BATTERY_CHEM_LITHIUM_THIONYL, /* Li-SOCl2 (3.6 В, висока пасивація) */
    BATTERY_CHEM_COIN_CR2032,      /* Li-MnO2 (3.0 В, високий ESR) */
    BATTERY_CHEM_ALKALINE          /* Zn-MnO2 (1.5 В, похилий розряд) */
} battery_chem_t;

/* Конфігурація параметрів батарейного вузла */
typedef struct {
    battery_chem_t chem;
    uint32_t nominal_capacity_uah; /* Номінальна ємність у мкА·год */
    uint32_t esr_milliohm;          /* Еквівалентний послідовний опір (мОм) */
    uint16_t brownout_limit_mv;    /* Поріг аварійного скидання MCU (мВ) */
    uint16_t base_self_discharge_ppm_year; /* Базовий саморозряд при +25C (ppm/рік) */
} battery_config_t;

/* Стан обліку заряду та здоров'я батареї */
typedef struct {
    battery_config_t cfg;
    uint64_t consumed_nanoamp_hours; /* Інтегратор витраченої ємності */
    uint32_t last_pulse_timestamp_s; /* Час останнього силового імпульсу */
    bool depassivation_needed;       /* Прапорець потреби депасивації */
} battery_gauge_t;

/* Ініціалізація структури обліку */
void battery_gauge_init(battery_gauge_t *gauge, const battery_config_t *cfg) {
    if (!gauge || !cfg) return;
    gauge->cfg = *cfg;
    gauge->consumed_nanoamp_hours = 0;
    gauge->last_pulse_timestamp_s = 0;
    gauge->depassivation_needed = false;
}

/* Облік заряду, спожитого в режимі сну за інтервал часу */
void battery_gauge_track_sleep(battery_gauge_t *gauge, uint32_t duration_ms, uint32_t sleep_current_na) {
    if (!gauge) return;
    /* Переведення наноампер-мілісекунд у наноампер-години: nA * ms / 3600000 */
    uint64_t consumed_nah = ((uint64_t)sleep_current_na * duration_ms) / 3600000ULL;
    gauge->consumed_nanoamp_hours += consumed_nah;
}

/* Облік заряду активного імпульсу струму */
void battery_gauge_track_pulse(battery_gauge_t *gauge, uint32_t duration_us, uint32_t current_ua, uint32_t now_s) {
    if (!gauge) return;
    /* uA * us / 3600000000 = uAh -> * 1000 = nAh */
    uint64_t consumed_nah = ((uint64_t)current_ua * duration_us) / 3600000ULL;
    gauge->consumed_nanoamp_hours += consumed_nah;
    gauge->last_pulse_timestamp_s = now_s;
    gauge->depassivation_needed = false;
}

/* Періодичний облік фонового саморозряду з температурною поправкою */
void battery_gauge_update_self_discharge(battery_gauge_t *gauge, int8_t temp_celsius, uint32_t interval_hours) {
    if (!gauge) return;
    
    /* Фактор Арреніуса: подвоєння швидкості на кожні 10°C понад +25°C */
    float temp_factor = 1.0f;
    if (temp_celsius > 25) {
        int8_t delta_t = temp_celsius - 25;
        temp_factor = 1.0f + (float)delta_t * 0.08f; /* Лінеаризація для MCU без FPU */
    } else if (temp_celsius < 10) {
        temp_factor = 0.6f;
    }

    /* Розрахунок втрат на годину від номінальної ємності */
    uint64_t nom_nah = (uint64_t)gauge->cfg.nominal_capacity_uah * 1000ULL;
    uint64_t annual_loss_nah = (nom_nah * gauge->cfg.base_self_discharge_ppm_year) / 1000000ULL;
    uint64_t hour_loss_nah = (uint64_t)((annual_loss_nah / 8760ULL) * temp_factor);

    gauge->consumed_nanoamp_hours += (hour_loss_nah * interval_hours);

    /* Перевірка потреби депасивації для Li-SOCl2 (якщо спокій > 30 діб або мороз) */
    if (gauge->cfg.chem == BATTERY_CHEM_LITHIUM_THIONYL) {
        if ((interval_hours > 720) || (temp_celsius < 0 && interval_hours > 168)) {
            gauge->depassivation_needed = true;
        }
    }
}

/* Прогноз просідання напруги перед радіопосилкою (повертає очікувану напругу клем у мВ) */
uint16_t battery_predict_pulse_voltage_mv(const battery_gauge_t *gauge, uint16_t ocv_mv, uint32_t pulse_current_ua) {
    if (!gauge) return 0;
    
    /* Омічний спад: ΔU (мВ) = I (мкА) * ESR (мОм) / 1000000 */
    uint32_t sag_mv = ((uint64_t)pulse_current_ua * gauge->cfg.esr_milliohm) / 1000000ULL;
    
    if (ocv_mv <= sag_mv) {
        return 0;
    }
    return (ocv_mv - (uint16_t)sag_mv);
}

/* Отримання залишкового заряду у відсотках (0..100) */
uint8_t battery_get_state_of_charge_pct(const battery_gauge_t *gauge) {
    if (!gauge) return 0;
    uint64_t nom_nah = (uint64_t)gauge->cfg.nominal_capacity_uah * 1000ULL;
    if (gauge->consumed_nanoamp_hours >= nom_nah) {
        return 0;
    }
    uint64_t remaining_nah = nom_nah - gauge->consumed_nanoamp_hours;
    return (uint8_t)((remaining_nah * 100ULL) / nom_nah);
}
