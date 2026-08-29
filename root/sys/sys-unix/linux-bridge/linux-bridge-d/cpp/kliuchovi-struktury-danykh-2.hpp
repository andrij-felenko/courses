#pragma once
#include <cstdint>
#include <memory>

namespace linux_bridge {
enum class BridgePortState : uint8_t { Disabled = 0, Listening = 1, Learning = 2, Forwarding = 3, Blocking = 4 };
struct NetBridge;
struct NetDevice;
struct NetBridgeTlanGroup;
struct NetBridgePort {
    NetBridge* br{nullptr};
    NetDevice* dev{nullptr};
    BridgePortState state{BridgePortState::Disabled};
    uint8_t priority{32};
    uint32_t path_cost{100};
    uint16_t port_no{0};
    uint32_t flags{0};
    std::shared_ptr<NetBridgeVlanGroup> vlgrp;
};
}
