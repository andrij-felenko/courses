// Звірити зчитану місію з еталоном. 1 — усе збіглося в межах допуску.
// Цілі 1e-7° декодуються назад у градуси прямо тут, множенням на 1e-7.
int verify_mission(const mavlink_mission_item_int_t *items, int n_read,
                   const wp_t *expected, int n_exp, double tol_m) {
    // Пастка №3 у зародку: звіряти можна ЛИШЕ повний список.
    if (n_read != n_exp) {
        printf("звірка НЕМОЖЛИВА: зчитано %d, а задумано %d — "
               "список неповний, будь-яка звірка тут бреше\n", n_read, n_exp);
        return 0;
    }
    printf("%2s  %-16s %12s %12s %7s %6s  результат\n",
           "#", "команда", "lat", "lon", "alt", "frame");
    const double DEG_M = 111111.0;      // 1° широти ≈ 111 111 м
    int ok_all = 1;
    for (int i = 0; i < n_exp; i++) {
        const mavlink_mission_item_int_t *it = &items[i];
        double lat = it->x * 1e-7, lon = it->y * 1e-7;   // ЦІЛЕ 1e-7° → градуси
        // горизонтальна відстань між зчитаним і задуманим, у метрах (для довготи — ×cos)
        double dlat_m = (it->x - expected[i].x) * 1e-7 * DEG_M;
        double dlon_m = (it->y - expected[i].y) * 1e-7 * DEG_M * cos(lat * M_PI / 180.0);
        double dist_m = hypot(dlat_m, dlon_m);

        char why[64] = ""; int bad = 0;
        if (it->command != expected[i].command) { bad = 1; strcat(why, "команда "); }
        if (it->frame   != expected[i].frame)   { bad = 1; strcat(why, "frame(висота!) "); }
        if (dist_m      > tol_m)                { bad = 1; strcat(why, "зсув "); }
        if (fabs(it->z - expected[i].z) > tol_m){ bad = 1; strcat(why, "висота "); }
        if (bad) ok_all = 0;
        printf("%2u  %-16u %12.7f %12.7f %7.1f %6u  %s\n",
               it->seq, it->command, lat, lon, (double)it->z, it->frame,
               bad ? why : "OK");
    }
    return ok_all;
}
