#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Рівні стану аварійної системи батареї
typedef enum {
    BATTERY_STATE_NORMAL   = 0,
    BATTERY_STATE_WARNING  = 1,
    BATTERY_STATE_RTL      = 2,
    BATTERY_STATE_LAND     = 3
} battery_state_t;

// Конфігураційні параметри батареї
typedef struct {
    uint8_t  cell_count;            // Кількість банок (наприклад, 6 для 6S)
    float    capacity_mah;          // Номінальна ємність у мА·год
    float    r_internal_pack_ohm;   // Сумарний внутрішній опір пака в Омах
    float    filter_time_const_sec; // Стала часу ФНЧ напруги (секунди)

    // Пороги напруги розімкненого кола (OCV) на одну банку, В
    float    v_cell_warning;        // Поріг рівня 1 (Warning, зазвичай 3.65 В)
    float    v_cell_rtl;            // Поріг рівня 2 (RTL, зазвичай 3.55 В)
    float    v_cell_land;           // Поріг рівня 3 (Land, зазвичай 3.40 В)

    // Пороги залишкової ємності (SOC), частка від 0.0 до 1.0
    float    soc_warning;           // Поріг 1 (наприклад, 0.30)
    float    soc_rtl;               // Поріг 2 (наприклад, 0.20)
    float    soc_land;              // Поріг 3 (наприклад, 0.10)

    // Час дебаунсу для кожного порогу, мілісекунди
    uint32_t debounce_warning_ms;   // 5000 мс
    uint32_t debounce_rtl_ms;       // 3000 мс
    uint32_t debounce_land_ms;      // 1000 мс
} battery_config_t;

// Внутрішній стан менеджера живлення
typedef struct {
    battery_config_t cfg;
    
    float    u_cell_ocv_filtered;   // Відфільтрована напруга ЕРС на комірку
    float    consumed_mah;          // Спожитий заряд у мА·год
    float    soc_remaining;         // Залишковий відносний заряд [0.0 ... 1.0]

    uint32_t time_below_warn_ms;    // Тривалість перебування нижче порогу Warning
    uint32_t time_below_rtl_ms;     // Тривалість перебування нижче порогу RTL
    uint32_t time_below_land_ms;    // Тривалість перебування нижче порогу Land

    battery_state_t current_state;  // Поточний зафіксований стан системи
    bool     is_initialized;
} battery_monitor_t;

void battery_monitor_init(battery_monitor_t *mon, const battery_config_t *cfg) {
    mon->cfg = *cfg;
    mon->u_cell_ocv_filtered = cfg->v_cell_warning;
    mon->consumed_mah = 0.0f;
    mon->soc_remaining = 1.0f;
    mon->time_below_warn_ms = 0;
    mon->time_below_rtl_ms = 0;
    mon->time_below_land_ms = 0;
    mon->current_state = BATTERY_STATE_NORMAL;
    mon->is_initialized = false;
}

// Періодичний крок обробки (викликається в циклі з кроком dt_sec)
battery_state_t battery_monitor_update(battery_monitor_t *mon, 
                                       float u_pack_raw_volts, 
                                       float i_pack_raw_amps, 
                                       float dt_sec) {
    if (mon->cfg.cell_count == 0) return BATTERY_STATE_NORMAL;

    // 1. Інтегрування витраченого заряду (кулонівський лічильник)
    float delta_mah = (i_pack_raw_amps * 1000.0f) * (dt_sec / 3600.0f);
    mon->consumed_mah += delta_mah;
    mon->soc_remaining = 1.0f - (mon->consumed_mah / mon->cfg.capacity_mah);
    if (mon->soc_remaining < 0.0f) mon->soc_remaining = 0.0f;
    if (mon->soc_remaining > 1.0f) mon->soc_remaining = 1.0f;

    // 2. Компенсація просідання напруги від струму (Voltage Sag Compensation)
    // U_ocv = U_measured + I * R_internal
    float u_pack_ocv_instant = u_pack_raw_volts + (i_pack_raw_amps * mon->cfg.r_internal_pack_ohm);
    float u_cell_ocv_instant = u_pack_ocv_instant / (float)mon->cfg.cell_count;

    // 3. Фільтрація низьких частот для усунення імпульсних шумів
    if (!mon->is_initialized) {
        mon->u_cell_ocv_filtered = u_cell_ocv_instant;
        mon->is_initialized = true;
    } else {
        float alpha = dt_sec / (mon->cfg.filter_time_const_sec + dt_sec);
        mon->u_cell_ocv_filtered += alpha * (u_cell_ocv_instant - mon->u_cell_ocv_filtered);
    }

    // 4. Оцінка стану за двома незалежними джерелами
    battery_state_t state_voltage = BATTERY_STATE_NORMAL;
    if (mon->u_cell_ocv_filtered <= mon->cfg.v_cell_land) {
        state_voltage = BATTERY_STATE_LAND;
    } else if (mon->u_cell_ocv_filtered <= mon->cfg.v_cell_rtl) {
        state_voltage = BATTERY_STATE_RTL;
    } else if (mon->u_cell_ocv_filtered <= mon->cfg.v_cell_warning) {
        state_voltage = BATTERY_STATE_WARNING;
    }

    battery_state_t state_capacity = BATTERY_STATE_NORMAL;
    if (mon->soc_remaining <= mon->cfg.soc_land) {
        state_capacity = BATTERY_STATE_LAND;
    } else if (mon->soc_remaining <= mon->cfg.soc_rtl) {
        state_capacity = BATTERY_STATE_RTL;
    } else if (mon->soc_remaining <= mon->cfg.soc_warning) {
        state_capacity = BATTERY_STATE_WARNING;
    }

    // Консервативний арбітраж: беремо найгірший стан з двох сигналів
    battery_state_t raw_target_state = (state_voltage > state_capacity) ? state_voltage : state_capacity;

    // 5. Розрахунок таймерів дебаунсу
    uint32_t dt_ms = (uint32_t)(dt_sec * 1000.0f);

    if (raw_target_state >= BATTERY_STATE_LAND) {
        mon->time_below_land_ms += dt_ms;
    } else {
        mon->time_below_land_ms = 0;
    }

    if (raw_target_state >= BATTERY_STATE_RTL) {
        mon->time_below_rtl_ms += dt_ms;
    } else {
        mon->time_below_rtl_ms = 0;
    }

    if (raw_target_state >= BATTERY_STATE_WARNING) {
        mon->time_below_warn_ms += dt_ms;
    } else {
        mon->time_below_warn_ms = 0;
    }

    // 6. Ескалація з фіксацією стану (Latching State Machine)
    if (mon->time_below_land_ms >= mon->cfg.debounce_land_ms) {
        mon->current_state = BATTERY_STATE_LAND;
    } else if (mon->time_below_rtl_ms >= mon->cfg.debounce_rtl_ms) {
        if (mon->current_state < BATTERY_STATE_RTL) {
            mon->current_state = BATTERY_STATE_RTL;
        }
    } else if (mon->time_below_warn_ms >= mon->cfg.debounce_warning_ms) {
        if (mon->current_state < BATTERY_STATE_WARNING) {
            mon->current_state = BATTERY_STATE_WARNING;
        }
    }

    return mon->current_state;
}
