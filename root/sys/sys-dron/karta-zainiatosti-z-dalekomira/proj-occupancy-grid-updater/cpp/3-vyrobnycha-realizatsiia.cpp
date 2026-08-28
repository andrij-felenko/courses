#include <array>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>
#include <vector>

namespace navigation {

inline constexpr size_t GridDim = 128;
inline constexpr size_t GridMask = GridDim - 1;
inline constexpr float GridResolution = 0.1f; // 10 см на комірку

inline constexpr int16_t LogOddsFree = -62;
inline constexpr int16_t LogOddsOcc = 173;
inline constexpr int16_t LogOddsMin = -400;
inline constexpr int16_t LogOddsMax = 400;
inline constexpr int16_t LogOddsOccThresh = 100;

inline constexpr size_t NumSectors = 72;
inline constexpr float SectorAngleDeg = 5.0f;

enum class AvoidanceAction : uint8_t {
    Proceed = 0,
    Brake,
    BypassLeft,
    BypassRight,
    Climb
};

struct AvoidanceOutput {
    AvoidanceAction action{AvoidanceAction::Proceed};
    float target_heading_rad{0.0f};
    float recommended_speed_mps{0.0f};
};

struct Vector2D {
    float x{0.0f};
    float y{0.0f};
};

struct GridIndex {
    int32_t x{0};
    int32_t y{0};
};

[[nodiscard]] constexpr float normalize_angle(float a) noexcept {
    while (a > std::numbers::pi_v<float>) a -= 2.0f * std::numbers::pi_v<float>;
    while (a < -std::numbers::pi_v<float>) a += 2.0f * std::numbers::pi_v<float>;
    return a;
}

class FastLocalOccupancyGrid {
public:
    explicit FastLocalOccupancyGrid(Vector2D initial_origin) noexcept
        : origin_(initial_origin) {
        log_odds_.fill(0);
        cost_layer_.fill(0);
    }

    void shift_origin(Vector2D new_origin) noexcept {
        float dx = new_origin.x - origin_.x;
        float dy = new_origin.y - origin_.y;

        auto shift_x = static_cast<int32_t>(dx / GridResolution);
        auto shift_y = static_cast<int32_t>(dy / GridResolution);

        if (shift_x == 0 && shift_y == 0) return;

        if (std::abs(shift_x) >= static_cast<int32_t>(GridDim) ||
            std::abs(shift_y) >= static_cast<int32_t>(GridDim)) {
            log_odds_.fill(0);
            cost_layer_.fill(0);
            origin_ = new_origin;
            offset_x_ = 0;
            offset_y_ = 0;
            return;
        }

        if (shift_x > 0) {
            for (int32_t x = 0; x < shift_x; ++x) {
                size_t col = (offset_x_ + x) & GridMask;
                for (size_t y = 0; y < GridDim; ++y) {
                    log_odds_[col * GridDim + y] = 0;
                    cost_layer_[col * GridDim + y] = 0;
                }
            }
        } else if (shift_x < 0) {
            for (int32_t x = shift_x; x < 0; ++x) {
                size_t col = (offset_x_ + GridDim + x) & GridMask;
                for (size_t y = 0; y < GridDim; ++y) {
                    log_odds_[col * GridDim + y] = 0;
                    cost_layer_[col * GridDim + y] = 0;
                }
            }
        }

        if (shift_y > 0) {
            for (int32_t y = 0; y < shift_y; ++y) {
                size_t row = (offset_y_ + y) & GridMask;
                for (size_t x = 0; x < GridDim; ++x) {
                    log_odds_[x * GridDim + row] = 0;
                    cost_layer_[x * GridDim + row] = 0;
                }
            }
        } else if (shift_y < 0) {
            for (int32_t y = shift_y; y < 0; ++y) {
                size_t row = (offset_y_ + GridDim + y) & GridMask;
                for (size_t x = 0; x < GridDim; ++x) {
                    log_odds_[x * GridDim + row] = 0;
                    cost_layer_[x * GridDim + row] = 0;
                }
            }
        }

        offset_x_ = (offset_x_ + shift_x) & GridMask;
        offset_y_ = (offset_y_ + shift_y) & GridMask;
        origin_.x += static_cast<float>(shift_x) * GridResolution;
        origin_.y += static_cast<float>(shift_y) * GridResolution;
    }

