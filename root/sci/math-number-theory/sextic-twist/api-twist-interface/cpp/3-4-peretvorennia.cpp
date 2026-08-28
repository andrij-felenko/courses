#include <vector>

struct UntwistResult {
    std::vector<std::uint8_t> x_coeff;
    std::vector<std::uint8_t> y_coeff;
};

class MillerUntwister {
public:
    [[nodiscard]] std::expected<UntwistResult, TwistStatus> untwist_for_miller(
        std::span<const std::uint8_t> in_g2_point
    ) const noexcept;
};
