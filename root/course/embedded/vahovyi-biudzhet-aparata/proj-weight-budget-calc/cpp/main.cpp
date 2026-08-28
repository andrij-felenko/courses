#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <numeric>
#include <cmath>
#include <iomanip>

enum class ComponentCategory : size_t {
    Payload = 0,
    Battery,
    Propulsion,
    Avionics,
    Airframe,
    Margin,
    Count
};

constexpr std::array<std::string_view, static_cast<size_t>(ComponentCategory::Count)> CategoryNames = {
    "Корисне навантаження",
    "Акумуляторна батарея",
    "Силова установка",
    "Бортова авіоніка",
    "Планер і кріплення",
    "Конструкторський резерв"
};

struct Vector3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct Component {
    std::string name;
    ComponentCategory category;
    float mass_g{0.0f};
    Vector3D position_mm;
    float power_w{0.0f};
};

struct BudgetAnalysis {
    float mtow_g{0.0f};
    std::array<float, static_cast<size_t>(ComponentCategory::Count)> category_mass_g{};
    std::array<float, static_cast<size_t>(ComponentCategory::Count)> category_fraction{};
    Vector3D cg_mm;
    float cg_offset_mm{0.0f};
    float twr{0.0f};
    float total_idle_power_w{0.0f};
    bool is_balanced{false};
    bool is_twr_sufficient{false};
    bool is_battery_fraction_ok{false};
};

class WeightBudgetCalculator {
public:
    WeightBudgetCalculator(int motor_count, float max_thrust_per_motor_g, Vector3D cot_position_mm = {})
        : motor_count_(motor_count),
          max_thrust_per_motor_g_(max_thrust_per_motor_g),
          cot_position_mm_(cot_position_mm) {}

    void add_component(std::string name, ComponentCategory cat, 
                       float mass_g, Vector3D pos, float power_w = 0.0f) {
        components_.push_back(Component{
            .name = std::move(name),
            .category = cat,
            .mass_g = mass_g,
            .position_mm = pos,
            .power_w = power_w
        });
    }

    [[nodiscard]] BudgetAnalysis calculate() const {
        BudgetAnalysis res{};

        float sum_mx = 0.0f;
        float sum_my = 0.0f;
        float sum_mz = 0.0f;

        for (const auto& item : components_) {
            res.mtow_g += item.mass_g;
            const auto cat_idx = static_cast<size_t>(item.category);
            res.category_mass_g[cat_idx] += item.mass_g;
            res.total_idle_power_w += item.power_w;

            sum_mx += item.mass_g * item.position_mm.x;
            sum_my += item.mass_g * item.position_mm.y;
            sum_mz += item.mass_g * item.position_mm.z;
        }

        if (res.mtow_g > 0.0f) {
            res.cg_mm = Vector3D{
                .x = sum_mx / res.mtow_g,
                .y = sum_my / res.mtow_g,
                .z = sum_mz / res.mtow_g
            };

            for (size_t c = 0; c < static_cast<size_t>(ComponentCategory::Count); ++c) {
                res.category_fraction[c] = (res.category_mass_g[c] / res.mtow_g) * 100.0f;
            }

            const float dx = res.cg_mm.x - cot_position_mm_.x;
            const float dy = res.cg_mm.y - cot_position_mm_.y;
            res.cg_offset_mm = std::sqrt(dx * dx + dy * dy);

            const float total_max_thrust = static_cast<float>(motor_count_) * max_thrust_per_motor_g_;
            res.twr = total_max_thrust / res.mtow_g;

            res.is_balanced = (res.cg_offset_mm <= 3.0f);
            res.is_twr_sufficient = (res.twr >= 1.8f);
            const size_t bat_idx = static_cast<size_t>(ComponentCategory::Battery);
            res.is_battery_fraction_ok = (res.category_fraction[bat_idx] <= 55.0f);
        }

        return res;
    }