    void update_ray(Vector2D start, Vector2D end, bool hit) noexcept {
        auto idx0 = world_to_indices(start);
        auto idx1 = world_to_indices(end);
        if (!idx0 || !idx1) return;

        int32_t x0 = idx0->x;
        int32_t y0 = idx0->y;
        int32_t x1 = idx1->x;
        int32_t y1 = idx1->y;

        int32_t dx = std::abs(x1 - x0);
        int32_t dy = std::abs(y1 - y0);
        int32_t sx = (x0 < x1) ? 1 : -1;
        int32_t sy = (y0 < y1) ? 1 : -1;
        int32_t err = dx - dy;

        int32_t cx = x0;
        int32_t cy = y0;

        while (cx != x1 || cy != y1) {
            update_cell_log_odds(cx, cy, LogOddsFree);
            int32_t e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                cx = (cx + sx) & GridMask;
            }
            if (e2 < dx) {
                err += dx;
                cy = (cy + sy) & GridMask;
            }
        }

        if (hit) {
            update_cell_log_odds(x1, y1, LogOddsOcc);
        }
    }

    void inflate(float safety_radius_m) noexcept {
        auto rad_cells = static_cast<int32_t>(safety_radius_m / GridResolution);
        if (rad_cells <= 0) return;

        for (size_t x = 0; x < GridDim; ++x) {
            for (size_t y = 0; y < GridDim; ++y) {
                if (log_odds_[x * GridDim + y] >= LogOddsOccThresh) {
                    for (int32_t dx = -rad_cells; dx <= rad_cells; ++dx) {
                        for (int32_t dy = -rad_cells; dy <= rad_cells; ++dy) {
                            if (dx * dx + dy * dy <= rad_cells * rad_cells) {
                                size_t nx = (x + dx) & GridMask;
                                size_t ny = (y + dy) & GridMask;
                                cost_layer_[nx * GridDim + ny] = 255;
                            }
                        }
                    }
                }
            }
        }
    }

