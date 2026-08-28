class BresenhamEllipse {
public:
    template <typename Callback>
    requires std::invocable<Callback, int32_t, int32_t>
    static void draw_ellipse(Point2D center, int32_t rx, int32_t ry, Callback&& plot) {
        const int64_t rx2 = static_cast<int64_t>(rx) * rx;
        const int64_t ry2 = static_cast<int64_t>(ry) * ry;
        const int64_t two_rx2 = 2 * rx2;
        const int64_t two_ry2 = 2 * ry2;
        
        int32_t x = 0;
        int32_t y = ry;
        int64_t px = 0;
        int64_t py = two_rx2 * y;
        
        auto plot_4way = [&](int32_t ex, int32_t ey) {
            plot(center.x + ex, center.y + ey);
            plot(center.x - ex, center.y + ey);
            plot(center.x + ex, center.y - ey);
            plot(center.x - ex, center.y - ey);
        };
        
        // Область 1
        int64_t d1 = ry2 - (rx2 * ry) + (rx2 / 4);
        plot_4way(x, y);
        
        while (px < py) {
            ++x;
            px += two_ry2;
            if (d1 < 0) {
                d1 += ry2 + px;
            } else {
                --y;
                py -= two_rx2;
                d1 += ry2 + px - py;
            }
            plot_4way(x, y);
        }
        
        // Область 2
        int64_t d2 = ry2 * (x + 1) * (x + 1) + rx2 * (y - 1) * (y - 1) - rx2 * ry2;
        while (y > 0) {
            --y;
            py -= two_rx2;
            if (d2 > 0) {
                d2 += rx2 - py;
            } else {
                ++x;
                px += two_ry2;
                d2 += rx2 - py + px;
            }
            plot_4way(x, y);
        }
    }
};
