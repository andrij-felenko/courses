preflight_result_t preflight_for_mode(const vehicle_state_t *v, flight_mode_t mode) {
    // Спільне ядро — те, без чого не злетиш у ЖОДНОМУ режимі.
    if (v->battery_mv < BATT_MIN_MV)  return PF_LOW_BATTERY;
    if (!v->rc_link_ok)               return PF_NO_RC_LINK;
    if (!v->imu_healthy)              return PF_IMU_FAULT;

    // Додаткові умови — лише для режимів, що спираються на позицію.
    if (mode_needs_position(mode)) {
        if (v->gps_sats < GPS_MIN_SATS)  return PF_NO_GPS_FIX;
        if (!v->compass_calibrated)      return PF_COMPASS_UNCAL;
    }
    return PF_OK;
}
