#include <cstdint>
#include <cstddef>
#include <span>

namespace crypto::curve {

struct Point {
    uint64_t x{1};
    uint64_t z{0};
};

/* Арифметичний крок драбини Монтгомері */
void montgomery_step(Point &r0, Point &r1, const Point &base) noexcept {
    r0.x = r0.x + r1.x;
    r0.z = r0.z * base.x;
    r1.x = r1.x * r1.x;
    r1.z = r1.z + base.z;
}

/* Постійночасове скалярне множення точки еліптичної кривої */
[[nodiscard]] Point scalar_multiply_ct(std::span<const uint8_t> scalar, const Point &base) noexcept {
    Point r0{ .x = 1, .z = 0 };
    Point r1 = base;
    bool prev_bit = false;

    for (auto it = scalar.rbegin(); it != scalar.rend(); ++it) {
        const uint8_t byte = *it;
        for (int b = 7; b >= 0; --b) {
            const bool bit = ((byte >> b) & 1U) != 0;
            const bool swap_needed = bit ^ prev_bit;

            constant_time::cswap(swap_needed, r0, r1);
            montgomery_step(r0, r1, base);

            prev_bit = bit;
        }
    }

    constant_time::cswap(prev_bit, r0, r1);
    return r0;
}

} // namespace crypto::curve
