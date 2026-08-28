#include "return_budget.h"

/* Періодичний обробник навігаційного контуру (2 Гц) */
void navigation_step_return_check(void) {
    return_telemetry_t telem;
    
    /* Зчитування координат із GNSS/EKF */
    telem.pos_current_ned[0] = g_vehicle_state.pos_n;
    telem.pos_current_ned[1] = g_vehicle_state.pos_e;
    telem.pos_current_ned[2] = g_vehicle_state.pos_d;

    telem.pos_home_ned[0] = g_home_position.pos_n;
    telem.pos_home_ned[1] = g_home_position.pos_e;
    telem.pos_home_ned[2] = g_home_position.pos_d;

    /* Вектор горизонтального вітру за оцінкою EKF */
    telem.wind_ned[0] = g_wind_estimator.wind_north_ms;
    telem.wind_ned[1] = g_wind_estimator.wind_east_ms;

    /* Стан силового акумулятора */
    telem.voltage_v           = g_battery_monitor.voltage_v;
    telem.current_a           = g_battery_monitor.current_a;
    telem.energy_remaining_wh = g_battery_monitor.remaining_energy_wh;
    telem.soc_ratio           = g_battery_monitor.soc_normalized;
    telem.r_internal_ohms     = g_battery_monitor.estimated_r_int;
    telem.battery_temp_c      = g_battery_monitor.temperature_c;

    return_budget_result_t budget;
    int32_t status = return_budget_update(&g_return_budget_ctx, &telem, &budget);

    if (status == RETURN_OK) {
        if (budget.rtl_mandatory) {
            /* Примусова активація RTL при досягненні точки неповернення */
            flight_mode_set_mandatory_rtl(RTL_TRIGGER_ENERGY_PNR);
        } else if (budget.state == RETURN_STATE_CAUTION) {
            gcs_send_warning("Energy margin low: return path wind degraded");
        }
    } else if (status == RETURN_ERR_HEADWIND_TOO_HIGH || status == RETURN_ERR_CROSSWIND_LIMIT) {
        /* Вітер не дозволяє дістатися точки Home — аварійна посадка */
        flight_mode_set_emergency_landing();
    }
}
