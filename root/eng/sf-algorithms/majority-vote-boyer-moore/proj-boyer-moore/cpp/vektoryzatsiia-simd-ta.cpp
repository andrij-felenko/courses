#include <immintrin.h>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <span>

class SimdVerifier {
public:
    [[nodiscard]] static std::size_t count_frequency(std::span<const int32_t> data, int32_t target) noexcept {
        std::size_t count = 0;
        std::size_t i = 0;
        const std::size_t size = data.size();
        const int32_t* ptr = data.data();

        const __m256i target_vec = _mm256_set1_epi32(target);

        for (; i + 8 <= size; i += 8) {
            const __m256i chunk = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(ptr + i));
            const __m256i match = _mm256_cmpeq_epi32(chunk, target_vec);
            const int mask = _mm256_movemask_epi8(match);
            if (mask != 0) {
                count += static_cast<std::size_t>(std::popcount(static_cast<unsigned int>(mask))) / 4;
            }
        }

        for (; i < size; ++i) {
            if (ptr[i] == target) {
                ++count;
            }
        }

        return count;
    }
};
