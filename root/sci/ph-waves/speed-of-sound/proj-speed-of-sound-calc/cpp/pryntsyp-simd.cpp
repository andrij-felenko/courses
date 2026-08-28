// Modern C++20 / C++23 std::experimental::simd vectorization
#include <experimental/simd>
#include <span>

namespace stdx = std::experimental;

void calc_speed_air_simd(std::span<const double> temps, std::span<double> speeds) {
    using simd_4d = stdx::fixed_size_simd<double, 4>;
    const simd_4d v_c0(331.3);
    const simd_4d v_inv273(1.0 / 273.15);

    for (size_t i = 0; i + 4 <= temps.size(); i += 4) {
        simd_4d v_t(&temps[i], stdx::element_aligned);
        simd_4d v_term = 1.0 + v_t * v_inv273;
        simd_4d v_c = v_c0 * stdx::sqrt(v_term);
        v_c.copy_to(&speeds[i], stdx::element_aligned);
    }
}
