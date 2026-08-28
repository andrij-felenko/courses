void plot_ellipse_quadrants_c(int32_t cx, int32_t cy, int32_t x, int32_t y, PixelCallbackC plot, void* user_data) {
    plot(cx + x, cy + y, user_data);
    plot(cx - x, cy + y, user_data);
    plot(cx + x, cy - y, user_data);
    plot(cx - x, cy - y, user_data);
}

void bresenham_draw_ellipse_c(int32_t cx, int32_t cy, int32_t rx, int32_t ry, PixelCallbackC plot, void* user_data) {
    int64_t rx2 = (int64_t)rx * rx;
    int64_t ry2 = (int64_t)ry * ry;
    int64_t two_rx2 = 2 * rx2;
    int64_t two_ry2 = 2 * ry2;
    
    int32_t x = 0;
    int32_t y = ry;
    int64_t px = 0;
    int64_t py = two_rx2 * y;
    
    // Область 1
    int64_t d1 = ry2 - (rx2 * ry) + (rx2 / 4);
    plot_ellipse_quadrants_c(cx, cy, x, y, plot, user_data);
    
    while (px < py) {
        x++;
        px += two_ry2;
        if (d1 < 0) {
            d1 += ry2 + px;
        } else {
            y--;
            py -= two_rx2;
            d1 += ry2 + px - py;
        }
        plot_ellipse_quadrants_c(cx, cy, x, y, plot, user_data);
    }
    
    // Область 2
    int64_t d2 = ry2 * (x + 1) * (x + 1) + rx2 * (y - 1) * (y - 1) - rx2 * ry2;
    while (y > 0) {
        y--;
        py -= two_rx2;
        if (d2 > 0) {
            d2 += rx2 - py;
        } else {
            x++;
            px += two_ry2;
            d2 += rx2 - py + px;
        }
        plot_ellipse_quadrants_c(cx, cy, x, y, plot, user_data);
    }
}
