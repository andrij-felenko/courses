#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <optional>
#include <cmath>

enum class PulseShape {
    Rectangular,
    HalfSine,
    Triangular,
    ExponentialRc
};

enum class FuseSpeed {
    VeryFastFF,
    FastF,
    SlowBlowT
};

enum class CircuitType {
    Ac,
    Dc
};

struct CircuitRequirements {
    double current_rms{0.0};       // Робочий струм навантаження, А
    double voltage{0.0};           // Робоча напруга кола, В
    CircuitType circuit_type{CircuitType::Ac};
    double temp_ambient{25.0};     // Температура середовища, °C
    double fault_current_max{0.0}; // Максимальний струм к.з. джерела, А
    
    // Параметри пускового імпульсу
    PulseShape pulse_shape{PulseShape::Rectangular};
    double pulse_peak_current{0.0}; // Піковий струм імпульсу, А
    double pulse_duration{0.0};     // Тривалість імпульсу (або RC тау), с
    int expected_cycles{100000};    // Очікувана кількість циклів ввімкнення

    // Граничний інтеграл захищуваного напівпровідника
    std::optional<double> semiconductor_i2t_limit{std::nullopt};
};

struct FuseModel {
    std::string_view part_number;
    double current_rating{0.0};    // Номінальний струм, А
    double voltage_rating_ac{0.0}; // Номінальна напруга AC, В
    double voltage_rating_dc{0.0}; // Номінальна напруга DC, В
    double breaking_capacity{0.0}; // Відключна здатність, А
    double i2t_melting{0.0};       // Інтеграл плавлення, А²·с
    double i2t_clearing{0.0};      // Повний інтеграл відключення, А²·с
    FuseSpeed speed_class{FuseSpeed::FastF};
};

struct SizingResult {
    bool is_valid{false};
    std::optional<FuseModel> selected_fuse{std::nullopt};
    double calculated_inrush_i2t{0.0};
    double min_required_i2t_melting{0.0};
    double temp_derating_factor{1.0};
    std::string_view status_message;
};

// Розрахунок температурного дератингу для стандартного запобіжника
[[nodiscard]] constexpr double calculate_temp_derating(double temp_celsius) noexcept {
    if (temp_celsius <= 25.0) {
        return 1.0;
    }
    // Зниження номіналу ~0.35% на градус вище 25°C
    const double derating = 1.0 - (temp_celsius - 25.0) * 0.0035;
    return (derating > 0.4) ? derating : 0.4;
}

// Визначення коефіцієнта циклічної втоми
[[nodiscard]] constexpr double calculate_pulse_factor(int cycles) noexcept {
    if (cycles <= 1) return 1.00;
    if (cycles <= 10) return 0.70;
    if (cycles <= 100) return 0.50;
    if (cycles <= 1000) return 0.40;
    if (cycles <= 10000) return 0.29;
    return 0.20; // 100 000+ циклів
}

// Обчислення I²t пускового імпульсу за його математичною формою
[[nodiscard]] constexpr double calculate_inrush_i2t(PulseShape shape, double i_peak, double duration) noexcept {
    switch (shape) {
        case PulseShape::Rectangular:
            return i_peak * i_peak * duration;
        case PulseShape::HalfSine:
            return 0.5 * i_peak * i_peak * duration;
        case PulseShape::Triangular:
            return (1.0 / 3.0) * i_peak * i_peak * duration;
        case PulseShape::ExponentialRc:
            // duration інтерпретується як стала часу tau = R*C
            return 0.5 * i_peak * i_peak * duration;
    }
    return i_peak * i_peak * duration;
}

// Головна функція інженерного підбору запобіжника
[[nodiscard]] SizingResult select_fuse(const CircuitRequirements& req, std::span<const FuseModel> catalog) {
    SizingResult res{};
    res.temp_derating_factor = calculate_temp_derating(req.temp_ambient);
    res.calculated_inrush_i2t = calculate_inrush_i2t(req.pulse_shape, req.pulse_peak_current, req.pulse_duration);
    
    const double pulse_factor = calculate_pulse_factor(req.expected_cycles);
    res.min_required_i2t_melting = res.calculated_inrush_i2t / pulse_factor;

    // Нормативний запас UL 0.75 для тривалого безперервного струму
    const double min_current_rating = req.current_rms / (res.temp_derating_factor * 0.75);

    for (const auto& fuse : catalog) {
        // 1. Перевірка за тривалим струмом
        if (fuse.current_rating < min_current_rating) {
            continue;
        }

        // 2. Перевірка за напругою (AC vs DC)
        if (req.circuit_type == CircuitType::Ac) {
            if (fuse.voltage_rating_ac < req.voltage) continue;
        } else {
            if (fuse.voltage_rating_dc < req.voltage) continue;
        }

        // 3. Перевірка граничної відключної здатності
        if (fuse.breaking_capacity < req.fault_current_max) {
            continue;
        }

        // 4. Перевірка стійкості до імпульсної втоми
        if (fuse.i2t_melting < res.min_required_i2t_melting) {
            continue;
        }

        // 5. Координація з силовим напівпровідником
        if (req.semiconductor_i2t_limit.has_value()) {
            const double safe_semi_limit = 0.75 * req.semiconductor_i2t_limit.value();
            if (fuse.i2t_clearing > safe_semi_limit) {
                continue;
            }
        }

        // Знайдено найменший придатний компонент
        res.is_valid = true;
        res.selected_fuse = fuse;
        res.status_message = "Компонент успішно підібрано та верифіковано";
        return res;
    }

    res.status_message = "Жоден компонент у каталозі не задовольняє всі критерії захисту";
    return res;
}

int main() {
    const std::vector<FuseModel> catalog = {
        {"FUSE-F-1A",    1.0,  250.0, 63.0,  50.0,    0.45,   1.2,   FuseSpeed::FastF},
        {"FUSE-T-1.25A", 1.25, 250.0, 63.0,  50.0,    2.80,   7.5,   FuseSpeed::SlowBlowT},
        {"FUSE-T-2A",    2.0,  250.0, 63.0,  1500.0,  9.50,   24.0,  FuseSpeed::SlowBlowT},
        {"FUSE-FF-2A",   2.0,  250.0, 125.0, 10000.0, 0.85,   2.1,   FuseSpeed::VeryFastFF},
        {"FUSE-T-3.15A", 3.15, 250.0, 63.0,  1500.0,  22.0,   60.0,  FuseSpeed::SlowBlowT}
    };

    CircuitRequirements req{
        .current_rms = 0.8,
        .voltage = 230.0,
        .circuit_type = CircuitType::Ac,
        .temp_ambient = 45.0,
        .fault_current_max = 1000.0,
        .pulse_shape = PulseShape::ExponentialRc,
        .pulse_peak_current = 30.0,
        .pulse_duration = 0.0012,
        .expected_cycles = 100000,
        .semiconductor_i2t_limit = std::nullopt
    };

    const auto res = select_fuse(req, catalog);

    if (res.is_valid && res.selected_fuse.has_value()) {
        const auto& f = res.selected_fuse.value();
        std::cout << "Обрано компонент: " << f.part_number 
                  << " (Номінал: " << f.current_rating << " А)\n";
        std::cout << "Пусковий I²t: " << res.calculated_inrush_i2t 
                  << " А²·с | Необхідний I²t плавлення: " << res.min_required_i2t_melting << " А²·с\n";
        std::cout << "Температурний коефіцієнт дератингу: " << res.temp_derating_factor << "\n";
    } else {
        std::cout << "Помилка підбору: " << res.status_message << "\n";
    }

    return 0;
}
