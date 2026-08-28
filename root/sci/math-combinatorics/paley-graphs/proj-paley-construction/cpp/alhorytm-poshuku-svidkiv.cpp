#include <span>
#include <vector>
#include <optional>
#include <bit>
#include <cstring>

std::optional<uint32_t> find_extension_witness_fast(
    const PaleyGraph &g,
    std::span<const uint32_t> U,
    std::span<const uint32_t> W) {

    uint32_t words = g.words_per_row();
    uint32_t n = g.order();
    std::vector<uint64_t> mask(words, ~0ULL);

    // Очищення зайвих бітів в останньому слові
    if (uint32_t rem = n % 64; rem != 0) {
        mask.back() = (1ULL << rem) - 1;
    }

    // 1. Повинна бути реберна суміжність з усіма u in U
    for (uint32_t u : U) {
        auto row = g.row_bitset(u);
        for (uint32_t w = 0; w < words; ++w) {
            mask[w] &= row[w];
        }
    }

    // 2. Повинна бути відсутність ребер з усіма w in W
    for (uint32_t w_node : W) {
        auto row = g.row_bitset(w_node);
        for (uint32_t w = 0; w < words; ++w) {
            mask[w] &= ~row[w];
        }
    }

    // 3. Виключаємо самі вершини з множин U та W
    for (uint32_t u : U) {
        mask[u / 64] &= ~(1ULL << (u % 64));
    }
    for (uint32_t w_node : W) {
        mask[w_node / 64] &= ~(1ULL << (w_node % 64));
    }

    // 4. Пошук першого ненульового біта
    for (uint32_t w = 0; w < words; ++w) {
        if (mask[w] != 0) {
            uint32_t bit_idx = static_cast<uint32_t>(std::countr_zero(mask[w]));
            return w * 64 + bit_idx;
        }
    }

    return std::nullopt;
}
