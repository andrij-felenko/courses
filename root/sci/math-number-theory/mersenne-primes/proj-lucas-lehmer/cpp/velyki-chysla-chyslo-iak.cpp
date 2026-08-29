#include <algorithm>
#include <cstdint>
#include <span>
#include <vector>

using Limb = std::uint32_t;

// Обчислення бітової довжини багаторозрядного числа
int bit_length(std::span<const Limb> a) noexcept {
    for (int i = static_cast<int>(a.size()) - 1; i >= 0; --i) {
        if (a[i] != 0) {
            int b = 32;
            while (!((a[i] >> (b - 1)) & 1U)) {
                --b;
            }
            return 32 * i + b;
        }
    }
    return 0;
}

// Побітовий зсув великого числа вправо на p бітів: out = a >> p
void shift_right_p(std::span<const Limb> a, int p, std::span<Limb> out) noexcept {
    const int W = static_cast<int>(a.size());
    const int n = static_cast<int>(out.size());
    const int Q = p / 32;                      // зсув на цілі 32-бітні слова
    const int R = p % 32;                      // бітовий зсув (R ∈ [1, 31])
    for (int i = 0; i < n; ++i) {
        const std::uint64_t lo = (i + Q < W) ? a[i + Q] : 0;
        const std::uint64_t hi = (i + Q + 1 < W) ? a[i + Q + 1] : 0;
        out[i] = static_cast<Limb>((lo >> R) | (hi << (32 - R)));
    }
}

// Додавання з поширенням переносу: a += b
void add_inplace(std::span<Limb> a, std::span<const Limb> b) noexcept {
    std::uint64_t carry = 0;
    const std::size_t count = std::min(a.size(), b.size());
    for (std::size_t i = 0; i < count; ++i) {
        const std::uint64_t cur = static_cast<std::uint64_t>(a[i]) + b[i] + carry;
        a[i] = static_cast<Limb>(cur);
        carry = cur >> 32;
    }
}

// Зведення за модулем Mp = 2ᵖ − 1 без ділення (бітова згортка)
void reduce_mod_mp(std::span<const Limb> prod, int p, std::span<Limb> r) {
    const int W = static_cast<int>(prod.size());
    const int n = static_cast<int>(r.size());
    const int Q = p / 32;
    const int R = p % 32;

    std::vector<Limb> acc(prod.begin(), prod.end());
    std::vector<Limb> low(W, 0);
    std::vector<Limb> high(W, 0);

    while (bit_length(acc) > p) {
        for (int i = 0; i < W; ++i) {
            if (i < Q) {
                low[i] = acc[i];
            } else if (i == Q) {
                low[i] = acc[i] & ((1U << R) - 1);
            } else {
                low[i] = 0;
            }
        }
        shift_right_p(acc, p, high);
        std::fill(acc.begin(), acc.end(), 0);
        add_inplace(acc, low);
        add_inplace(acc, high);
    }

    std::copy_n(acc.begin(), n, r.begin());

    // Якщо остача точно дорівнює Mp (усі p бітів одиниці), це еквівалент 0
    bool is_mp = true;
    for (int i = 0; i < n - 1; ++i) {
        if (r[i] != 0xFFFFFFFFU) {
            is_mp = false;
            break;
        }
    }
    if (r[n - 1] != ((1U << R) - 1)) {
        is_mp = false;
    }
    if (is_mp) {
        std::fill(r.begin(), r.end(), 0);
    }
}
