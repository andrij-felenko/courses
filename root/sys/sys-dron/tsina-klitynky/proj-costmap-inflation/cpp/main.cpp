#include <iostream>
#include <vector>
#include <queue>
#include <cmath>
#include <cstdint>
#include <limits>
#include <algorithm>
#include <span>
#include <optional>

namespace drone::costmap {

enum class CellCost : uint8_t {
    FreeSpace         = 0,
    InscribedObstacle = 253,
    LethalObstacle    = 254,
    NoInformation     = 255
};

struct CostmapConfig {
    uint32_t width{40};
    uint32_t height{40};
    float resolution{0.5f};          // метрів на клітинку
    float origin_x{0.0f};
    float origin_y{0.0f};
    float inscribed_radius{0.6f};    // вписаний радіус (м)
    float inflation_radius{2.0f};    // радіус інфляції (м)
    float cost_scaling_factor{2.5f}; // швидкість експоненційного спаду
    float cost_weight{4.0f};         // штраф за вартість клітинки
    float turn_penalty_weight{0.5f}; // штраф за зміну напрямку
};

struct GridPoint {
    int32_t x{0};
    int32_t y{0};

    [[nodiscard]] constexpr bool operator==(const GridPoint& other) const noexcept {
        return x == other.x && y == other.y;
    }
};

class LayeredCostmap2D {
public:
    explicit LayeredCostmap2D(CostmapConfig config)
        : cfg_(config),
          cost_grid_(config.width * config.height, static_cast<uint8_t>(CellCost::FreeSpace)),
          static_grid_(config.width * config.height, static_cast<uint8_t>(CellCost::FreeSpace)) {
        buildLookupTable();
    }

    void setObstacle(int32_t x, int32_t y) noexcept {
        if (isValid(x, y)) {
            static_grid_[toIndex(x, y)] = static_cast<uint8_t>(CellCost::LethalObstacle);
        }
    }

    [[nodiscard]] uint8_t getCost(int32_t x, int32_t y) const noexcept {
        if (!isValid(x, y)) return static_cast<uint8_t>(CellCost::NoInformation);
        return cost_grid_[toIndex(x, y)];
    }

    [[nodiscard]] const CostmapConfig& config() const noexcept { return cfg_; }

    void updateInflation() {
        const uint32_t w = cfg_.width;
        const uint32_t h = cfg_.height;
        const uint32_t total = w * h;

        cost_grid_ = static_grid_;

        struct InflationCell {
            int32_t x, y, src_x, src_y;
        };

        std::queue<InflationCell> q;
        std::vector<bool> visited(total, false);

        for (uint32_t y = 0; y < h; ++y) {
            for (uint32_t x = 0; x < w; ++x) {
                const uint32_t idx = y * w + x;
                if (static_grid_[idx] == static_cast<uint8_t>(CellCost::LethalObstacle)) {
                    q.push({static_cast<int32_t>(x), static_cast<int32_t>(y),
                            static_cast<int32_t>(x), static_cast<int32_t>(y)});
                    visited[idx] = true;
                }
            }
        }

        constexpr int32_t dx[8] = {-1, 1, 0, 0, -1, -1, 1, 1};
        constexpr int32_t dy[8] = {0, 0, -1, 1, -1, 1, -1, 1};

        while (!q.empty()) {
            const auto curr = q.front();
            q.pop();

            for (int i = 0; i < 8; ++i) {
                const int32_t nx = curr.x + dx[i];
                const int32_t ny = curr.y + dy[i];

                if (!isValid(nx, ny)) continue;
                const uint32_t n_idx = toIndex(nx, ny);
                if (visited[n_idx]) continue;

                const int32_t diff_x = nx - curr.src_x;
                const int32_t diff_y = ny - curr.src_y;
                const uint32_t dist_sq = static_cast<uint32_t>(diff_x * diff_x + diff_y * diff_y);

                if (dist_sq >= lut_.size()) continue;

                const uint8_t cost = lut_[dist_sq];
                if (cost > static_cast<uint8_t>(CellCost::FreeSpace)) {
                    cost_grid_[n_idx] = std::max(cost_grid_[n_idx], cost);
                    visited[n_idx] = true;
                    q.push({nx, ny, curr.src_x, curr.src_y});
                }
            }
        }
    }

