#include <iostream>
#include <vector>
#include <string_view>
#include <iomanip>
#include <optional>

struct HardwareTier {
    std::string_view name;
    double nre_dev{0.0};         // Вартість інженерної розробки, $
    double nre_tooling{0.0};     // Трафарети, тестові голчасті адаптери, $
    double cert_cost{0.0};       // Витрати на сертифікаційні лабораторії, $
    double bom_cost{0.0};        // Вартість комплектуючих за специфікацією, $
    double smt_cost{0.0};        // Монтаж за одиницю на лінії SMT, $
    double test_cost{0.0};       // Функціональне тестування за одиницю, $
    double scrap_rate{0.02};     // Частка технологічного браку
    int time_to_market_w{4};     // Термін розробки у тижнях

    [[nodiscard]] constexpr double total_nre() const noexcept {
        return nre_dev + nre_tooling + cert_cost;
    }

    [[nodiscard]] constexpr double unit_variable_cost() const noexcept {
        const double base = bom_cost + smt_cost + test_cost;
        if (scrap_rate >= 1.0) {
            return base * 2.0;
        }
        return base / (1.0 - scrap_rate);
    }

    [[nodiscard]] constexpr double tco(unsigned int volume) const noexcept {
        return total_nre() + static_cast<double>(volume) * unit_variable_cost();
    }

    [[nodiscard]] constexpr double effective_unit_cost(unsigned int volume) const noexcept {
        if (volume == 0) return total_nre();
        return tco(volume) / static_cast<double>(volume);
    }
};

// Розрахунок точки беззбитковості (Break-Even) між двома рішеннями
[[nodiscard]] constexpr std::optional<double> calculate_breakeven(
    const HardwareTier& low_nre_tier,
    const HardwareTier& high_nre_tier) noexcept 
{
    const double nre1 = low_nre_tier.total_nre();
    const double nre2 = high_nre_tier.total_nre();
    const double var1 = low_nre_tier.unit_variable_cost();
    const double var2 = high_nre_tier.unit_variable_cost();

    if (var1 <= var2 || nre2 <= nre1) {
        return std::nullopt;
    }

    return (nre2 - nre1) / (var1 - var2);
}

int main() {
    const std::vector<HardwareTier> tiers = {
        {
            .name = "1. Девборда + макетка",
            .nre_dev = 200.0,
            .nre_tooling = 0.0,
            .cert_cost = 0.0,
            .bom_cost = 45.0,
            .smt_cost = 0.0,
            .test_cost = 5.0,
            .scrap_rate = 0.05,
            .time_to_market_w = 1
        },
        {
            .name = "2. Модуль на платі-носії",
            .nre_dev = 2500.0,
            .nre_tooling = 300.0,
            .cert_cost = 1500.0,
            .bom_cost = 16.50,
            .smt_cost = 2.50,
            .test_cost = 1.00,
            .scrap_rate = 0.02,
            .time_to_market_w = 4
        },
        {
            .name = "3. SoM на платі-носії",
            .nre_dev = 7000.0,
            .nre_tooling = 600.0,
            .cert_cost = 3500.0,
            .bom_cost = 42.00,
            .smt_cost = 3.50,
            .test_cost = 2.00,
            .scrap_rate = 0.02,
            .time_to_market_w = 10
        },
        {
            .name = "4. Повністю своя (Chip-Down)",
            .nre_dev = 35000.0,
            .nre_tooling = 4000.0,
            .cert_cost = 25000.0,
            .bom_cost = 9.80,
            .smt_cost = 1.80,
            .test_cost = 0.80,
            .scrap_rate = 0.04,
            .time_to_market_w = 32
        }
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== ПОРІВНЯЛЬНИЙ АНАЛІЗ АПАРАТНИХ СХОДИНОК ===\n\n";

    for (const auto& tier : tiers) {
        std::cout << tier.name << ":\n"
                  << "  Сумарний NRE:         $" << tier.total_nre() << "\n"
                  << "  Змінна собівартість:   $" << tier.unit_variable_cost() << " / шт\n"
                  << "  Час виходу на ринок:  " << tier.time_to_market_w << " тижнів\n\n";
    }

    if (const auto v_star = calculate_breakeven(tiers[1], tiers[3]); v_star.has_value()) {
        std::cout << "Точка беззбитковості (Модуль на носії vs Chip-Down):\n"
                  << "  V* = " << static_cast<unsigned long>(*v_star) << " шт.\n"
                  << "  До " << static_cast<unsigned long>(*v_star) << " шт вигідніший сертифікований модуль на носії.\n"
                  << "  Понад " << static_cast<unsigned long>(*v_star) << " шт окупається перехід на Chip-Down.\n\n";
    }

    const std::vector<unsigned int> sample_volumes = {500, 2000, 10000, 50000};
    std::cout << "--- Ефективна вартість одиниці залежно від тиражу ---\n";
    for (unsigned int vol : sample_volumes) {
        std::cout << "\nТираж V = " << vol << " шт:\n";
        for (const auto& tier : tiers) {
            std::cout << "  " << std::left << std::setw(28) << tier.name
                      << " TCO: $" << std::right << std::setw(10) << tier.tco(vol)
                      << "  (фактично $" << std::setw(6) << tier.effective_unit_cost(vol) << "/шт)\n";
        }
    }

    return 0;
}
