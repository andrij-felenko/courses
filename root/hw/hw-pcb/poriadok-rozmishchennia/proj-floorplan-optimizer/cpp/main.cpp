#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <algorithm>
#include <span>
#include <memory>
#include <optional>
#include <array>

enum class CompType {
    FixedConnector,
    ProcessorCore,
    PowerSupply,
    SensitiveAnalog,
    PassiveDecoupling
};

struct Vector2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& o) const noexcept { return {x + o.x, y + o.y}; }
    [[nodiscard]] constexpr Vector2D operator-(const Vector2D& o) const noexcept { return {x - o.x, y - o.y}; }
    [[nodiscard]] constexpr Vector2D operator*(double s) const noexcept { return {x * s, y * s}; }
    constexpr Vector2D& operator+=(const Vector2D& o) noexcept { x += o.x; y += o.y; return *this; }
    constexpr Vector2D& operator-=(const Vector2D& o) noexcept { x -= o.x; y -= o.y; return *this; }

    [[nodiscard]] double length_sq() const noexcept { return x * x + y * y; }
    [[nodiscard]] double length() const noexcept { return std::hypot(x, y); }
};

struct Component {
    int id{0};
    std::string name;
    CompType type{CompType::FixedConnector};
    Vector2D pos;
    Vector2D vel;
    double width{0.0};
    double height{0.0};
    bool is_fixed{false};
    double heat_power{0.0};
    double temp_sens{0.0};
};

struct Net {
    int id{0};
    std::string name;
    std::vector<size_t> pin_comp_indices;
    double weight{1.0};
};

class PlacementOptimizer {
public:
    static constexpr size_t GridDim = 16;

    PlacementOptimizer(double board_width, double board_height)
        : m_board_w(board_width), m_board_h(board_height) {
        for (auto& row : m_congestion) row.fill(0.0);
    }

    size_t add_component(std::string_view name, CompType type, Vector2D pos,
                          double w, double h, bool is_fixed = false,
                          double heat = 0.0, double sens = 0.0) {
        size_t idx = m_components.size();
        m_components.push_back(Component{
            .id = static_cast<int>(idx),
            .name = std::string(name),
            .type = type,
            .pos = pos,
            .vel = {0.0, 0.0},
            .width = w,
            .height = h,
            .is_fixed = is_fixed,
            .heat_power = heat,
            .temp_sens = sens
        });
        return idx;
    }

    size_t add_net(std::string_view name, double weight = 1.0) {
        size_t idx = m_nets.size();
        m_nets.push_back(Net{
            .id = static_cast<int>(idx),
            .name = std::string(name),
            .pin_comp_indices = {},
            .weight = weight
        });
        return idx;
    }

    void connect_net(size_t net_idx, size_t comp_idx) {
        if (net_idx < m_nets.size() && comp_idx < m_components.size()) {
            m_nets[net_idx].pin_comp_indices.push_back(comp_idx);
        }
    }

    [[nodiscard]] double calculate_hpwl() const noexcept {
        double total = 0.0;
        for (const auto& net : m_nets) {
            if (net.pin_comp_indices.size() < 2) continue;

            double min_x = 1e9, max_x = -1e9;
            double min_y = 1e9, max_y = -1e9;

            for (size_t idx : net.pin_comp_indices) {
                const auto& c = m_components[idx];
                min_x = std::min(min_x, c.pos.x);
                max_x = std::max(max_x, c.pos.x);
                min_y = std::min(min_y, c.pos.y);
                max_y = std::max(max_y, c.pos.y);
            }

            double q = (net.pin_comp_indices.size() <= 3) ? 1.0 : 1.18;
            total += ((max_x - min_x) + (max_y - min_y)) * net.weight * q;
        }
        return total;
    }

    void compute_routing_congestion() {
        for (auto& row : m_congestion) row.fill(0.0);
        double cell_w = m_board_w / GridDim;
        double cell_h = m_board_h / GridDim;

        for (const auto& net : m_nets) {
            if (net.pin_comp_indices.size() < 2) continue;

            double min_x = 1e9, max_x = -1e9, min_y = 1e9, max_y = -1e9;
            for (size_t idx : net.pin_comp_indices) {
                const auto& c = m_components[idx];
                min_x = std::min(min_x, c.pos.x);
                max_x = std::max(max_x, c.pos.x);
                min_y = std::min(min_y, c.pos.y);
                max_y = std::max(max_y, c.pos.y);
            }

            size_t gx0 = std::clamp(static_cast<size_t>(min_x / cell_w), size_t{0}, GridDim - 1);
            size_t gx1 = std::clamp(static_cast<size_t>(max_x / cell_w), size_t{0}, GridDim - 1);
            size_t gy0 = std::clamp(static_cast<size_t>(min_y / cell_h), size_t{0}, GridDim - 1);
            size_t gy1 = std::clamp(static_cast<size_t>(max_y / cell_h), size_t{0}, GridDim - 1);

            double demand = net.weight / static_cast<double>((gx1 - gx0 + 1) * (gy1 - gy0 + 1));
            for (size_t gy = gy0; gy <= gy1; ++gy) {
                for (size_t gx = gx0; gx <= gx1; ++gx) {
                    m_congestion[gy][gx] += demand;
                }
            }
        }
    }

