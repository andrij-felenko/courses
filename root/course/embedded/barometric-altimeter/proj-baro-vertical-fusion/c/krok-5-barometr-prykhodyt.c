// Скелет головного циклу польотного контролера (спрощено).
void control_loop_step(vfusion_t *f, accel_cal_t *cal, const mat3 *R) {
    static float t_prev = 0.0f;
    float t_now = time_seconds();
    float dt = t_now - t_prev;
    t_prev = t_now;
    if (dt <= 0.0f || dt > 0.1f) return;    // захист від збоїв таймера/зависань

    // --- акселерометр: щокроку ---
    vec3 a = accel_read();                   // сирі м/с² у системі тіла
    a.x -= cal->accel_bias.x;                // зняти зсув (крок 1)
    a.y -= cal->accel_bias.y;
    a.z -= cal->accel_bias.z;
    float az = world_vertical_accel(R, a);   // оберт у світ + мінус g (крок 2)

    // --- барометр: лише коли є новий відлік ---
    int   have_baro = baro_data_ready();     // true лише на нових даних тиску
    float baro_alt  = f->alt;                // за замовчуванням — не тягнути
    if (have_baro) {
        float p = baro_read_pressure();      // Па
        baro_alt = baro_relative_altitude(p);// відносна висота (крок 3)
    }

    vfusion_update(f, az, baro_alt, dt, have_baro);   // злиття (крок 4)

    // f->alt, f->vz — готові для контуру утримання висоти
}
