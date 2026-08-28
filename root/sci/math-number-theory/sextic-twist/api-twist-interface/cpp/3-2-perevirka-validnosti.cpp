#include <span>

class G2Validator {
public:
    [[nodiscard]] std::expected<void, TwistStatus> is_on_curve(
        std::span<const std::uint8_t> in_g2_uncompressed
    ) const noexcept;

    [[nodiscard]] std::expected<void, TwistStatus> validate_subgroup(
        std::span<const std::uint8_t> in_g2_uncompressed
    ) const noexcept;
};
