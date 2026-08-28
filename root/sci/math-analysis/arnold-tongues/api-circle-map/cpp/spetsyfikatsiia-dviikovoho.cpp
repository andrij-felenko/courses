#include <string_view>

namespace physics::nonlinear::api {

struct LibraryVersion {
    int major{1};
    int minor{0};
    int patch{0};

    [[nodiscard]] static constexpr std::string_view string() noexcept {
        return "1.0.0";
    }
};

} // namespace physics::nonlinear::api
