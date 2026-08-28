/* Накопичений кут камери на момент кадру, рад, по трьох осях. */
typedef struct { double ax, ay, az; } att;

/* Приріст орієнтації за один кадр: інтегруємо ω від t0 до t1 (відеочас).
   subdt — крок інтегрування в секундах (дрібніший за відлік гіро). */
static att integrate_frame(const gyro_sample *g, size_t n, const time_sync *s,
                           double t0, double t1, double subdt)
{
    att d = {0, 0, 0};
    for (double t = t0; t < t1; t += subdt) {
        double step = subdt;
        if (t + step > t1) step = t1 - t;        /* останній шматок — рівно до t1 */
        double tg = frame_to_gyro_time(s, t + 0.5 * step);  /* гіро в СЕРЕДИНІ кроку */
        double wx, wy, wz;
        gyro_at(g, n, tg, &wx, &wy, &wz);
        d.ax += wx * step;                        /* ω·dt — приріст кута за крок */
        d.ay += wy * step;
        d.az += wz * step;
    }
    return d;
}

/* Накопичені кути для всіх кадрів. times[k] — момент кадру k у відеочасі.
   out[k] — орієнтація камери на момент кадру k (відносно кадру 0). */
void build_attitudes(const gyro_sample *g, size_t n, const time_sync *s,
                     const double *times, size_t frames, att *out)
{
    const double SUBDT = 0.0005;                  /* 0.5 мс — дрібніше за крок гіро */
    out[0].ax = out[0].ay = out[0].az = 0.0;      /* кадр 0 — точка відліку */
    for (size_t k = 1; k < frames; ++k) {
        att d = integrate_frame(g, n, s, times[k-1], times[k], SUBDT);
        out[k].ax = out[k-1].ax + d.ax;           /* накопичуємо приріст */
        out[k].ay = out[k-1].ay + d.ay;
        out[k].az = out[k-1].az + d.az;
    }
}
