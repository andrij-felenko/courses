#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <memory>
#include <optional>

namespace robotics::coverage {

constexpr double kEpsilon = 1e-6;

enum class EventType {
    In,
    Out,
    Split,
    Merge,
    Regular
};

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] double distance_to(const Point2D& other) const noexcept {
        return std::hypot(x - other.x, y - other.y);
    }
};

struct SweepEvent {
    Point2D pt;
    EventType type{EventType::Regular};
    std::size_t polygon_index{0};
    std::size_t vertex_index{0};

    bool operator<(const SweepEvent& other) const noexcept {
        if (std::abs(pt.x - other.pt.x) > kEpsilon) {
            return pt.x < other.pt.x;
        }
        return pt.y < other.pt.y;
    }
};

class BcdCell {
public:
    explicit BcdCell(std::size_t id, double x_min, double x_max) noexcept
        : id_(id), x_min_(x_min), x_max_(x_max) {}

    void generate_stripes(double top_y, double bot_y, double step_d) {
        waypoints_.clear();
        double cur_x = x_min_ + step_d * 0.5;
        bool moving_up = true;

        while (cur_x <= x_max_ + kEpsilon) {
            if (moving_up) {
                waypoints_.push_back({ cur_x, bot_y });
                waypoints_.push_back({ cur_x, top_y });
            } else {
                waypoints_.push_back({ cur_x, top_y });
                waypoints_.push_back({ cur_x, bot_y });
            }
            moving_up = !moving_up;
            cur_x += step_d;
        }
    }

    void add_neighbor(std::size_t neighbor_id) {
        if (std::find(neighbors_.begin(), neighbors_.end(), neighbor_id) == neighbors_.end()) {
            neighbors_.push_back(neighbor_id);
        }
    }

    [[nodiscard]] std::size_t id() const noexcept { return id_; }
    [[nodiscard]] const std::vector<Point2D>& waypoints() const noexcept { return waypoints_; }
    [[nodiscard]] const std::vector<std::size_t>& neighbors() const noexcept { return neighbors_; }
    [[nodiscard]] bool is_visited() const noexcept { return visited_; }
    void set_visited(bool state) noexcept { visited_ = state; }

private:
    std::size_t id_{0};
    double x_min_{0.0};
    double x_max_{0.0};
    std::vector<Point2D> waypoints_;
    std::vector<std::size_t> neighbors_;
    bool visited_{false};
};

class BcdPlanner {
public:
    void add_cell(double x_min, double x_max, double top_y, double bot_y, double step_d) {
        const std::size_t id = cells_.size();
        auto cell = std::make_unique<BcdCell>(id, x_min, x_max);
        cell->generate_stripes(top_y, bot_y, step_d);
        cells_.push_back(std::move(cell));
    }

    void connect_cells(std::size_t u, std::size_t v) {
        if (u < cells_.size() && v < cells_.size()) {
            cells_[u]->add_neighbor(v);
            cells_[v]->add_neighbor(u);
        }
    }

    [[nodiscard]] std::vector<Point2D> plan_coverage(std::size_t start_cell = 0) {
        std::vector<Point2D> global_path;
        for (auto& cell : cells_) {
            cell->set_visited(false);
        }
        if (start_cell < cells_.size()) {
            dfs_traverse(start_cell, global_path);
        }
        return global_path;
    }

    [[nodiscard]] std::size_t cell_count() const noexcept { return cells_.size(); }

private:
    void dfs_traverse(std::size_t current_id, std::vector<Point2D>& path) {
        auto& current_cell = *cells_[current_id];
        current_cell.set_visited(true);

        const auto& wps = current_cell.waypoints();
        path.insert(path.end(), wps.begin(), wps.end());

        for (std::size_t neighbor_id : current_cell.neighbors()) {
            if (!cells_[neighbor_id]->is_visited()) {
                dfs_traverse(neighbor_id, path);
            }
        }
    }

    std::vector<std::unique_ptr<BcdCell>> cells_;
};

} // namespace robotics::coverage

int main() {
    using namespace robotics::coverage;

    BcdPlanner planner;
    constexpr double kStepD = 5.0;

    // Створюємо комірки для демонстраційного полігону з перешкодою
    planner.add_cell(0.0, 35.0, 60.0, 0.0, kStepD);     // C0: ліва зона
    planner.add_cell(35.0, 65.0, 60.0, 45.0, kStepD);   // C1: верхній коридор
    planner.add_cell(35.0, 65.0, 15.0, 0.0, kStepD);    // C2: нижній коридор
    planner.add_cell(65.0, 100.0, 60.0, 0.0, kStepD);   // C3: права зона

    // Зв'язки між комірками
    planner.connect_cells(0, 1);
    planner.connect_cells(0, 2);
    planner.connect_cells(1, 3);
    planner.connect_cells(2, 3);

    const std::vector<Point2D> full_mission = planner.plan_coverage(0);

    std::cout << "C++ BCD Planner згенеровано " << planner.cell_count()
              << " комірок із сумарною довжиною місії " << full_mission.size()
              << " точок маршруту." << std::endl;

    return 0;
}