    void run_optimization(size_t max_epochs = 400) {
        double temp = 6.0;
        constexpr double decay = 0.988;
        constexpr double k_spring = 1.4;
        constexpr double k_repulse = 50.0;
        constexpr double k_thermal = 180.0;
        constexpr double damping = 0.22;

        std::vector<Vector2D> forces(m_components.size());

        for (size_t epoch = 0; epoch < max_epochs; ++epoch) {
            std::fill(forces.begin(), forces.end(), Vector2D{0.0, 0.0});

            /* 1. Розрахунок сил пружин зв'язків */
            for (const auto& net : m_nets) {
                const size_t count = net.pin_comp_indices.size();
                if (count < 2) continue;
                const double scale = 2.0 / static_cast<double>(count);

                for (size_t i = 0; i < count; ++i) {
                    for (size_t j = i + 1; j < count; ++j) {
                        size_t a_idx = net.pin_comp_indices[i];
                        size_t b_idx = net.pin_comp_indices[j];

                        Vector2D delta = m_components[b_idx].pos - m_components[a_idx].pos;
                        Vector2D f = delta * (k_spring * net.weight * scale);

                        forces[a_idx] += f;
                        forces[b_idx] -= f;
                    }
                }
            }

            /* 2. Сили відштовхування перекриттів і теплової сегрегації */
            for (size_t i = 0; i < m_components.size(); ++i) {
                for (size_t j = i + 1; j < m_components.size(); ++j) {
                    auto& comp_a = m_components[i];
                    auto& comp_b = m_components[j];

                    Vector2D delta = comp_b.pos - comp_a.pos;
                    double dist_sq = delta.length_sq();
                    double dist = std::sqrt(dist_sq) + 0.001;

                    double req_x = (comp_a.width + comp_b.width) * 0.5 + 1.2;
                    double req_y = (comp_a.height + comp_b.height) * 0.5 + 1.2;
                    double abs_dx = std::abs(delta.x);
                    double abs_dy = std::abs(delta.y);

                    if (abs_dx < req_x && abs_dy < req_y) {
                        double over_x = req_x - abs_dx;
                        double over_y = req_y - abs_dy;
                        Vector2D rep_f{
                            (delta.x > 0 ? -1.0 : 1.0) * k_repulse * over_x,
                            (delta.y > 0 ? -1.0 : 1.0) * k_repulse * over_y
                        };
                        forces[i] += rep_f;
                        forces[j] -= rep_f;
                    }

                    if ((comp_a.heat_power > 0.0 && comp_b.temp_sens > 0.0) ||
                        (comp_b.heat_power > 0.0 && comp_a.temp_sens > 0.0)) {
                        double p = std::max(comp_a.heat_power, comp_b.heat_power);
                        double s = std::max(comp_a.temp_sens, comp_b.temp_sens);
                        double f_val = (k_thermal * p * s) / (dist_sq + 120.0);
                        Vector2D th_f = (delta * (1.0 / dist)) * f_val;

                        forces[i] -= th_f;
                        forces[j] -= th_f;
                    }
                }
            }

            /* 3. Оновлення координат із обмеженням кроку */
            double max_move = 0.0;
            for (size_t i = 0; i < m_components.size(); ++i) {
                auto& c = m_components[i];
                if (c.is_fixed) continue;

                c.vel = c.vel * (1.0 - damping) + forces[i] * 0.01;
                double step_len = c.vel.length();

                Vector2D step = c.vel;
                if (step_len > temp) {
                    step = (c.vel * (1.0 / step_len)) * temp;
                }

                c.pos += step;

                double pad_x = c.width * 0.5 + 2.0;
                double pad_y = c.height * 0.5 + 2.0;
                c.pos.x = std::clamp(c.pos.x, pad_x, m_board_w - pad_x);
                c.pos.y = std::clamp(c.pos.y, pad_y, m_board_h - pad_y);

                max_move = std::max(max_move, step.length());
            }

            temp *= decay;
            if (temp < 0.04 && max_move < 0.005) break;
        }

        compute_routing_congestion();
    }

    [[nodiscard]] std::span<const Component> components() const noexcept { return m_components; }
    [[nodiscard]] const auto& congestion_map() const noexcept { return m_congestion; }

private:
    double m_board_w{120.0};
    double m_board_h{90.0};
    std::vector<Component> m_components;
    std::vector<Net> m_nets;
    std::array<std::array<double, GridDim>, GridDim> m_congestion;
};
