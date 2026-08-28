#include <cstdint>
#include <optional>

namespace gnss::api {

struct GalileoNeQuickBroadcast {
    double        a_z0{63.7};
    double        a_z1{0.0};
    double        a_z2{0.0};
    std::uint8_t  region_flags{0};
    std::uint32_t issue_of_data{0};
    bool          valid{false};

    [[nodiscard]] constexpr double calculateAz(double modip_deg) const noexcept {
        return a_z0 + a_z1 * modip_deg + a_z2 * modip_deg * modip_deg;
    }
};

} // namespace gnss::api
