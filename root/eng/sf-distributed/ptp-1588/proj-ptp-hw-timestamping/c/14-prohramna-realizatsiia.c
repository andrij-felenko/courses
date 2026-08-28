typedef struct {
    double kp;                  // Пропорційний коефіцієнт (1/с)
    double ki;                  // Інтегральний коефіцієнт (1/с^2)
    double drift_ppb;           // Накопичений дрейф частоти (ppb)
    double max_drift_ppb;       // Граничне підстроювання (+-100000 ppb)
    int64_t last_sync_ns;       // Час попереднього вимірювання
    int count;                  // Лічильник стабілізації
} ptp_pi_servo_t;

void ptp_servo_init(ptp_pi_servo_t *s) {
    s->kp = 0.7;
    s->ki = 0.3;
    s->drift_ppb = 0.0;
    s->max_drift_ppb = 100000.0; // +-100 ppm
    s->last_sync_ns = 0;
    s->count = 0;
}

double ptp_servo_sample(ptp_pi_servo_t *s, int64_t offset_ns, int64_t local_ts_ns) {
    if (s->last_sync_ns == 0) {
        s->last_sync_ns = local_ts_ns;
        return 0.0;
    }

    double dt = (double)(local_ts_ns - s->last_sync_ns) / 1e9;
    s->last_sync_ns = local_ts_ns;

    if (dt <= 0.0 || dt > 2.0) {
        dt = 1.0; // Захист від втрати пакетів
    }

    // Інтегральна складова: накопичення дрейфу генератора
    s->drift_ppb += s->ki * (double)offset_ns * dt;

    // Обмеження інтегратора (Anti-windup)
    if (s->drift_ppb > s->max_drift_ppb) s->drift_ppb = s->max_drift_ppb;
    if (s->drift_ppb < -s->max_drift_ppb) s->drift_ppb = -s->max_drift_ppb;

    // Результуюче коригування частоти
    double adj_ppb = s->kp * (double)offset_ns + s->drift_ppb;

    if (adj_ppb > s->max_drift_ppb) adj_ppb = s->max_drift_ppb;
    if (adj_ppb < -s->max_drift_ppb) adj_ppb = -s->max_drift_ppb;

    return adj_ppb;
}