    [[nodiscard]] bool isValid(int32_t x, int32_t y) const noexcept {
        return x >= 0 && x < static_cast<int32_t>(cfg_.width) &&
               y >= 0 && y < static_cast<int32_t>(cfg_.height);
    }

    [[nodiscard]] uint32_t toIndex(int32_t x, int32_t y) const noexcept {
        return static_cast<uint32_t>(y * cfg_.width + x);
    }

private:
    void buildLookupTable() {
        const auto cell_inf = static_cast<int32_t>(std::ceil(cfg_.inflation_radius / cfg_.resolution));
        const uint32_t max_dist_sq = static_cast<uint32_t>(cell_inf * cell_inf) + 1;
        lut_.resize(max_dist_sq);

        for (uint32_t d_sq = 0; d_sq < max_dist_sq; ++d_sq) {
            const float dist_m = std::sqrt(static_cast<float>(d_sq)) * cfg_.resolution;
            if (dist_m <= cfg_.inscribed_radius) {
                lut_[d_sq] = static_cast<uint8_t>(CellCost::InscribedObstacle);
            } else if (dist_m >= cfg_.inflation_radius) {
                lut_[d_sq] = static_cast<uint8_t>(CellCost::FreeSpace);
            } else {
                const float delta_d = dist_m - cfg_.inscribed_radius;
                const float factor = std::exp(-cfg_.cost_scaling_factor * delta_d);
                const float cost = factor * (static_cast<float>(CellCost::InscribedObstacle) - 1.0f);
                lut_[d_sq] = (cost < 1.0f) ? static_cast<uint8_t>(CellCost::FreeSpace)
                                           : static_cast<uint8_t>(cost);
            }
        }
    }

    CostmapConfig cfg_;
    std::vector<uint8_t> cost_grid_;
    std::vector<uint8_t> static_grid_;
    std::vector<uint8_t> lut_;
};

class CostmapAStarPlanner {
public:
    struct PlanNode {
        GridPoint pt;
        float g_cost{0.0f};
        float f_cost{0.0f};
        int32_t parent_idx{-1};

        [[nodiscard]] bool operator>(const PlanNode& other) const noexcept {
            return f_cost > other.f_cost;
        }
    };

