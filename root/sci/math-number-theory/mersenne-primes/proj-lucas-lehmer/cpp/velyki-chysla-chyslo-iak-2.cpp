#include <algorithm>
#include <cstdint>
#include <span>

using Limb = std::uint32_t;

// Множення великого числа на себе («стовпчик»): prod = a²
void square(std::span<const Limb> a, std::span<Limb> prod) noexcept {
    std::fill(prod.begin(), prod.end(), 0);
    const int n = static_cast<int>(a.size());
    for (int i = 0; i < n; ++i) {
        std::uint64_t carry = 0;
        for (int j = 0; j < n; ++j) {
            const std::uint64_t cur = static_cast<std::uint64_t>(prod[i + j]) +
                                     static_cast<std::uint64_t>(a[i]) * a[j] + carry;
            prod[i + j] = static_cast<Limb>(cur);
            carry = cur >> 32;
        }
        prod[i + n] += static_cast<Limb>(carry);
    }
}
