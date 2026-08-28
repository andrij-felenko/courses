#include <iostream>
#include <iomanip>
#include <expected>
#include <string_view>

struct NodeMeasurement {
    double v_measured{0.0};     // Виміряна напруга (В)
    double r_thevenin{0.0};    // Еквівалентний опір Тевеніна (Ом)
    double r_meter{10e6};       // Вхідний опір вольтметра (Ом)
};

struct CorrectedResult {
    double v_actual{0.0};
    double error_percent{0.0};
};

enum class CorrectionError {
    InvalidResistance,
    NullPointer
};

[[nodiscard]] constexpr auto calculate_true_voltage(const NodeMeasurement& m) 
    -> std::expected<CorrectedResult, CorrectionError> 
{
    if (m.r_meter <= 0.0 || m.r_thevenin < 0.0) {
        return std::unexpected(CorrectionError::InvalidResistance);
    }

    const double v_true = m.v_measured * (1.0 + (m.r_thevenin / m.r_meter));
    const double err_pct = ((m.v_measured - v_true) / v_true) * 100.0;

    return CorrectedResult{
        .v_actual = v_true,
        .error_percent = err_pct
    };
}

int main() {
    constexpr NodeMeasurement test_node{
        .v_measured = 1.6667,
        .r_thevenin = 500'000.0, // 500 кОм
        .r_meter = 1'000'000.0    // 1 МОм
    };

    const auto result = calculate_true_voltage(test_node);
    if (result) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Показ вольтметра:     " << test_node.v_measured << " V\n";
        std::cout << "Істинна напруга:      " << result->v_actual << " V\n";
        std::cout << "Похибка навантаження: " << std::setprecision(2) 
                  << result->error_percent << " %\n";
    } else {
        std::cerr << "Помилка обчислення параметрів навантаження\n";
    }

    return 0;
}