    [[nodiscard]] static std::optional<std::vector<GridPoint>> plan(
        const LayeredCostmap2D& map,
        GridPoint start,
        GridPoint goal) {
        
        const auto& cfg = map.config();
        const uint32_t total = cfg.width * cfg.height;

        if (!map.isValid(start.x, start.y) || !map.isValid(goal.x, goal.y)) return std::nullopt;
        if (map.getCost(start.x, start.y) >= static_cast<uint8_t>(CellCost::InscribedObstacle)) return std::nullopt;
        if (map.getCost(goal.x, goal.y) >= static_cast<uint8_t>(CellCost::InscribedObstacle)) return std::nullopt;

        std::vector<float> g_score(total, std::numeric_limits<float>::infinity());
        std::vector<int32_t> parent_map(total, -1);
        std::vector<bool> closed(total, false);

        std::priority_queue<PlanNode, std::vector<PlanNode>, std::greater<>> pq;

        const uint32_t start_idx = map.toIndex(start.x, start.y);
        g_score[start_idx] = 0.0f;

        const float h_start = std::hypot(static_cast<float>(goal.x - start.x),
                                         static_cast<float>(goal.y - start.y)) * cfg.resolution;
        pq.push({start, 0.0f, h_start, -1});

        constexpr int32_t dx[8] = {-1, 1, 0, 0, -1, -1, 1, 1};
        constexpr int32_t dy[8] = {0, 0, -1, 1, -1, 1, -1, 1};
        constexpr float step_dist[8] = {1.0f, 1.0f, 1.0f, 1.0f, 1.41421356f, 1.41421356f, 1.41421356f, 1.41421356f};

        bool found = false;
        const uint32_t goal_idx = map.toIndex(goal.x, goal.y);

        while (!pq.empty()) {
            const auto curr = pq.top();
            pq.pop();

            const uint32_t curr_idx = map.toIndex(curr.pt.x, curr.pt.y);
            if (closed[curr_idx]) continue;
            closed[curr_idx] = true;

            if (curr.pt == goal) {
                found = true;
                break;
            }

            for (int i = 0; i < 8; ++i) {
                const int32_t nx = curr.pt.x + dx[i];
                const int32_t ny = curr.pt.y + dy[i];

                if (!map.isValid(nx, ny)) continue;
                const uint32_t n_idx = map.toIndex(nx, ny);
                if (closed[n_idx]) continue;

                const uint8_t cell_cost = map.getCost(nx, ny);
                if (cell_cost >= static_cast<uint8_t>(CellCost::InscribedObstacle)) continue;

                const float cost_factor = 1.0f + cfg.cost_weight * (static_cast<float>(cell_cost) / 254.0f);
                const float edge_cost = step_dist[i] * cfg.resolution * cost_factor;

                float turn_penalty = 0.0f;
                if (curr.parent_idx >= 0) {
                    const int32_t px = curr.parent_idx % static_cast<int32_t>(cfg.width);
                    const int32_t py = curr.parent_idx / static_cast<int32_t>(cfg.width);
                    const int32_t dir1_x = curr.pt.x - px;
                    const int32_t dir1_y = curr.pt.y - py;
                    const int32_t dir2_x = dx[i];
                    const int32_t dir2_y = dy[i];

                    const float dot = static_cast<float>(dir1_x * dir2_x + dir1_y * dir2_y);
                    const float len1 = std::hypot(static_cast<float>(dir1_x), static_cast<float>(dir1_y));
                    const float len2 = std::hypot(static_cast<float>(dir2_x), static_cast<float>(dir2_y));
                    if (len1 > 0.0f && len2 > 0.0f) {
                        const float cos_theta = std::clamp(dot / (len1 * len2), -1.0f, 1.0f);
                        turn_penalty = cfg.turn_penalty_weight * (1.0f - cos_theta);
                    }
                }

                const float tentative_g = curr.g_cost + edge_cost + turn_penalty;
                if (tentative_g < g_score[n_idx]) {
                    g_score[n_idx] = tentative_g;
                    parent_map[n_idx] = static_cast<int32_t>(curr_idx);

                    const float h = std::hypot(static_cast<float>(goal.x - nx),
                                               static_cast<float>(goal.y - ny)) * cfg.resolution;
                    pq.push({{nx, ny}, tentative_g, tentative_g + h, static_cast<int32_t>(curr_idx)});
                }
            }
        }

        if (!found) return std::nullopt;

        std::vector<GridPoint> path;
        int32_t curr = static_cast<int32_t>(goal_idx);
        const int32_t s_idx = static_cast<int32_t>(start_idx);

        while (curr >= 0) {
            path.push_back({curr % static_cast<int32_t>(cfg.width),
                            curr / static_cast<int32_t>(cfg.width)});
            if (curr == s_idx) break;
            curr = parent_map[curr];
        }

        std::reverse(path.begin(), path.end());
        return path;
    }
};

} // namespace drone::costmap

int main() {
    using namespace drone::costmap;

    CostmapConfig cfg{
        .width = 40,
        .height = 40,
        .resolution = 0.5f,
        .origin_x = 0.0f,
        .origin_y = 0.0f,
        .inscribed_radius = 0.6f,
        .inflation_radius = 2.0f,
        .cost_scaling_factor = 2.5f,
        .cost_weight = 4.0f,
        .turn_penalty_weight = 0.5f
    };

    LayeredCostmap2D map(cfg);

    // Створення L-подібної перешкоди
    for (int y = 10; y <= 25; ++y) map.setObstacle(15, y);
    for (int x = 15; x <= 25; ++x) map.setObstacle(x, 25);

    map.updateInflation();

    const auto path = CostmapAStarPlanner::plan(map, {5, 5}, {30, 30});

    std::cout << "Результат планування C++:\n";
    if (path.has_value()) {
        std::cout << "Шлях знайдено! Кількість точок: " << path->size() << "\n";
        std::cout << "Старт: (" << path->front().x << ", " << path->front().y << ") -> "
                  << "Фініш: (" << path->back().x << ", " << path->back().y << ")\n";
    } else {
        std::cout << "Шлях заблоковано!\n";
    }

    return 0;
}
