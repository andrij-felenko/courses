void control_tick(void) {
    // ── ЛАНКА 1: давачі — сирі, шумні, часткові виміри ────────────────
    imu_sample_t imu;
    imu_read(&imu);                       // гіро (рад/с) + акселерометр (g)

    // ── ЛАНКА 2: оцінювач — з шумних вимірів один чистий СТАН ──────────
    //   поєднує швидкий гіроскоп і повільний акселерометр (доповняльний
    //   фільтр); на виході — кут, якому можна вірити, а не сирий давач
    state_t st;
    estimator_update(&imu, DT_S, &st);    // st.roll, st.pitch, st.yaw_rate ...

    // ── ЛАНКА 3: керування — неузгодженість і команда ─────────────────
    setpoint_t sp;
    setpoint_get(&sp);                    // бажаний стан: від пілота АБО від місії

    float err_roll = sp.roll - st.roll;           // КЛЮЧОВЕ: від ОЦІНКИ, не від давача
    float u_roll   = pid_step(&pid_roll, err_roll, DT_S);
    float err_pitch = sp.pitch - st.pitch;
    float u_pitch   = pid_step(&pid_pitch, err_pitch, DT_S);

    // ── ЛАНКА 4: виконавчі механізми — команда у фізичну дію ───────────
    motor_cmd_t m = mixer(sp.throttle, u_roll, u_pitch, /*u_yaw=*/0.0f);
    motors_write(&m);                     // ESC ← мотори; апарат рухається
}
