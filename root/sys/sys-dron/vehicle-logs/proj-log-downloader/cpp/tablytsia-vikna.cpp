#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>

constexpr uint32_t kChunk  = 90;                        // байтів у одному LOG_DATA
constexpr uint32_t kBins   = 2048;                      // кошиків у вікні
constexpr uint64_t kWindow = uint64_t(kChunk) * kBins;  // 184 320 Б

class Bits {
public:
    void clear() { w_.fill(0ull); }
    void set(uint32_t i)        { w_[i >> 6] |= 1ull << (i & 63); }
    bool test(uint32_t i) const { return (w_[i >> 6] >> (i & 63) & 1ull) != 0; }

    // перший нуль у [from, bins); bins, якщо нулів немає
    uint32_t firstZero(uint32_t from, uint32_t bins) const {
        for (uint32_t k = from >> 6; k * 64 < bins; ++k) {
            uint64_t free = ~w_[k];
            const uint32_t base = k * 64;
            if (base < from) free &= ~0ull << (from - base);      // лівий край
            const uint32_t width = std::min(64u, bins - base);
            if (width < 64)  free &= (1ull << width) - 1;         // хвіст поза вікном
            if (free) return base + uint32_t(std::countr_zero(free));
        }
        return bins;
    }

    // перша одиниця у [from, bins); bins, якщо одиниць далі немає
    uint32_t firstOne(uint32_t from, uint32_t bins) const {
        for (uint32_t k = from >> 6; k * 64 < bins; ++k) {
            uint64_t v = w_[k];
            const uint32_t base = k * 64;
            if (base < from) v &= ~0ull << (from - base);
            if (v) return std::min(bins, base + uint32_t(std::countr_zero(v)));
        }
        return bins;
    }

    uint32_t countZeros(uint32_t from, uint32_t to) const {
        uint32_t n = 0;
        for (uint32_t i = from; i < to; ++i) if (!test(i)) ++n;
        return n;
    }

private:
    std::array<uint64_t, kBins / 64> w_{};
};
