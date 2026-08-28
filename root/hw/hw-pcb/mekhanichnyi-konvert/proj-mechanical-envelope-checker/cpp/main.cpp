#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <iomanip>
#include <span>
#include <optional>

namespace mech {

enum class ComponentClass {
    Standard,
    Mlcc,          // Керамічні конденсатори: чутливі до механічного напруження
    Connector,     // Інтерфейсні роз'єми з вимогами до вильоту
    TallPassive    // Високі компоненти (дроселі, електроліти), що блокують інструмент
};

enum class ViolationType {
    ScrewHeadCollision,
    ToolClearanceBlocked,
    MlccStressZone,
    HeightExceeded,
    ConnectorOverhangMismatch
};

struct Vec2 {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vec2 operator-(const Vec2& other) const noexcept {
        return { x - other.x, y - other.y };
    }
};

struct Component {
    std::string refdes;
    ComponentClass comp_class{ComponentClass::Standard};
    Vec2 center;
    double width{0.0};       // мм (вісь X при куті 0)
    double length{0.0};      // мм (вісь Y при куті 0)
    double height{0.0};      // мм
    double rotation_deg{0.0};// градуси
    double overhang_req{0.0};// мм
};

struct MountingHole {
    std::string id;
    Vec2 center;
    double drill_dia{3.2};
    double screw_head_dia{6.0};
    double tool_clearance_dia{8.0};
    double mlcc_keepout_dia{10.0};
};

struct HeightZone {
    std::string name;
    double min_x{0.0};
    double min_y{0.0};
    double max_x{0.0};
    double max_y{0.0};
    double max_allowed_height{0.0};

    [[nodiscard]] bool contains(const Vec2& pt) const noexcept {
        return pt.x >= min_x && pt.x <= max_x && pt.y >= min_y && pt.y <= max_y;
    }
};

struct Violation {
    ViolationType type;
    std::string refdes;
    std::string context_id;
    double actual_value{0.0};
    double limit_value{0.0};
    Vec2 location;
};

class GeometryEngine {
public:
    [[nodiscard]] static constexpr double deg_to_rad(double deg) noexcept {
        return deg * (std::numbers::pi / 180.0);
    }

    [[nodiscard]] static bool check_obb_circle_intersect(
        const Component& comp,
        const Vec2& circle_center,
        double radius,
        double& out_dist) noexcept 
    {
        const double rad = deg_to_rad(-comp.rotation_deg);
        const double cos_a = std::cos(rad);
        const double sin_a = std::sin(rad);

        const Vec2 d = circle_center - comp.center;

        // Перехід у власну систему координат прямокутника
        const double local_x = d.x * cos_a - d.y * sin_a;
        const double local_y = d.x * sin_a + d.y * cos_a;

        const double half_w = comp.width * 0.5;
        const double half_l = comp.length * 0.5;

        const double nearest_x = std::clamp(local_x, -half_w, half_w);
        const double nearest_y = std::clamp(local_y, -half_l, half_l);

        const double delta_x = local_x - nearest_x;
        const double delta_y = local_y - nearest_y;

        const double dist_sq = delta_x * delta_x + delta_y * delta_y;
        out_dist = std::sqrt(dist_sq);

        return dist_sq < (radius * radius);
    }
};

class EnvelopeChecker {
public:
    explicit EnvelopeChecker(double board_w, double board_h)
        : board_width_{board_w}, board_height_{board_h} {}

    void add_component(Component comp) {
        components_.push_back(std::move(comp));
    }

    void add_hole(MountingHole hole) {
        holes_.push_back(std::move(hole));
    }

    void add_height_zone(HeightZone zone) {
        height_zones_.push_back(std::move(zone));
    }

    [[nodiscard]] std::span<const Violation> run_checks() {
        violations_.clear();

        for (const auto& comp : components_) {
            // 1. Валідація відносно кріпильних отворів
            for (const auto& hole : holes_) {
                double dist = 0.0;

                // Пряма колізія з головкою гвинта
                const double r_screw = hole.screw_head_dia * 0.5;
                if (GeometryEngine::check_obb_circle_intersect(comp, hole.center, r_screw, dist)) {
                    violations_.push_back({
                        ViolationType::ScrewHeadCollision, comp.refdes, hole.id, dist, r_screw, comp.center
                    });
                }

                // Блокування зони монтажного інструменту високими деталями
                const double r_tool = hole.tool_clearance_dia * 0.5;
                if (comp.height > 4.0 && GeometryEngine::check_obb_circle_intersect(comp, hole.center, r_tool, dist)) {
                    violations_.push_back({
                        ViolationType::ToolClearanceBlocked, comp.refdes, hole.id, comp.height, r_tool, comp.center
                    });
                }

                // Зона небезпечних деформацій для крихких MLCC
                if (comp.comp_class == ComponentClass::Mlcc) {
                    const double r_mlcc = hole.mlcc_keepout_dia * 0.5;
                    if (GeometryEngine::check_obb_circle_intersect(comp, hole.center, r_mlcc, dist)) {
                        violations_.push_back({
                            ViolationType::MlccStressZone, comp.refdes, hole.id, dist, r_mlcc, comp.center
                        });
                    }
                }
            }

            // 2. Валідація тривимірних зон обмеження висоти корпусу
            for (const auto& zone : height_zones_) {
                if (zone.contains(comp.center) && comp.height > zone.max_allowed_height) {
                    violations_.push_back({
                        ViolationType::HeightExceeded, comp.refdes, zone.name, comp.height, zone.max_allowed_height, comp.center
                    });
                }
            }

            // 3. Валідація вильоту інтерфейсних роз'ємів за контур плати
            if (comp.comp_class == ComponentClass::Connector && comp.overhang_req > 0.0) {
                const double actual_left_edge = comp.center.x - (comp.length * 0.5);
                const double actual_overhang = -actual_left_edge;
                if (std::abs(actual_overhang - comp.overhang_req) > 0.3) {
                    violations_.push_back({
                        ViolationType::ConnectorOverhangMismatch, comp.refdes, "LeftEdge", actual_overhang, comp.overhang_req, comp.center
                    });
                }
            }
        }

        return violations_;
    }

