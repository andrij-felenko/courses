// Головний публічний виклик планувальника.
// Повертає кількість вейпойнтів у wp[], або 0, якщо шляху немає.
int plan_path(int sx, int sy, int gx, int gy, Waypoint *wp, int wp_cap) {
    static int32_t raw[N_CELLS];        // буфер сирого шляху (статичний, не стек!)

    if (!astar_search(sx, sy, gx, gy))
        return 0;                       // шляху не існує

    int n = astar_reconstruct(gx, gy, raw, N_CELLS);
    if (n == 0) return 0;               // не влізло (буфер малий)

    return path_to_waypoints(raw, n, wp, wp_cap);
}
