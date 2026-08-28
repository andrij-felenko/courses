class BresenhamCircle {
public:
    template <typename Callback>
    requires std::invocable<Callback, int32_t, int32_t>
    static void draw_circle(Point2D center, int32_t radius, Callback&& plot) {
        int32_t x = 0;
        int32_t y = radius;
        int32_t d = 3 - 2 * radius;
        
        auto plot_symmetric = [&](int32_t px, int32_t py) {
            plot(center.x + px, center.y + py);
            plot(center.x - px, center.y + py);
            plot(center.x + px, center.y - py);
            plot(center.x - px, center.y - py);
            plot(center.x + py, center.y + px);
            plot(center.x - py, center.y + px);
            plot(center.x + py, center.y - px);
            plot(center.x - py, center.y - px);
        };
        
        plot_symmetric(x, y);
        
        while (y >= x) {
            ++x;
            if (d > 0) {
                --y;
                d += 4 * (x - y) + 10;
            } else {
                d += 4 * x + 6;
            }
            plot_symmetric(x, y);
        }
    }
    
    [[nodiscard]] static std::vector<Point2D> rasterize_circle(Point2D center, int32_t radius) {
        std::vector<Point2D> pixels;
        draw_circle(center, radius, [&pixels](int32_t x, int32_t y) {
            pixels.push_back({x, y});
        });
        return pixels;
    }
};
