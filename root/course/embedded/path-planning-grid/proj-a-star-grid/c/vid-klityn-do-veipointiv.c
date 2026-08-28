// Один вейпойнт у клітинних координатах.
typedef struct { int x, y; } Waypoint;

// Прорідити шлях out[] до поворотних точок → wp[]. Повертає їхню кількість.
static int path_to_waypoints(const int32_t *path, int n,
                             Waypoint *wp, int wp_cap) {
    if (n == 0) return 0;
    int m = 0;
    // Старт — завжди вейпойнт.
    wp[m].x = x_of(path[0]); wp[m].y = y_of(path[0]); m++;

    for (int i = 1; i < n - 1; i++) {
        int px = x_of(path[i - 1]), py = y_of(path[i - 1]);
        int cx = x_of(path[i]),     cy = y_of(path[i]);
        int nx = x_of(path[i + 1]), ny = y_of(path[i + 1]);

        int dir_in_x  = cx - px, dir_in_y  = cy - py;   // куди прийшли
        int dir_out_x = nx - cx, dir_out_y = ny - cy;   // куди підемо

        // Напрямок змінився → поворот → це вейпойнт.
        if (dir_in_x != dir_out_x || dir_in_y != dir_out_y) {
            if (m >= wp_cap) return m;   // буфер вичерпано — віддамо що є
            wp[m].x = cx; wp[m].y = cy; m++;
        }
    }
    // Ціль — завжди вейпойнт.
    if (m < wp_cap) {
        wp[m].x = x_of(path[n - 1]); wp[m].y = y_of(path[n - 1]); m++;
    }
    return m;
}
