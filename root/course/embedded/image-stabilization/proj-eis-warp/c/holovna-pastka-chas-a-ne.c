/* Розбіжність між рухом по гіро і рухом по відео при заданій прив'язці.
   motion_video[k] — виміряний по пікселях кут між кадрами k−1 і k (рад);
   менше значення = краща синхронізація. Перебором t_off шукаємо мінімум. */
static double sync_cost(const gyro_sample *g, size_t n, double t_off, double scale,
                        const double *times, const double *motion_video, size_t frames)
{
    time_sync s = { t_off, scale };
    double err = 0.0;
    for (size_t k = 1; k < frames; ++k) {
        att d = integrate_frame(g, n, &s, times[k-1], times[k], 0.0005);
        double motion_gyro = sqrt(d.ax*d.ax + d.ay*d.ay + d.az*d.az); /* кут по гіро */
        double diff = motion_gyro - motion_video[k];
        err += diff * diff;                  /* сума квадратів розбіжностей */
    }
    return err;
}

/* Грубий пошук найкращого зсуву в діапазоні ±range секунд із кроком step. */
double find_offset(const gyro_sample *g, size_t n, double scale,
                   const double *times, const double *motion_video, size_t frames,
                   double range, double step)
{
    double best_off = 0.0, best_cost = 1e300;
    for (double off = -range; off <= range; off += step) {
        double c = sync_cost(g, n, off, scale, times, motion_video, frames);
        if (c < best_cost) { best_cost = c; best_off = off; }  /* тримаємо мінімум */
    }
    return best_off;            /* далі уточнюють дрібнішим кроком навколо best_off */
}
