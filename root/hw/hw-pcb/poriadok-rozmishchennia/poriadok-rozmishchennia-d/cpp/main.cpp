#include <iostream>
#include <vector>
#include <cmath>
#include <string_view>
#include <span>
#include <expected>

enum class ComponentKind {
    FixedMechanical,
    ProcessorCore,
    PowerHot,
    AnalogSensitive,
    DecouplingCap
};

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr double manhattan_distance_to(const Point2D& other) const noexcept {
        return std::abs(x - other.x) + std::abs(y - other.y);
    }

    [[nodiscard]] double euclidean_distance_to(const Point2D& other) const noexcept {
        return std::hypot(x - other.x, y - other.y);
    }
};

struct Component {
    int id{0};
    ComponentKind kind{ComponentKind::FixedMechanical};
    Point2D position;
    double width{0.0};
    double height{0.0};
    int assigned_to_ic{-1};
};

struct NetConnection {
    size_t comp_a_index{0};
    size_t comp_b_index{0};
    double weight{1.0};
};

enum class VerificationError {
    ThermalViolation,
    DecouplingViolation,
    BoundaryOverflow
};

class FloorplanVerifier {
public:
    FloorplanVerifier(double board_w, double board_h)
        : m_board_width(board_w), m_board_height(board_h) {}

    void add_component(Component comp) {
        m_components.push_back(comp);
    }

    void add_net(NetConnection net) {
        m_nets.push_back(net);
    }

    [[nodiscard]] double calculate_total_manhattan_wirelength() const noexcept {
        double total = 0.0;
        for (const auto& net : m_nets) {
            if (net.comp_a_index < m_components.size() && net.comp_b_index < m_components.size()) {
                const auto& a = m_components[net.comp_a_index];
                const auto& b = m_components[net.comp_b_index];
                total += a.position.manhattan_distance_to(b.position) * net.weight;
            }
        }
        return total;
    }

    [[nodiscard]] std::vector<std::string> verify_design_rules(double min_thermal_dist, double max_decoupling_dist) const {
        std::vector<std::string> violations;

        for (size_t i = 0; i < m_components.size(); ++i) {
            const auto& comp_i = m_components[i];

            /* Перевірка меж плати */
            if (comp_i.position.x < 0.0 || comp_i.position.x > m_board_width ||
                comp_i.position.y < 0.0 || comp_i.position.y > m_board_height) {
                violations.push_back("Компонент #" + std::to_string(comp_i.id) + " виходить за межі плати");
            }

            /* Теплова ізоляція: гарячі джерела проти чутливих сенсорів */
            if (comp_i.kind == ComponentKind::PowerHot) {
                for (size_t j = 0; j < m_components.size(); ++j) {
                    const auto& comp_j = m_components[j];
                    if (comp_j.kind == ComponentKind::AnalogSensitive) {
                        double dist = comp_i.position.euclidean_distance_to(comp_j.position);
                        if (dist < min_thermal_dist) {
                            violations.push_back("Тепловий конфлікт: Вузол #" + std::to_string(comp_i.id) +
                                                 " на відстані " + std::to_string(dist) + " мм від сенсора #" +
                                                 std::to_string(comp_j.id) + " (мінімум " + std::to_string(min_thermal_dist) + " мм)");
                        }
                    }
                }
            }

            /* Близькість блокувальних конденсаторів до живлених IC */
            if (comp_i.kind == ComponentKind::DecouplingCap && comp_i.assigned_to_ic >= 0) {
                auto it = std::find_if(m_components.begin(), m_components.end(),
                                       [id = comp_i.assigned_to_ic](const Component& c) { return c.id == id; });
                if (it != m_components.end()) {
                    double dist = comp_i.position.euclidean_distance_to(it->position);
                    if (dist > max_decoupling_dist) {
                        violations.push_back("Порушення розв'язки: Конденсатор #" + std::to_string(comp_i.id) +
                                             " на відстані " + std::to_string(dist) + " мм від IC #" +
                                             std::to_string(it->id) + " (максимум " + std::to_string(max_decoupling_dist) + " мм)");
                    }
                }
            }
        }

        return violations;
    }

private:
    double m_board_width{100.0};
    double m_board_height{80.0};
    std::vector<Component> m_components;
    std::vector<NetConnection> m_nets;
};
