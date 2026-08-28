#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

template <std::equality_comparable T>
struct SummaryVote {
    T candidate{};
    std::size_t count{0};

    [[nodiscard]] constexpr friend SummaryVote operator+(const SummaryVote& lhs, const SummaryVote& rhs) noexcept {
        if (lhs.count == 0) return rhs;
        if (rhs.count == 0) return lhs;

        if (lhs.candidate == rhs.candidate) {
            return SummaryVote{ lhs.candidate, lhs.count + rhs.count };
        }

        if (lhs.count >= rhs.count) {
            return SummaryVote{ lhs.candidate, lhs.count - rhs.count };
        } else {
            return SummaryVote{ rhs.candidate, rhs.count - lhs.count };
        }
    }
};
