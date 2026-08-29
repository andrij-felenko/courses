#pragma once
#include <cstdint>
#include <vector>
#include <memory>
#include <mutex>
#include "kliuchovi-struktury-danykh-2.hpp"

namespace linux_bridge {

struct BridgeId {
    uint16_t priority{32768};
    uint8_t mac[6]{};
};

struct NetBridge {
    mutable std::mutex lock;
    mutable std::mutex hash_lock;
    std::vector<std::shared_ptr<NetBridgePort>> port_list;
    NetDevice* dev{nullptr};
    BridgeId bridge_id;
    uint64_t ageing_time_ms{300000};
    uint8_t stp_enabled{0};
    bool vlan_filtering{false};
    uint16_t default_pvid{1};
    std::shared_ptr<NetBridgeVlanGroup> vlgrp;
    bool multicast_snooping{true};
};

}
