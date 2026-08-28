#include <cstdint>
#include <cmath>
#include <limits>
#include <algorithm>

namespace drone::navigation {

enum class CellCost : uint8_t {
    FreeSpace         = 0,
    InscribedObstacle = 253,
    LethalObstacle    = 254,
    NoInformation     = 255
};

struct CostmapConfig {
    float resolution{0.1f};          // Розмір клітинки в метрах
    float inscribed_radius{0.45f};   // Вписаний радіус дрона (м)
    float inflation_radius{1.5f};    // Зовнішній радіус інфляції (м)
    float cost_scaling_factor{3.0f}; // Коефіцієнт експоненційного спаду
    float cost_weight{4.0f};         // Вага штрафу вартості
    float turn_penalty_weight{0.8f}; // Вага штрафу за поворот
};

struct GridPoint {
    int x{0};
    int y{0};

    [[nodiscard]] constexpr bool operator==(const GridPoint& other) const noexcept {
        return x == other.x && y == other.y;
    }
};

class CostEvaluator {
public:
    explicit CostEvaluator(CostmapConfig config) noexcept : cfg_(config) {}

    [[nodiscard]] uint8_t computeInflationCost(float dist_to_obstacle) const noexcept {
        if (dist_to_obstacle <= cfg_.inscribed_radius) {
            return static_cast<uint8_t>(CellCost::InscribedObstacle);
        }
        if (dist_to_obstacle >= cfg_.inflation_radius) {
            return static_cast<uint8_t>(CellCost::FreeSpace);
        }

        const float delta_d = dist_to_obstacle - cfg_.inscribed_radius;
        const float factor = std::exp(-cfg_.cost_scaling_factor * delta_d);
        const float cost = factor * (static_cast<float>(CellCost::InscribedObstacle) - 1.0f);

        return (cost < 1.0f) ? static_cast<uint8_t>(CellCost::FreeSpace) 
                             : static_cast<uint8_t>(cost);
    }

    [[nodiscard]] float computeStepCost(GridPoint from,
                                        GridPoint to,
                                        GridPoint prev,
                                        uint8_t cell_cost) const noexcept {
        if (cell_cost >= static_cast<uint8_t>(CellCost::InscribedObstacle)) {
            return std::numeric_limits<float>::infinity();
        }

        const int dx = to.x - from.x;
        const int dy = to.y - from.y;
        const float step_dist = (dx != 0 && dy != 0) 
            ? (1.41421356f * cfg_.resolution) 
            : (1.0f * cfg_.resolution);

        const float cost_factor = 1.0f + cfg_.cost_weight * (static_cast<float>(cell_cost) / 254.0f);
        const float traversal_cost = step_dist * cost_factor;

        float turn_penalty = 0.0f;
        if (!(prev == from)) {
            const int dir1_x = from.x - prev.x;
            const int dir1_y = from.y - prev.y;
            const float dot = static_cast<float>(dir1_x * dx + dir1_y * dy);
            const float len1 = std::hypot(static_cast<float>(dir1_x), static_cast<float>(dir1_y));
            const float len2 = std::hypot(static_cast<float>(dx), static_cast<float>(dy));

            if (len1 > 0.0f && len2 > 0.0f) {
                const float cos_theta = std::clamp(dot / (len1 * len2), -1.0f, 1.0f);
                turn_penalty = cfg_.turn_penalty_weight * (1.0f - cos_theta);
            }
        }

        return traversal_cost + turn_penalty;
    }

private:
    CostmapConfig cfg_;
};

} // namespace drone::navigation
