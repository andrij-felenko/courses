#include <cstddef>
#include <cstdint>
#include <span>

class BranchlessMajorityTracker {
public:
    [[nodiscard]] static int32_t find_candidate(std::span<const int32_t> stream) noexcept {
        int32_t candidate = 0;
        int32_t count = 0;

        for (const int32_t value : stream) {
            const bool is_zero = (count == 0);
            candidate = is_zero ? value : candidate;
            count = is_zero ? 1 : (count + ((candidate == value) ? 1 : -1));
        }

        return candidate;
    }
};
