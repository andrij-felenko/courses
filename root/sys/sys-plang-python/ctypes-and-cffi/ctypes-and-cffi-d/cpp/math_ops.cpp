// math_ops.cpp
#include <cstdint>
#include <cstddef>
#include <span>

extern "C" int32_t add_vectors(const int32_t *a, const int32_t *b, int32_t *out, std::size_t n) noexcept {
    if (!a || !b || !out) return -1;
    std::span<const int32_t> span_a(a, n);
    std::span<const int32_t> span_b(b, n);
    std::span<int32_t>       span_out(out, n);
    for (std::size_t i = 0; i < n; ++i) {
        span_out[i] = span_a[i] + span_b[i];
    }
    return 0;
}
