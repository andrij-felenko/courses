#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Типи станів автомата кульгавого режиму
typedef enum {
    LIMP_STATE_NORMAL       = 0,
    LIMP_STATE_THROTTLED    = 1,
    LIMP_STATE_L1           = 2,
    LIMP_STATE_L2           = 3,
    LIMP_STATE_CRITICAL_LAND= 4,
    LIMP_STATE_LATCHED      = 5
} limp_state_t;

// Діагностичні коди несправностей (DTC)
typedef enum {
    DTC_NONE                = 0x0000,
    DTC_MOSFET_OVERTEMP     = 0x1001,
    DTC_BATTERY_UNDERVOLT   = 0x2001,
    DTC_CELL_UNBALANCE      = 0x2002,
    DTC_PHASE_CURRENT_FAULT = 0x3001,
    DTC_COMM_LINK_LOST      = 0x4001
} dtc_code_t;

// Вхідні дані телеметрії датчиків
typedef struct {
    float mosfet_temp_c;        // Температура радіатора/кристала силових ключів (°C)
    float bus_voltage_v;        // Напруга силової шини живлення (В)
    float min_cell_voltage_v;   // Мінімальна напруга найслабшої комірки батареї (В)
    float total_current_a;      // Загальний споживаний струм борту (А)
    bool  current_sensor_valid; // Прапорець справності вимірювання струму фаз
    bool  comm_link_active;     // Прапорець наявності каналу телеметрії
    uint32_t timestamp_ms;      // Системний час (мс)
} sensor_telemetry_t;

// Вихідні обмеження та керуючі сигнали
typedef struct {
    float max_allowed_current_a; // Динамічно урізаний ліміт струму (А)
    uint32_t target_pwm_freq_hz; // Адаптивна частота ШІМ інвертора (Гц)
    bool  enable_tier1_nav;      // Живлення Tier 1: GNSS/Висотомір
    bool  enable_tier2_sbc;      // Живлення Tier 2: Супутній комп'ютер / AI
    bool  enable_tier3_payload;  // Живлення Tier 3: Підвіс камери / Фари
    limp_state_t current_state;  // Поточний стан автомата
    dtc_code_t   active_dtc;     // Активний код несправності
} limp_control_outputs_t;

// Структура конфігурації порогів та гістерезису
typedef struct {
    float temp_warn_c;           // Поріг початку тротлінгу (наприклад, 90.0 °C)
    float temp_crit_c;           // Поріг переходу в Limp L1 (наприклад, 105.0 °C)
    float temp_fatal_c;          // Поріг переходу в Limp L2 (наприклад, 115.0 °C)
    float temp_hysteresis_c;     // Гістерезис температури для скидання (наприклад, 8.0 °C)
    float volt_min_cell_warn_v;  // Попередження розряду комірки (наприклад, 3.3 В)
    float volt_min_cell_crit_v;  // Критичний розряд комірки (наприклад, 3.0 В)
    float nominal_current_max_a; // Номінальний піковий струм (наприклад, 80.0 А)
    float limp_l1_current_max_a; // Ліміт струму Limp L1 (наприклад, 40.0 А)
    float limp_l2_current_max_a; // Ліміт струму Limp L2 (наприклад, 28.0 А)
    uint32_t min_dwell_time_ms;  // Мінімальний час утримання аварійного стану (мс)
} limp_config_t;

// Стан контексту контролера
typedef struct {
    limp_config_t config;
    limp_state_t  state;
    dtc_code_t    latched_dtc;
    uint32_t      state_entry_time_ms;
    uint32_t      last_fault_timestamp;
} limp_controller_ctx_t;

// Ініціалізація контролера
void limp_controller_init(limp_controller_ctx_t *ctx, const limp_config_t *cfg) {
    if (!ctx || !cfg) return;
    ctx->config = *cfg;
    ctx->state = LIMP_STATE_NORMAL;
    ctx->latched_dtc = DTC_NONE;
    ctx->state_entry_time_ms = 0;
    ctx->last_fault_timestamp = 0;
}

// Перехід автомата з фіксацією часу та коду DTC
static void set_state(limp_controller_ctx_t *ctx, limp_state_t new_state, dtc_code_t dtc, uint32_t now_ms) {
    if (ctx->state != new_state) {
        ctx->state = new_state;
        ctx->state_entry_time_ms = now_ms;
        if (dtc != DTC_NONE && ctx->latched_dtc == DTC_NONE) {
            ctx->latched_dtc = dtc;
            ctx->last_fault_timestamp = now_ms;
            // Тут викликається низькорівневий запис Freeze Frame у NVS
        }
    }
}

