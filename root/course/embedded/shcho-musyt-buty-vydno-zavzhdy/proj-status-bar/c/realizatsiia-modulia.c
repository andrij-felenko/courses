#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

/* --- Конфігурація та константи семантичних кольорів (RGB565) --- */
#define COLOR_RGB565_GREEN       0x2560  /* Норма: #27ae60 */
#define COLOR_RGB565_YELLOW      0xFCC0  /* Увага / Деградація: #f39c12 */
#define COLOR_RGB565_RED         0xC1C5  /* Критична відмова: #c0392b */
#define COLOR_RGB565_GRAY        0x7BEF  /* Застарілі дані: #7f8c8d */
#define COLOR_RGB565_WHITE       0xFFFF  /* Основний текст */
#define COLOR_RGB565_BLACK       0x0000  /* Тінь / Контур / Фон */

#define STALE_WARN_TIMEOUT_MS    1000U
#define STALE_CRIT_TIMEOUT_MS    3000U
#define HYSTERESIS_VOLTAGE_MV    250U    /* 0.25 В */
#define HYSTERESIS_DEBOUNCE_MS   1500U   /* 1.5 с на повернення в норму */

#define STATUS_BAR_HEIGHT        28
#define MAX_TEXT_LEN             64

typedef enum {
    SEV_NORMAL = 0,
    SEV_WARNING,
    SEV_CRITICAL,
    SEV_STALE
} SeverityLevel;

typedef enum {
    NAV_MANUAL = 0,
    NAV_ALTHOLD,
    NAV_POSHOLD,
    NAV_AUTO_MISSION,
    NAV_GUIDED,
    NAV_FAILSAFE_RTL
} FlightMode;

typedef struct {
    float roll_deg;
    float pitch_deg;
    float altitude_amsl_m;
    float altitude_agl_m;
    float ground_speed_mps;
    float vertical_speed_mps;
} SpatialState;

typedef struct {
    uint16_t voltage_mv;
    int16_t  current_cda;     /* Сантиампери (0.01 А) */
    uint16_t consumed_mah;
    uint8_t  battery_soc_pct;
    int8_t   esc_temperature_c;
} PowerHealth;

typedef struct {
    int8_t   rssi_dbm;
    int8_t   snr_db;
    uint8_t  link_quality_pct;
    uint16_t round_trip_time_ms;
} LinkQuality;

typedef struct {
    SpatialState state;
    FlightMode   mode;
    bool         is_armed;
    PowerHealth  power;
    LinkQuality  link;
    uint32_t     timestamp_ms;
} TelemetryFrame;

typedef struct {
    SeverityLevel overall_severity;
    SeverityLevel power_severity;
    SeverityLevel link_severity;
    uint16_t      filtered_voltage_mv;
    uint32_t      last_warn_time_ms;
    char          mode_str[24];
    char          power_str[28];
    char          link_str[28];
    char          state_str[36];
} StatusBarPresenter;

/* Перетворення коду режиму в фіксований текстовий анонсатор */
static const char* flight_mode_to_string(FlightMode mode, bool armed) {
    if (!armed) {
        return "DISARMED";
    }
    switch (mode) {
        case NAV_MANUAL:       return "ARM: MANUAL";
        case NAV_ALTHOLD:      return "ARM: ALTHOLD";
        case NAV_POSHOLD:      return "ARM: POSHOLD";
        case NAV_AUTO_MISSION: return "ARM: AUTO";
        case NAV_GUIDED:       return "ARM: GUIDED";
        case NAV_FAILSAFE_RTL: return "FAILSAFE: RTL";
        default:               return "ARM: UNKNOWN";
    }
}

/* Оцінка стану живлення з гістерезисом та захистом від брязкоту навантаження */
static SeverityLevel evaluate_power_health(StatusBarPresenter *pres, uint16_t v_mv, uint32_t now_ms) {
    const uint16_t v_warn_thresh = 14800; /* 14.8 В */
    const uint16_t v_crit_thresh = 14000; /* 14.0 В */

    if (v_mv < v_crit_thresh) {
        pres->power_severity = SEV_CRITICAL;
        pres->last_warn_time_ms = now_ms;
        return SEV_CRITICAL;
    }

    if (v_mv < v_warn_thresh) {
        if (pres->power_severity == SEV_CRITICAL) {
            /* Відновлення з червоного в жовтий вимагає подолання гістерезису */
            if (v_mv >= (v_crit_thresh + HYSTERESIS_VOLTAGE_MV)) {
                pres->power_severity = SEV_WARNING;
            }
        } else {
            pres->power_severity = SEV_WARNING;
        }
        pres->last_warn_time_ms = now_ms;
        return pres->power_severity;
    }

    /* Напруга вище порогу попередження: перевірка гістерезису повернення в норму */
    if (pres->power_severity == SEV_WARNING) {
        if (v_mv >= (v_warn_thresh + HYSTERESIS_VOLTAGE_MV) &&
            (now_ms - pres->last_warn_time_ms >= HYSTERESIS_DEBOUNCE_MS)) {
            pres->power_severity = SEV_NORMAL;
        }
    } else {
        pres->power_severity = SEV_NORMAL;
    }

    return pres->power_severity;
}

