#include <iostream>
#include <vector>
#include <cmath>
#include <functional>
#include <algorithm>
#include <cstdint>

struct Point2D {
    int32_t x{0};
    int32_t y{0};
    
    constexpr bool operator==(const Point2D& other) const noexcept = default;
};

using PixelCallback = std::function<void(int32_t x, int32_t y)>;

class BresenhamRasterizer {
public:
    template <typename Callback>
    requires std::invocable<Callback, int32_t, int32_t>
    static void draw_line(Point2D p1, Point2D p2, Callback&& plot) {
        int32_t dx = std::abs(p2.x - p1.x);
        int32_t dy = std::abs(p2.y - p1.y);
        const int32_t sx = (p1.x < p2.x) ? 1 : -1;
        const int32_t sy = (p1.y < p2.y) ? 1 : -1;
        
        const bool is_steep = (dy > dx);
        if (is_steep) {
            std::swap(dx, dy);
        }
        
        int32_t err = 2 * dy - dx;
        int32_t x = p1.x;
        int32_t y = p1.y;
        
        for (int32_t i = 0; i <= dx; ++i) {
            plot(x, y);
            
            while (err >= 0) {
                if (is_steep) {
                    x += sx;
                } else {
                    y += sy;
                }
                err -= 2 * dx;
            }
            
            if (is_steep) {
                y += sy;
            } else {
                x += sx;
            }
            err += 2 * dy;
        }
    }
    
    [[nodiscard]] static std::vector<Point2D> rasterize_line(Point2D p1, Point2D p2) {
        std::vector<Point2D> pixels;
        pixels.reserve(static_cast<size_t>(std::max(std::abs(p2.x - p1.x), std::abs(p2.y - p1.y)) + 1));
        draw_line(p1, p2, [&pixels](int32_t x, int32_t y) {
            pixels.push_back({x, y});
        });
        return pixels;
    }
};
