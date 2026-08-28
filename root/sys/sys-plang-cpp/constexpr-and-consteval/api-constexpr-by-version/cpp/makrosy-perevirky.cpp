#include <array>

constexpr std::array<int, 4> make_lut() { return {1, 2, 4, 8}; }

#if defined(__cpp_constexpr) && __cpp_constexpr >= 202211L
constexpr int weight(int i) {
    static constexpr auto lut = make_lut();   // одна копія на програму
    return lut[i];
}
#else
constexpr auto g_lut = make_lut();            // до C++23 — лише за межами функції
constexpr int weight(int i) { return g_lut[i]; }
#endif

static_assert(weight(3) == 8);
