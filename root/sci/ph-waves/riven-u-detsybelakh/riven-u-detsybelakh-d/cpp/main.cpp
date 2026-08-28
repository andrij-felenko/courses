#include <cmath>
#include <iostream>
#include <limits>

namespace acoustics {

inline constexpr double p0_spl_pa = 20.0e-6;
inline constexpr double v0_dbu    = 0.7745966692;

[[nodiscard]] constexpr double calculate_spl(double p_rms_pa) noexcept {
    if (p_rms_pa <= 0.0) {
        return -std::numeric_limits<double>::infinity();
    }
    return 20.0 * std::log10(p_rms_pa / p0_spl_pa);
}

[[nodiscard]] constexpr double voltage_to_dbu(double v_rms) noexcept {
    if (v_rms <= 0.0) {
        return -std::numeric_limits<double>::infinity();
    }
    return 20.0 * std::log10(v_rms / v0_dbu);
}

} // namespace acoustics

int main() {
    constexpr double p_talk = 0.02; // 0.02 Па = 20 мПа (розмова)
    constexpr double v_line = 1.228; // 1.228 В (+4 dBu)

    std::cout << "Звуковий тиск " << p_talk << " Па = " 
              << acoustics::calculate_spl(p_talk) << " дБ SPL\n";
    std::cout << "Напруга " << v_line << " В = " 
              << acoustics::voltage_to_dbu(v_line) << " dBu\n";
    return 0;
}
