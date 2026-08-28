// Повертаємо код першої НЕпройденої умови, або PREFLIGHT_OK.
// Порядок пунктів — від найдешевшого й найважливішого до решти.
preflight_result_t preflight_check(const vehicle_state_t *v) {
    if (v == NULL)                    return PF_INTERNAL_ERR;

    // 1. Живлення: сідати в повітрі — найгірший сценарій.
    if (v->battery_mv < BATT_MIN_MV)  return PF_LOW_BATTERY;

    // 2. Навігація: без фіксу GPS немає утримання позиції.
    if (v->gps_sats < GPS_MIN_SATS)   return PF_NO_GPS_FIX;

    // 3. Орієнтація: несходимий компас = політ у випадковий бік.
    if (!v->compass_calibrated)       return PF_COMPASS_UNCAL;

    // 4. Зв'язок: без каналу з оператором злітати не можна.
    if (!v->rc_link_ok)               return PF_NO_RC_LINK;

    // 5. Стан датчиків орієнтації.
    if (!v->imu_healthy)              return PF_IMU_FAULT;

    return PF_OK;   // усі пункти зелені — лише тепер дозволяємо зброїти
}