/* Оновлення моделі представлення на основі свіжого телеметричного кадру */
void status_bar_update(StatusBarPresenter *pres, const TelemetryFrame *frame, uint32_t now_ms) {
    uint32_t age_ms = now_ms - frame->timestamp_ms;

    /* 1. Перевірка актуальності телеметрії (Data Staleness) */
    if (age_ms >= STALE_CRIT_TIMEOUT_MS) {
        pres->link_severity = SEV_CRITICAL;
        pres->overall_severity = SEV_CRITICAL;
        snprintf(pres->link_str, sizeof(pres->link_str), "[X LOST: %.1fs]", (float)age_ms / 1000.0f);
    } else if (age_ms >= STALE_WARN_TIMEOUT_MS) {
        pres->link_severity = SEV_STALE;
        pres->overall_severity = SEV_WARNING;
        snprintf(pres->link_str, sizeof(pres->link_str), "[⧗ STALE: %.1fs]", (float)age_ms / 1000.0f);
    } else {
        /* Сигнал свіжий — оцінюємо якість зв'язку */
        if (frame->link.link_quality_pct < 50 || frame->link.rssi_dbm < -100) {
            pres->link_severity = SEV_WARNING;
            snprintf(pres->link_str, sizeof(pres->link_str), "[! LQ:%u%% %ddBm]",
                     frame->link.link_quality_pct, frame->link.rssi_dbm);
        } else {
            pres->link_severity = SEV_NORMAL;
            snprintf(pres->link_str, sizeof(pres->link_str), "[OK LQ:%u%% %ddBm]",
                     frame->link.link_quality_pct, frame->link.rssi_dbm);
        }
    }

    /* 2. Оцінка живлення */
    SeverityLevel pwr_sev = evaluate_power_health(pres, frame->power.voltage_mv, now_ms);
    float volt_f = (float)frame->power.voltage_mv / 1000.0f;
    float curr_f = (float)frame->power.current_cda / 100.0f;

    if (pwr_sev == SEV_CRITICAL) {
        snprintf(pres->power_str, sizeof(pres->power_str), "[X CRIT %.1fV %.1fA]", volt_f, curr_f);
    } else if (pwr_sev == SEV_WARNING) {
        snprintf(pres->power_str, sizeof(pres->power_str), "[! LOW %.1fV %.1fA]", volt_f, curr_f);
    } else {
        snprintf(pres->power_str, sizeof(pres->power_str), "[OK %.1fV %u%%]", volt_f, frame->power.battery_soc_pct);
    }

    /* 3. Режим автопілота */
    snprintf(pres->mode_str, sizeof(pres->mode_str), "%s", flight_mode_to_string(frame->mode, frame->is_armed));

    /* 4. Просторовий стан */
    snprintf(pres->state_str, sizeof(pres->state_str), "H:%.0fm GS:%.1fm/s VSI:%+.1f",
             frame->state.altitude_agl_m, frame->state.ground_speed_mps, frame->state.vertical_speed_mps);

    /* Загальний рівень важливості для окантовки панелі */
    if (pres->link_severity == SEV_CRITICAL || pwr_sev == SEV_CRITICAL || frame->mode == NAV_FAILSAFE_RTL) {
        pres->overall_severity = SEV_CRITICAL;
    } else if (pres->link_severity == SEV_WARNING || pres->link_severity == SEV_STALE || pwr_sev == SEV_WARNING) {
        pres->overall_severity = SEV_WARNING;
    } else {
        pres->overall_severity = SEV_NORMAL;
    }
}

/* Отримання кольору шрифту та фону за рівнем важливості */
uint16_t status_bar_get_color(SeverityLevel sev) {
    switch (sev) {
        case SEV_NORMAL:   return COLOR_RGB565_GREEN;
        case SEV_WARNING:  return COLOR_RGB565_YELLOW;
        case SEV_CRITICAL: return COLOR_RGB565_RED;
        case SEV_STALE:    return COLOR_RGB565_GRAY;
        default:           return COLOR_RGB565_WHITE;
    }
}
