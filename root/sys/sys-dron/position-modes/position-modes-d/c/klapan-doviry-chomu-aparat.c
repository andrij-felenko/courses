// Спрощена перевірка входу в режим із позицією (у дусі AP_Arming / set_mode).
// Повертає true, якщо оцінка положення варта того, щоб на ній тримати точку.
static bool position_estimate_ok(void) {
    if (gps.status() < GPS_OK_FIX_3D)   // немає навіть 3D-прив'язки
        return false;
    if (gps.get_hdop() > 140)           // HDOP 1.40 (тут — соті) — геометрія кепська
        return false;
    // головне слово — за фільтром стану: чи ЗБІГЛАСЯ його оцінка положення?
    return ahrs.get_ekf_position_ok();  // EKF сам стежить за своїм розкидом
}

bool set_mode_loiter(void) {
    if (!position_estimate_ok()) {
        gcs_send_text("Loiter: немає певної позиції");  // повідомити пілота
        return false;                                    // ВІДХИЛИТИ вхід у режим
    }
    enter_mode(MODE_LOITER);            // усе гаразд — пускаємо
    return true;
}
