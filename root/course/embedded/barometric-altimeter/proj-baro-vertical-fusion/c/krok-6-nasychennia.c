static float clampf(float x, float lo, float hi) {
    return x < lo ? lo : (x > hi ? hi : x);
}

// Насичена версія кроку злиття: захищає інтеграли від розбігання.
void vfusion_update_safe(vfusion_t *f, float az_world, float baro_alt,
                         float dt, int have_baro) {
    // 1) обмежити вхідне прискорення руху фізично розумним діапазоном
    az_world = clampf(az_world, -30.0f, 30.0f);     // ~3g угору/вниз

    if (!f->started) {
        f->alt = baro_alt;  f->vz = 0.0f;  f->started = 1;  return;
    }

    // 2) прогноз (як у кроці 4)
    float vz_new = f->vz + az_world * dt;
    vz_new = clampf(vz_new, -40.0f, 40.0f);         // швидкість фізично обмежена
    f->alt += 0.5f * (f->vz + vz_new) * dt;
    f->vz   = vz_new;

    // 3) корекція барометром лише на новий відлік
    if (have_baro) {
        float err = baro_alt - f->alt;
        // захист від абсурдної розбіжності (збій барометра): не тягнутися за нею
        err = clampf(err, -50.0f, 50.0f);
        float k1 = 2.0f / f->tau;
        float k2 = 1.0f / (f->tau * f->tau);
        f->alt += k1 * err * dt;
        f->vz  += k2 * err * dt;
    }
}
