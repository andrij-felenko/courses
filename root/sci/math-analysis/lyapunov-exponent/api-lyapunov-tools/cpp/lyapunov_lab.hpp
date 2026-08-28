// lyapunov_lab.hpp - C++20 API специфікація бібліотеки LyapunovLab
#ifndef LYAPUNOV_LAB_HPP
#define LYAPUNOV_LAB_HPP

#include <vector>
#include <array>
#include <functional>
#include <string_view>
#include <expected>
#include <memory>
#include <span>
#include <cstddef>

namespace lyapunov_lab {

enum class IntegratorType {
    RK4,
    DormandPrince8
};

enum class ErrorCode {
    InvalidDimension,
    NullPointer,
    Divergence,
    OutOfMemory
};

struct Config {
    std::size_t dim{3};
    double dt{0.01};
    std::size_t total_steps{100000};
    std::size_t transient_steps{10000};
    std::size_t qr_period{1};
    IntegratorType method{IntegratorType::RK4};
};

using RhsFunction = std::function<void(double t, std::span<const double> x, std::span<double> dxdt)>;
using JacobianFunction = std::function<void(double t, std::span<const double> x, std::span<double> J_flat)>;

struct System {
    RhsFunction rhs;
    JacobianFunction jacobian;
};

struct Metrics {
    std::vector<double> spectrum;
    double lyapunov_dimension{0.0};
    double lyapunov_time{0.0};
    double ks_entropy{0.0};
    bool is_chaotic{false};
};

class Analyzer {
public:
    explicit Analyzer(Config config);
    ~Analyzer() = default;

    Analyzer(const Analyzer&) = delete;
    Analyzer& operator=(const Analyzer&) = delete;
    Analyzer(Analyzer&&) noexcept = default;
    Analyzer& operator=(Analyzer&&) noexcept = default;

    [[nodiscard]] std::expected<Metrics, ErrorCode> compute(
        const System& sys,
        std::span<const double> initial_state
    ) const;

private:
    Config config_;
};

[[nodiscard]] constexpr std::string_view to_string(ErrorCode code) noexcept {
    switch (code) {
        case ErrorCode::InvalidDimension: return "Некоректна розмірність фазового простору";
        case ErrorCode::NullPointer:      return "Нульовий вказівник на функцію системи";
        case ErrorCode::Divergence:       return "Розбіжність чисельного розв'язку (overflow)";
        case ErrorCode::OutOfMemory:      return "Недостатньо оперативної пам'яті";
    }
    return "Невідома помилка";
}

} // namespace lyapunov_lab

#endif // LYAPUNOV_LAB_HPP
