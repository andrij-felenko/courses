void navigation_periodic_2hz(void) {
    return_telemetry_t telem;
    read_sensors_and_ekf(&telem);

    return_budget_result_t budget;
    int32_t status = return_budget_update(&g_return_budget_handle, &telem, &budget);

    if (status == RETURN_OK) {
        if (budget.rtl_mandatory) {
            trigger_failsafe_rtl(RTL_REASON_BATTERY_PNR);
        } else if (budget.state == RETURN_STATE_CAUTION) {
            send_mavlink_statustext(MAV_SEVERITY_WARNING, "PNR approaching: wind reserve critical");
        }
    } else {
        handle_navigation_error(status);
    }
}
