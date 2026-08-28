#include <expected>
#include <cstdint>

namespace mcuboot {

enum class SwapType : uint8_t {
    None   = 1,
    Test   = 2,
    Perm   = 3,
    Revert = 4,
    Fail   = 5,
    Panic  = 6
};

class BootManager {
public:
    [[nodiscard]] static std::expected<void, int> mark_confirmed() noexcept;
    [[nodiscard]] static std::expected<void, int> request_upgrade(bool permanent) noexcept;
    [[nodiscard]] static SwapType current_swap_type() noexcept;
};

} // namespace mcuboot
