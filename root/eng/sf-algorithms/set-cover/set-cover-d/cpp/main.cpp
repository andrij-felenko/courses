#include <vector>
#include <bitset>
#include <optional>
#include <span>
#include <limits>

constexpr size_t UNIVERSE_CAPACITY = 64;
using BitMask = std::bitset<UNIVERSE_CAPACITY>;

struct FastSubset {
    int id;
    double cost;
    BitMask mask;
};

class GreedySetCoverEngine {
public:
    static std::optional<size_t> findBestCandidate(
        std::span<const FastSubset> subsets,
        const BitMask& covered
    ) noexcept {
        size_t best_idx = 0;
        bool found = false;
        double best_ratio = std::numeric_limits<double>::infinity();

        for (size_t i = 0; i < subsets.size(); ++i) {
            BitMask newly = subsets[i].mask & (~covered);
            size_t count = newly.count();

            if (count > 0) {
                double ratio = subsets[i].cost / static_cast<double>(count);
                if (ratio < best_ratio) {
                    best_ratio = ratio;
                    best_idx = i;
                    found = true;
                }
            }
        }

        return found ? std::make_optional(best_idx) : std::nullopt;
    }
};