    void print_report(const BudgetAnalysis& a) const {
        std::cout << "=================================================================\n";
        std::cout << "              ІНЖЕНЕРНИЙ ЗВІТ ВАГОВОГО БЮДЖЕТУ                   \n";
        std::cout << "=================================================================\n";
        std::cout << std::left << std::setw(30) << "Категорія" << " | "
                  << std::right << std::setw(10) << "Маса (г)" << " | "
                  << std::setw(14) << "Частка MTOW (%)" << "\n";
        std::cout << "-----------------------------------------------------------------\n";

        std::cout << std::fixed << std::setprecision(1);
        for (size_t c = 0; c < static_cast<size_t>(ComponentCategory::Count); ++c) {
            std::cout << std::left << std::setw(30) << CategoryNames[c] << " | "
                      << std::right << std::setw(10) << a.category_mass_g[c] << " | "
                      << std::setw(13) << a.category_fraction[c] << "%\n";
        }
        std::cout << "-----------------------------------------------------------------\n";
        std::cout << std::left << std::setw(30) << "ПОВНА ЗЛІТНА МАСА (MTOW)" << " | "
                  << std::right << std::setw(10) << a.mtow_g << " | "
                  << std::setw(13) << 100.0f << "%\n";
        std::cout << "=================================================================\n";

        std::cout << "Центр тяжіння (CG):      X = " << std::showpos << a.cg_mm.x 
                  << " мм, Y = " << a.cg_mm.y << " мм, Z = " << a.cg_mm.z << " мм\n" << std::noshowpos;
        std::cout << "Центр тяги (CoT):        X = " << std::showpos << cot_position_mm_.x 
                  << " мм, Y = " << cot_position_mm_.y << " мм\n" << std::noshowpos;
        std::cout << "Зсув CG відносно CoT:    Δ = " << std::setprecision(2) << a.cg_offset_mm 
                  << " мм [" << (a.is_balanced ? "OK: Збалансовано" : "УВАГА: Перекіс > 3 мм") << "]\n";

        std::cout << "Тягооснащеність (TWR):   " << a.twr << ":1 ["
                  << (a.is_twr_sufficient ? "OK: Запас тяги достатній" : "КРИТИЧНО: TWR < 1.8") << "]\n";
        const size_t bat_idx = static_cast<size_t>(ComponentCategory::Battery);
        std::cout << "Частка акумулятора:      " << std::setprecision(1) << a.category_fraction[bat_idx] 
                  << "% [" << (a.is_battery_fraction_ok ? "OK: Оптимальна" : "УВАГА: Ризик перевантаження") << "]\n";
        std::cout << "Споживання електроніки:  " << a.total_idle_power_w 
                  << " Вт (постійне бортове навантаження)\n";
        std::cout << "=================================================================\n";
    }

private:
    int motor_count_{4};
    float max_thrust_per_motor_g_{0.0f};
    Vector3D cot_position_mm_{};
    std::vector<Component> components_;
};

int main() {
    // Конфігурація розвідувального 7-дюймового квадрокоптера (X4)
    WeightBudgetCalculator uav(4, 1850.0f, Vector3D{0.0f, 0.0f, 0.0f});

    uav.add_component("Термальна камера + Gimbal", ComponentCategory::Payload,    380.0f, Vector3D{ 45.0f, 0.0f, -20.0f}, 12.0f);
    uav.add_component("Бортовий комп'ютер SBC",   ComponentCategory::Payload,     85.0f, Vector3D{ 10.0f, 0.0f,  10.0f}, 15.0f);
    uav.add_component("Батарея Li-ion 6S2P 21700",ComponentCategory::Battery,    860.0f, Vector3D{-22.0f, 0.0f,  25.0f},  0.0f);
    uav.add_component("Мотори 2806.5 (4 шт)",     ComponentCategory::Propulsion, 192.0f, Vector3D{  0.0f, 0.0f,   0.0f},  0.0f);
    uav.add_component("ESC 4-in-1 55A",           ComponentCategory::Propulsion,  28.0f, Vector3D{  0.0f, 0.0f,   5.0f},  1.5f);
    uav.add_component("Пропелери 7.5x4.5 (4 шт)", ComponentCategory::Propulsion,  36.0f, Vector3D{  0.0f, 0.0f,  15.0f},  0.0f);
    uav.add_component("Політний контролер FC H7", ComponentCategory::Avionics,    14.0f, Vector3D{  0.0f, 0.0f,  12.0f},  3.0f);
    uav.add_component("GNSS модуль + Compass",    ComponentCategory::Avionics,    18.0f, Vector3D{-50.0f, 0.0f,  45.0f},  1.2f);
    uav.add_component("VTX 5.8GHz 2.5W + антена", ComponentCategory::Avionics,    32.0f, Vector3D{-40.0f, 0.0f,  20.0f}, 11.0f);
    uav.add_component("Приймач ELRS 868MHz",      ComponentCategory::Avionics,     4.0f, Vector3D{-30.0f, 0.0f,   8.0f},  0.5f);
    uav.add_component("Карбонова рама 7 дюймів",  ComponentCategory::Airframe,   165.0f, Vector3D{  0.0f, 0.0f,   0.0f},  0.0f);
    uav.add_component("Кріплення, демпфери, TPU", ComponentCategory::Airframe,    45.0f, Vector3D{  5.0f, 0.0f,   5.0f},  0.0f);
    uav.add_component("Конструкторський резерв",  ComponentCategory::Margin,      80.0f, Vector3D{  0.0f, 0.0f,   0.0f},  0.0f);

    const auto report = uav.calculate();
    uav.print_report(report);

    return 0;
}
