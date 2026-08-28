#include <cstdint>
#include <cstddef>
#include <span>
#include <utility>
#include <type_traits>

namespace crypto::constant_time {

/* Умовна перестановка двох довільних об'єктів однакового типу */
template <typename T>
requires std::is_trivially_copyable_v<T>
void cswap(bool condition, T &a, T &b) noexcept {
    auto *pa = reinterpret_cast<uint8_t*>(&a);
    auto *pb = reinterpret_cast<uint8_t*>(&b);
    const uint8_t cond_val = condition ? 1U : 0U;
    uint8_t mask = static_cast<uint8_t>(-static_cast<int8_t>(cond_val));
    mask = barrier(mask);

    for (size_t i = 0; i < sizeof(T); ++i) {
        const uint8_t delta = mask & (pa[i] ^ pb[i]);
        pa[i] ^= delta;
        pb[i] ^= delta;
    }
}

/* Умовна перестановка буферів пам'яті std::span */
void cswap_spans(bool condition, std::span<uint8_t> a, std::span<uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return;
    }
    const uint8_t cond_val = condition ? 1U : 0U;
    uint8_t mask = static_cast<uint8_t>(-static_cast<int8_t>(cond_val));
    mask = barrier(mask);

    for (size_t i = 0; i < a.size(); ++i) {
        const uint8_t delta = mask & (a[i] ^ b[i]);
        a[i] ^= delta;
        b[i] ^= delta;
    }
}

} // namespace crypto::constant_time
