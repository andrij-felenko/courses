#include "return_budget.h"

/*
 * Прив'язка оцінювача до польотного циклу автопілота.
 * Функції нижче реалізує сам автопілот — тут лише їхній контракт.
 */
typedef enum {
    RTL_REASON_BATTERY_PNR = 1,
    RTL_REASON_CROSSWIND   = 2,
    RTL_REASON_HEADWIND    = 3
} rtl_reason_t;

/* Значення з MAVLink MAV_SEVERITY */
#define MAV_SEVERITY_CRITICAL 2
#define MAV_SEVERITY_WARNING  4

extern void read_sensors_and_ekf(return_telemetry_t* out_telem);
extern void trigger_failsafe_rtl(rtl_reason_t reason);
extern void trigger_emergency_land(rtl_reason_t reason);
extern void send_mavlink_statustext(uint8_t severity, const char* text);
extern void log_flash_event(const char* tag, float value);
extern void handle_navigation_error(int32_t status);

#define NAV_PERIOD_SEC 0.5f  /* контур крутиться на 2 Гц */

static return_budget_handle_t g_return_budget_handle;
static bool g_rtl_engaged;          /* фіксуємо, що RTL уже наказано */
static float g_since_warning_sec;   /* щоб не залити пульт попередженнями */
static uint32_t g_bad_frames;       /* поспіль зіпсовані кадри телеметрії */

/* Виклик один раз під час старту, після завантаження параметрів планера. */
int32_t navigation_return_budget_boot(void) {
    static const return_config_t airframe = {
        .v_air_min_ms          = 12.0f,
        .v_air_max_ms          = 28.0f,
        .v_best_range_still_ms = 16.0f,
        .c_ind                 = 1500.0f,
        .c_par                 = 0.02f,
        .p_avionics_watts      = 12.0f,
        .rtl_safe_altitude_m   = 80.0f,
        .v_climb_ms            = 3.0f,
        .p_climb_watts         = 450.0f,
        .p_hover_watts         = 900.0f,
        .t_land_maneuver_sec   = 25.0f,
        .reserve_margin_ratio  = 0.25f,
        .filter_time_constant_s = 8.0f,
        .nominal_energy_wh     = 220.0f,
        .cell_v_cutoff         = 3.3f,
        .cell_count            = 6
    };

    g_rtl_engaged = false;
    g_since_warning_sec = 0.0f;
    g_bad_frames = 0;
    return return_budget_init(&g_return_budget_handle, &airframe);
}

void navigation_periodic_2hz(void) {
    return_telemetry_t telem;
    read_sensors_and_ekf(&telem);

    return_budget_result_t budget;
    const int32_t status =
        return_budget_update(&g_return_budget_handle, &telem, NAV_PERIOD_SEC, &budget);

    g_since_warning_sec += NAV_PERIOD_SEC;

    switch (status) {
        case RETURN_OK:
            g_bad_frames = 0;
            break;

        case RETURN_ERR_CROSSWIND_LIMIT:
            log_flash_event("CROSSWIND_LIMIT", budget.v_air_optimal_ms);
            send_mavlink_statustext(MAV_SEVERITY_CRITICAL, "Crosswind exceeds airspeed: landing here");
            trigger_emergency_land(RTL_REASON_CROSSWIND);
            return;

        case RETURN_ERR_HEADWIND_TOO_HIGH:
            log_flash_event("HEADWIND_LIMIT", budget.v_ground_ret_ms);
            send_mavlink_statustext(MAV_SEVERITY_CRITICAL, "Headwind stops return: landing here");
            trigger_emergency_land(RTL_REASON_HEADWIND);
            return;

        default:
            /* Один зіпсований кадр — не подія; десять поспіль (5 с) — уже відмова давачів. */
            if (++g_bad_frames >= 10) {
                handle_navigation_error(status);
                g_bad_frames = 0;
            }
            return;
    }

    if (budget.rtl_mandatory) {
        if (budget.state == RETURN_STATE_EMERGENCY_LAND) {
            log_flash_event("PACK_SAG_V", budget.projected_sag_voltage_v);
            send_mavlink_statustext(MAV_SEVERITY_CRITICAL, "Battery sag below cutoff: landing here");
            trigger_emergency_land(RTL_REASON_BATTERY_PNR);
        } else if (!g_rtl_engaged) {
            g_rtl_engaged = true;
            log_flash_event("PNR_RETURN_WH", budget.e_return_total_wh);
            log_flash_event("PNR_USABLE_WH", budget.e_usable_compensated_wh);
            send_mavlink_statustext(MAV_SEVERITY_CRITICAL, "Point of no return: RTL engaged");
            trigger_failsafe_rtl(RTL_REASON_BATTERY_PNR);
        }
    } else if (budget.state == RETURN_STATE_CAUTION && g_since_warning_sec >= 5.0f) {
        g_since_warning_sec = 0.0f;
        send_mavlink_statustext(MAV_SEVERITY_WARNING, "PNR approaching: wind reserve critical");
    }
}
