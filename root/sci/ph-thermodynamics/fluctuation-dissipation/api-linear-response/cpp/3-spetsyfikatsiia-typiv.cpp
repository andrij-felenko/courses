#include <complex>
#include <vector>
#include <span>
#include <expected>
#include <string_view>
#include <concepts>
#include <system_error>

namespace fdt {

/// Системні помилки аналізу лінійного відгуку
enum class FdtError {
    InvalidDataSize,
    NonUniformSampling,
    CausalityViolation,
    TemperatureOutOfRange,
    IntegrationDivergence
};

/// Структура фізичних констант середовища
struct PhysicalEnvironment {
    double temperature_kelvin{300.0};
    double hbar{1.054571817e-34};
    double k_B{1.380649e-23};
};

/// Спектральна точка комплексної сприйнятливості
struct SusceptibilityPoint {
    double frequency_rad_s;
    std::complex<double> susceptibility;
};

} // namespace fdt
