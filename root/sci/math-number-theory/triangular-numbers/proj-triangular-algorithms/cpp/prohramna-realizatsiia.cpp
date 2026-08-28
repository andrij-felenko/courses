#include <iostream>
#include <vector>
#include <cstdint>
#include <limits>

namespace math {

struct SquareTriangular {
    std::uint64_t index_n;
    std::uint64_t root_k;
    std::uint64_t value;
};

class SquareTriangularGenerator {
public:
    static std::vector<SquareTriangular> generate(std::size_t count) {
        std::vector<SquareTriangular> result;
        result.reserve(count);

        std::uint64_t n = 1;
        std::uint64_t k = 1;

        while (result.size() < count) {
            result.push_back({n, k, k * k});

            // Перевірка на переповнення
            if (n > (std::numeric_limits<std::uint64_t>::max() - 4 * k - 1) / 3) {
                break;
            }

            const std::uint64_t next_n = 3 * n + 4 * k + 1;
            const std::uint64_t next_k = 2 * n + 3 * k + 1;

            n = next_n;
            k = next_k;
        }

        return result;
    }
};

} // namespace math