    [[nodiscard]] AvoidanceOutput evaluate_vfh(
        float current_speed_mps,
        float target_heading_rad,
        float current_heading_rad,
        float max_decel
    ) const noexcept {
        AvoidanceOutput out;
        out.action = AvoidanceAction::Proceed;
        out.target_heading_rad = target_heading_rad;
        out.recommended_speed_mps = current_speed_mps;

        float stop_dist = (current_speed_mps * current_speed_mps) / (2.0f * max_decel)
                        + current_speed_mps * 0.2f + 0.8f;
        auto scan_cells = static_cast<int32_t>(stop_dist / GridResolution);
        scan_cells = std::clamp<int32_t>(scan_cells, 2, GridDim / 2 - 2);

        std::array<float, NumSectors> polar_density{};
        polar_density.fill(0.0f);

        size_t center_x = (offset_x_ + GridDim / 2) & GridMask;
        size_t center_y = (offset_y_ + GridDim / 2) & GridMask;

        for (int32_t dx = -scan_cells; dx <= scan_cells; ++dx) {
            for (int32_t dy = -scan_cells; dy <= scan_cells; ++dy) {
                float dist_sq = static_cast<float>(dx * dx + dy * dy);
                if (dist_sq <= 1.0f || dist_sq > static_cast<float>(scan_cells * scan_cells)) continue;

                size_t cx = (center_x + dx) & GridMask;
                size_t cy = (center_y + dy) & GridMask;

                uint8_t cost = cost_layer_[cx * GridDim + cy];
                if (cost > 0) {
                    float dist = std::sqrt(dist_sq);
                    float angle = std::atan2(static_cast<float>(dy), static_cast<float>(dx));
                    float rel_angle = normalize_angle(angle - current_heading_rad);
                    float deg = rel_angle * (180.0f / std::numbers::pi_v<float>);
                    if (deg < 0.0f) deg += 360.0f;

                    size_t sector = static_cast<size_t>(deg / SectorAngleDeg) % NumSectors;
                    float weight = (static_cast<float>(cost) / 255.0f) *
                                   (static_cast<float>(scan_cells) - dist) / static_cast<float>(scan_cells);
                    polar_density[sector] += weight;
                }
            }
        }

        float front_threat = polar_density[0] + polar_density[1] + polar_density[NumSectors - 1];

        if (front_threat < 0.3f) {
            return out;
        }

        if (front_threat > 2.5f && current_speed_mps > 1.5f) {
            out.action = AvoidanceAction::Brake;
            out.recommended_speed_mps = 0.0f;
            return out;
        }

        float best_cost = 1e9f;
        std::optional<size_t> best_sector;
        float target_rel = normalize_angle(target_heading_rad - current_heading_rad);

        for (size_t s = 0; s < NumSectors; ++s) {
            if (polar_density[s] < 0.5f) {
                float s_rad = static_cast<float>(s) * SectorAngleDeg * (std::numbers::pi_v<float> / 180.0f);
                if (s_rad > std::numbers::pi_v<float>) s_rad -= 2.0f * std::numbers::pi_v<float>;

                float diff_target = std::abs(normalize_angle(s_rad - target_rel));
                float diff_current = std::abs(normalize_angle(s_rad));
                float cost = 2.0f * diff_target + 1.0f * diff_current + polar_density[s] * 3.0f;

                if (cost < best_cost) {
                    best_cost = cost;
                    best_sector = s;
                }
            }
        }

        if (best_sector) {
            float chosen_rel = static_cast<float>(*best_sector) * SectorAngleDeg * (std::numbers::pi_v<float> / 180.0f);
            if (chosen_rel > std::numbers::pi_v<float>) chosen_rel -= 2.0f * std::numbers::pi_v<float>;
            out.target_heading_rad = normalize_angle(current_heading_rad + chosen_rel);
            out.action = (chosen_rel < 0.0f) ? AvoidanceAction::BypassLeft : AvoidanceAction::BypassRight;
            out.recommended_speed_mps = current_speed_mps * 0.75f;
        } else {
            out.action = AvoidanceAction::Climb;
            out.recommended_speed_mps = current_speed_mps * 0.3f;
        }

        return out;
    }

private:
    [[nodiscard]] std::optional<GridIndex> world_to_indices(Vector2D w) const noexcept {
        float lx = w.x - (origin_.x - (static_cast<float>(GridDim) * GridResolution * 0.5f));
        float ly = w.y - (origin_.y - (static_cast<float>(GridDim) * GridResolution * 0.5f));

        auto cx = static_cast<int32_t>(lx / GridResolution);
        auto cy = static_cast<int32_t>(ly / GridResolution);

        if (cx < 0 || cx >= static_cast<int32_t>(GridDim) ||
            cy < 0 || cy >= static_cast<int32_t>(GridDim)) {
            return std::nullopt;
        }

        return GridIndex{
            static_cast<int32_t>((offset_x_ + cx) & static_cast<int32_t>(GridMask)),
            static_cast<int32_t>((offset_y_ + cy) & static_cast<int32_t>(GridMask))
        };
    }

    void update_cell_log_odds(int32_t ix, int32_t iy, int16_t delta) noexcept {
        size_t idx = static_cast<size_t>(ix * GridDim + iy);
        int32_t nv = log_odds_[idx] + delta;
        log_odds_[idx] = static_cast<int16_t>(std::clamp<int32_t>(nv, LogOddsMin, LogOddsMax));

        if (log_odds_[idx] >= LogOddsOccThresh) {
            cost_layer_[idx] = 255;
        } else if (log_odds_[idx] <= LogOddsFree) {
            cost_layer_[idx] = 0;
        }
    }

    Vector2D origin_{0.0f, 0.0f};
    int32_t offset_x_{0};
    int32_t offset_y_{0};
    std::array<int16_t, GridDim * GridDim> log_odds_{};
    std::array<uint8_t, GridDim * GridDim> cost_layer_{};
};

} // namespace navigation
