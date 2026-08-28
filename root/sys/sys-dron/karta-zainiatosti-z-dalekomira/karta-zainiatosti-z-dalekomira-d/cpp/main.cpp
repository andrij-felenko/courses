#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

class LocalOccupancyGrid {
public:
    static constexpr size_t SizeX = 100;
    static constexpr size_t SizeY = 100;
    static constexpr float Resolution = 0.1f; // 10 см на воксель

    static constexpr int16_t LFree = -62;
    static constexpr int16_t LOcc = 173;
    static constexpr int16_t LMin = -400;
    static constexpr int16_t LMax = 400;
    static constexpr int16_t LOccThreshold = 100;

    enum class Tactic {
        Proceed,
        Brake,
        BypassLeft,
        BypassRight,
        Climb
    };

    struct Point2D {
        float x;
        float y;
    };

    struct GridCoord {
        int x;
        int y;
    };

    struct Decision {
        Tactic tactic;
        float command_heading_rad;
    };

    LocalOccupancyGrid(Point2D initial_origin) noexcept : origin_(initial_origin) {
        cells_.fill(0);
    }

    void update_ray(Point2D sensor_pos, Point2D hit_pos, bool hit_detected) noexcept {
        auto c0 = world_to_grid(sensor_pos);
        auto c1 = world_to_grid(hit_pos);
        if (!c0 || !c1) return;

        int dx = std::abs(c1->x - c0->x);
        int dy = std::abs(c1->y - c0->y);
        int sx = (c0->x < c1->x) ? 1 : -1;
        int sy = (c0->y < c1->y) ? 1 : -1;
        int err = dx - dy;

        int cx = c0->x;
        int cy = c0->y;

        while (cx != c1->x || cy != c1->y) {
            apply_log_odds(cx, cy, LFree);
            int e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                cx += sx;
            }
            if (e2 < dx) {
                err += dx;
                cy += sy;
            }
        }

        if (hit_detected) {
            apply_log_odds(c1->x, c1->y, LOcc);
        }
    }

    [[nodiscard]] Decision evaluate_reaction(float current_speed, float max_deceleration) const noexcept {
        const int center_x = SizeX / 2;
        const int center_y = SizeY / 2;

        const float stop_distance = (current_speed * current_speed) / (2.0f * max_deceleration) 
                                  + current_speed * 0.15f + 0.8f;
        const int scan_depth = static_cast<int>(stop_distance / Resolution);

        int obstacle_dist = 0;
        for (int step = 1; step <= scan_depth && (center_x + step) < static_cast<int>(SizeX); ++step) {
            if (at(center_x + step, center_y) >= LOccThreshold) {
                obstacle_dist = step;
                break;
            }
        }

        if (obstacle_dist == 0) {
            return {Tactic::Proceed, 0.0f};
        }

        if (obstacle_dist <= static_cast<int>(1.2f / Resolution)) {
            return {Tactic::Brake, 0.0f};
        }

        int free_left_count = 0;
        int free_right_count = 0;
        for (int s = 1; s <= scan_depth; ++s) {
            if (center_y - s >= 0 && at(center_x + s, center_y - s) < LOccThreshold) {
                free_left_count++;
            }
            if (center_y + s < static_cast<int>(SizeY) && at(center_x + s, center_y + s) < LOccThreshold) {
                free_right_count++;
            }
        }

        if (free_left_count > free_right_count && free_left_count > 5) {
            return {Tactic::BypassLeft, -0.5235f};
        }
        if (free_right_count >= free_left_count && free_right_count > 5) {
            return {Tactic::BypassRight, 0.5235f};
        }

        return {Tactic::Climb, 0.0f};
    }

private:
    [[nodiscard]] std::optional<GridCoord> world_to_grid(Point2D pt) const noexcept {
        float lx = pt.x - (origin_.x - (SizeX * Resolution * 0.5f));
        float ly = pt.y - (origin_.y - (SizeY * Resolution * 0.5f));
        int gx = static_cast<int>(lx / Resolution);
        int gy = static_cast<int>(ly / Resolution);

        if (gx < 0 || gx >= static_cast<int>(SizeX) || gy < 0 || gy >= static_cast<int>(SizeY)) {
            return std::nullopt;
        }
        return GridCoord{gx, gy};
    }

    void apply_log_odds(int gx, int gy, int16_t delta) noexcept {
        auto idx = static_cast<size_t>(gy * SizeX + gx);
        int32_t val = cells_[idx] + delta;
        cells_[idx] = static_cast<int16_t>(std::clamp<int32_t>(val, LMin, LMax));
    }

    [[nodiscard]] int16_t at(int gx, int gy) const noexcept {
        return cells_[static_cast<size_t>(gy * SizeX + gx)];
    }

    Point2D origin_;
    std::array<int16_t, SizeX * SizeY> cells_;
};