    void print_report() const {
        std::cout << "===============================================================\n"
                  << "ЗВІТ МЕХАНІЧНОГО КОНВЕРТА (C++20): Деталей: " << components_.size()
                  << ", Отворів: " << holes_.size() << "\n"
                  << "Знайдено дефектів: " << violations_.size() << "\n"
                  << "===============================================================\n";

        for (size_t idx = 0; const auto& v : violations_) {
            std::cout << "[" << std::setw(2) << std::setfill('0') << ++idx << "] ";
            switch (v.type) {
                case ViolationType::ScrewHeadCollision:
                    std::cout << "КОЛІЗІЯ З ГОЛОВКОЮ ГВИНТА: " << v.refdes << " перекриває "
                              << v.context_id << " (відстань " << std::fixed << std::setprecision(2)
                              << v.actual_value << " мм < R_screw " << v.limit_value << " мм)\n";
                    break;
                case ViolationType::ToolClearanceBlocked:
                    std::cout << "БЛОКУВАННЯ ІНСТРУМЕНТУ: Деталь " << v.refdes << " (висота "
                              << v.actual_value << " мм) блокує зону монтажу " << v.context_id
                              << " (R " << v.limit_value << " мм)\n";
                    break;
                case ViolationType::MlccStressZone:
                    std::cout << "НЕБЕЗПЕКА ЗЛАМУ MLCC: Конденсатор " << v.refdes << " у зоні деформацій "
                              << v.context_id << " (відстань " << v.actual_value << " мм < R_keepout "
                              << v.limit_value << " мм)\n";
                    break;
                case ViolationType::HeightExceeded:
                    std::cout << "ПЕРЕВИЩЕННЯ ВИСОТИ КОРПУСУ: " << v.refdes << " має висоту "
                              << v.actual_value << " мм > ліміту " << v.limit_value
                              << " мм у зоні " << v.context_id << "\n";
                    break;
                case ViolationType::ConnectorOverhangMismatch:
                    std::cout << "ПОХИБКА ВИЛЬОТУ РОЗ'ЄМУ: " << v.refdes << " виступає на "
                              << v.actual_value << " мм (вимога " << v.limit_value
                              << " мм) на " << v.context_id << "\n";
                    break;
            }
        }
        std::cout << "===============================================================\n";
    }

private:
    double board_width_{0.0};
    double board_height_{0.0};
    std::vector<Component> components_;
    std::vector<MountingHole> holes_;
    std::vector<HeightZone> height_zones_;
    std::vector<Violation> violations_;
};

} // namespace mech

int main() {
    mech::EnvelopeChecker checker(120.0, 70.0);

    // Додаємо 4 отвори M3
    checker.add_hole({ "H1_TopLeft",  { 6.0, 64.0 }, 3.2, 6.0, 8.0, 10.0 });
    checker.add_hole({ "H2_TopRight", { 114.0, 64.0 }, 3.2, 6.0, 8.0, 10.0 });
    checker.add_hole({ "H3_BotLeft",  { 6.0, 6.0 }, 3.2, 6.0, 8.0, 10.0 });
    checker.add_hole({ "H4_BotRight", { 114.0, 6.0 }, 3.2, 6.0, 8.0, 10.0 });

    // Зона обмеження висоти
    checker.add_height_zone({ "TopRib_Shield", 30.0, 50.0, 90.0, 70.0, 3.5 });

    // Тестові компоненти
    checker.add_component({ "C101", mech::ComponentClass::Mlcc, { 7.5, 61.5 }, 1.6, 0.8, 0.9, 45.0, 0.0 });
    checker.add_component({ "L201", mech::ComponentClass::TallPassive, { 9.0, 6.0 }, 6.0, 6.0, 5.5, 0.0, 0.0 });
    checker.add_component({ "J1_USB", mech::ComponentClass::Connector, { 4.0, 35.0 }, 8.9, 10.0, 3.2, 0.0, 1.4 });
    checker.add_component({ "Q301", mech::ComponentClass::Standard, { 50.0, 60.0 }, 6.5, 6.5, 4.2, 0.0, 0.0 });

    checker.run_checks();
    checker.print_report();

    return 0;
}
