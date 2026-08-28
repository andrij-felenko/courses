// Дзеркало клапана на вході: стежимо ЩОРАЗУ, поки летимо в режимі з позицією.
void position_modes_watchdog(uint32_t now_ms) {
    if (!mode_needs_position(current_mode))
        return;                                  // висотним/ручним режимам це байдуже

    if (ahrs.get_ekf_position_ok()) {
        ekf_bad_since_ms = 0;                     // оцінка знову певна — лічильник скинути
        return;
    }
    if (ekf_bad_since_ms == 0)
        ekf_bad_since_ms = now_ms;                // відзначили, коли оцінка «зіпсувалась»

    // терпимо коротку просадку (глюк може бути миттєвим), але не довше за поріг:
    if (now_ms - ekf_bad_since_ms > EKF_FS_MS) {  // напр. 2000 мс поспіль
        gcs_send_text("EKF failsafe: втрата позиції");
        set_mode(MODE_ALTHOLD);                    // відступ на сходинку нижче — тримаємо ВИСОТУ
    }
}
