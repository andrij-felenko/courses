#include <cstdint>
#include <string_view>

namespace mcuboot {

enum class SwapState : uint8_t {
    None   = 1,
    Test   = 2,
    Perm   = 3,
    Revert = 4,
    Fail   = 5,
    Panic  = 6
};

[[nodiscard]] constexpr std::string_view to_string(SwapState state) noexcept {
    switch (state) {
        case SwapState::None:   return "NONE";
        case SwapState::Test:   return "TEST";
        case SwapState::Perm:   return "PERM";
        case SwapState::Revert: return "REVERT";
        case SwapState::Fail:   return "FAIL";
        case SwapState::Panic:  return "PANIC";
    }
    return "UNKNOWN";
}

} // namespace mcuboot