// Головний крок оновлення контролера (викликається в циклі 50-100 Гц)
void limp_controller_update(limp_controller_ctx_t *ctx,
                            const sensor_telemetry_t *telem,
                            limp_control_outputs_t *out) {
    if (!ctx || !telem || !out) return;

    const uint32_t now = telem->timestamp_ms;
    const uint32_t dwell = now - ctx->state_entry_time_ms;
    dtc_code_t current_fault = DTC_NONE;

    // 1. Детекція першопричин збоїв
    if (!telem->current_sensor_valid) {
        current_fault = DTC_PHASE_CURRENT_FAULT;
    } else if (telem->mosfet_temp_c >= ctx->config.temp_fatal_c) {
        current_fault = DTC_MOSFET_OVERTEMP;
    } else if (telem->min_cell_voltage_v <= ctx->config.volt_min_cell_crit_v) {
        current_fault = DTC_BATTERY_UNDERVOLT;
    } else if (telem->mosfet_temp_c >= ctx->config.temp_crit_c) {
        current_fault = DTC_MOSFET_OVERTEMP;
    } else if (telem->mosfet_temp_c >= ctx->config.temp_warn_c ||
               telem->min_cell_voltage_v <= ctx->config.volt_min_cell_warn_v) {
        current_fault = DTC_MOSFET_OVERTEMP;
    }

    // 2. Логіка детермінованого автомата переходів
    switch (ctx->state) {
        case LIMP_STATE_NORMAL:
            if (current_fault == DTC_PHASE_CURRENT_FAULT ||
                telem->mosfet_temp_c >= ctx->config.temp_fatal_c ||
                telem->min_cell_voltage_v <= ctx->config.volt_min_cell_crit_v) {
                set_state(ctx, LIMP_STATE_L2, current_fault, now);
            } else if (telem->mosfet_temp_c >= ctx->config.temp_crit_c) {
                set_state(ctx, LIMP_STATE_L1, current_fault, now);
            } else if (current_fault != DTC_NONE) {
                set_state(ctx, LIMP_STATE_THROTTLED, current_fault, now);
            }
            break;

        case LIMP_STATE_THROTTLED:
            if (current_fault == DTC_PHASE_CURRENT_FAULT ||
                telem->mosfet_temp_c >= ctx->config.temp_fatal_c ||
                telem->min_cell_voltage_v <= ctx->config.volt_min_cell_crit_v) {
                set_state(ctx, LIMP_STATE_L2, current_fault, now);
            } else if (telem->mosfet_temp_c >= ctx->config.temp_crit_c) {
                set_state(ctx, LIMP_STATE_L1, current_fault, now);
            } else if (dwell >= ctx->config.min_dwell_time_ms) {
                // Умова повернення з гістерезисом
                if (telem->mosfet_temp_c <= (ctx->config.temp_warn_c - ctx->config.temp_hysteresis_c) &&
                    telem->min_cell_voltage_v > (ctx->config.volt_min_cell_warn_v + 0.15f)) {
                    set_state(ctx, LIMP_STATE_NORMAL, DTC_NONE, now);
                }
            }
            break;

        case LIMP_STATE_L1:
            if (current_fault == DTC_PHASE_CURRENT_FAULT ||
                telem->mosfet_temp_c >= ctx->config.temp_fatal_c ||
                telem->min_cell_voltage_v <= ctx->config.volt_min_cell_crit_v) {
                set_state(ctx, LIMP_STATE_L2, current_fault, now);
            } else if (dwell >= (ctx->config.min_dwell_time_ms * 2)) {
                // Відновлення до Throttled можливе лише при істотному охолодженні
                if (telem->mosfet_temp_c <= (ctx->config.temp_crit_c - ctx->config.temp_hysteresis_c) &&
                    telem->min_cell_voltage_v > (ctx->config.volt_min_cell_warn_v + 0.2f)) {
                    set_state(ctx, LIMP_STATE_THROTTLED, DTC_NONE, now);
                }
            }
            break;

        case LIMP_STATE_L2:
            // З L2 автоматичного виходу вгору немає: режим тримається до завершення польоту
            break;

        case LIMP_STATE_CRITICAL_LAND:
        case LIMP_STATE_LATCHED:
        default:
            break;
    }

    // 3. Формування вихідних керуючих параметрів та скидання навантаження
    out->current_state = ctx->state;
    out->active_dtc = ctx->latched_dtc;

    switch (ctx->state) {
        case LIMP_STATE_NORMAL:
            out->max_allowed_current_a = ctx->config.nominal_current_max_a;
            out->target_pwm_freq_hz = 25000;
            out->enable_tier1_nav = true;
            out->enable_tier2_sbc = true;
            out->enable_tier3_payload = true;
            break;

        case LIMP_STATE_THROTTLED: {
            // Лінійний спад струму в межах вікна температур
            float factor = (ctx->config.temp_crit_c - telem->mosfet_temp_c) /
                           (ctx->config.temp_crit_c - ctx->config.temp_warn_c);
            if (factor < 0.0f) factor = 0.0f;
            if (factor > 1.0f) factor = 1.0f;
            out->max_allowed_current_a = ctx->config.limp_l1_current_max_a +
                factor * (ctx->config.nominal_current_max_a - ctx->config.limp_l1_current_max_a);
            out->target_pwm_freq_hz = 16000;
            out->enable_tier1_nav = true;
            out->enable_tier2_sbc = true;
            out->enable_tier3_payload = true;
            break;
        }

        case LIMP_STATE_L1:
            out->max_allowed_current_a = ctx->config.limp_l1_current_max_a;
            out->target_pwm_freq_hz = 10000;
            out->enable_tier1_nav = true;
            out->enable_tier2_sbc = true;
            out->enable_tier3_payload = false; // Tier 3 знеструмлено (підвіс, світло)
            break;

        case LIMP_STATE_L2:
        case LIMP_STATE_CRITICAL_LAND:
        case LIMP_STATE_LATCHED:
            out->max_allowed_current_a = ctx->config.limp_l2_current_max_a;
            out->target_pwm_freq_hz = 8000;
            out->enable_tier1_nav = true;
            out->enable_tier2_sbc = false;     // Tier 2 знеструмлено (SBC/AI вимкнено)
            out->enable_tier3_payload = false; // Tier 3 знеструмлено
            break;
    }
}
