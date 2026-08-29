#pragma once
#include <cstdint>
#include <array>
#include <chrono>
#include "kliuchovi-struktury-danykh-2.hpp"

namespace linux_bridge {

struct FdbKey {
    std::array<uint8_t, 6> mac{};
    uint16_t vlan_id{0};
    bool operator==(const FdbKey& other) const = default;
};

struct NetBridgeFdbEntry {
    NetBridgePort* dst{nullptr};
    FdbKey key;
    std::chrono::steady_clock::time_point updated;
    std::chrono::steady_clock::time_point used;
    uint16_t flags{0};
    bool is_local{false};
    bool is_static{false};
    bool is_dynamic{true};
    bool added_by_user{false};
};

}
