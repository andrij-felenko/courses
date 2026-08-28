#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <array>
#include <vector>

namespace wifi::kvr {

inline constexpr uint8_t ELEMID_NEIGHBOR_REPORT = 0x34;
inline constexpr uint8_t ELEMID_MOBILITY_DOMAIN = 0x36;
inline constexpr uint8_t ELEMID_FAST_TRANSITION = 0x37;

inline constexpr uint8_t WNM_CATEGORY_CODE   = 0x0A;
inline constexpr uint8_t WNM_ACTION_BTM_REQ  = 0x07;
inline constexpr uint8_t WNM_ACTION_BTM_RESP = 0x08;

struct MobilityDomainInfo {
    uint16_t mdid{0};
    bool ft_over_ds{false};
    bool resource_request_cap{false};
};

struct NeighborEntry {
    std::array<uint8_t, 6> bssid{};
    uint32_t bssid_info{0};
    uint8_t reg_class{0};
    uint8_t channel{0};
    uint8_t phy_type{0};

    [[nodiscard]] constexpr bool is_same_security() const noexcept {
        return (bssid_info & (1U << 2)) != 0;
    }

    [[nodiscard]] constexpr bool is_ft_supported() const noexcept {
        return (bssid_info & (1U << 10)) != 0;
    }

    [[nodiscard]] constexpr bool is_he_wifi6() const noexcept {
        return (bssid_info & (1U << 13)) != 0;
    }
};

struct BtmRequestInfo {
    uint8_t dialog_token{0};
    bool preferred_candidate_list{false};
    bool disassociation_imminent{false};
    uint16_t disassoc_timer_tbtt{0};
    uint8_t validity_interval{0};
};

class FrameParser {
public:
    static std::optional<MobilityDomainInfo> parse_mdie(std::span<const uint8_t> payload) noexcept {
        if (payload.size() < 5 || payload[0] != ELEMID_MOBILITY_DOMAIN) {
            return std::nullopt;
        }
        const uint8_t len = payload[1];
        if (len < 3 || payload.size() < static_cast<size_t>(2 + len)) {
            return std::nullopt;
        }

        const uint16_t mdid = static_cast<uint16_t>(payload[2]) | 
                             (static_cast<uint16_t>(payload[3]) << 8);
        const uint8_t cap = payload[4];

        return MobilityDomainInfo{
            .mdid = mdid,
            .ft_over_ds = (cap & 0x01) != 0,
            .resource_request_cap = (cap & 0x02) != 0
        };
    }

    static std::optional<NeighborEntry> parse_neighbor_report_elem(std::span<const uint8_t> payload) noexcept {
        if (payload.size() < 15 || payload[0] != ELEMID_NEIGHBOR_REPORT) {
            return std::nullopt;
        }
        const uint8_t len = payload[1];
        if (len < 13 || payload.size() < static_cast<size_t>(2 + len)) {
            return std::nullopt;
        }

        NeighborEntry entry{};
        for (size_t i = 0; i < 6; ++i) {
            entry.bssid[i] = payload[2 + i];
        }

        entry.bssid_info = static_cast<uint32_t>(payload[8]) |
                          (static_cast<uint32_t>(payload[9]) << 8) |
                          (static_cast<uint32_t>(payload[10]) << 16) |
                          (static_cast<uint32_t>(payload[11]) << 24);

        entry.reg_class = payload[12];
        entry.channel = payload[13];
        entry.phy_type = payload[14];

        return entry;
    }

    static std::optional<BtmRequestInfo> parse_btm_request(std::span<const uint8_t> payload) noexcept {
        if (payload.size() < 7 || payload[0] != WNM_CATEGORY_CODE || payload[1] != WNM_ACTION_BTM_REQ) {
            return std::nullopt;
        }

        const uint8_t mode = payload[3];
        const uint16_t timer = static_cast<uint16_t>(payload[4]) | 
                              (static_cast<uint16_t>(payload[5]) << 8);

        return BtmRequestInfo{
            .dialog_token = payload[2],
            .preferred_candidate_list = (mode & (1U << 0)) != 0,
            .disassociation_imminent = (mode & (1U << 2)) != 0,
            .disassoc_timer_tbtt = timer,
            .validity_interval = payload[6]
        };
    }
};

} // namespace wifi::kvr
