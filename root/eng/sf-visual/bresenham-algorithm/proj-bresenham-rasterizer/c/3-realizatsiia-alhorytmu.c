void plot_circle_octants_c(int32_t cx, int32_t cy, int32_t x, int32_t y, PixelCallbackC plot, void* user_data) {
    plot(cx + x, cy + y, user_data);
    plot(cx - x, cy + y, user_data);
    plot(cx + x, cy - y, user_data);
    plot(cx - x, cy - y, user_data);
    plot(cx + y, cy + x, user_data);
    plot(cx - y, cy + x, user_data);
    plot(cx + y, cy - x, user_data);
    plot(cx - y, cy - x, user_data);
}

void bresenham_draw_circle_c(int32_t cx, int32_t cy, int32_t radius, PixelCallbackC plot, void* user_data) {
    int32_t x = 0;
    int32_t y = radius;
    int32_t d = 3 - 2 * radius;
    
    plot_circle_octants_c(cx, cy, x, y, plot, user_data);
    
    while (y >= x) {
        x++;
        if (d > 0) {
            y--;
            d = d + 4 * (x - y) + 10;
        } else {
            d = d + 4 * x + 6;
        }
        plot_circle_octants_c(cx, cy, x, y, plot, user_data);
    }
}
