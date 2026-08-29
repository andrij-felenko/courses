#include "kliuchovi-struktury-danykh.hpp"
#include "struktura-zapysu-fdb.hpp"

namespace linux_bridge {

enum class PacketType { Unicast, Multicast, Broadcast };

struct SkBuff {
    FdbKey dest_key;
    PacketType pkt_type{PacketType::Unicast};
    bool is_local{false};
};

void br_flood(NetBridge& br, const SkBuff& skb, PacketType type) {
    for (const auto& port : br.port_list) {
        if (port && port->state == BridgePortState::Forwarding) {}
    }
}

void forward_frame(NetBridge& br, const SkBuff& skb, const NetBridgeFdbEntry* dst_entry) {
    if (skb.pkt_type == PacketType::Broadcast) br_flood(br, skb, PacketType::Broadcast);
    else if (skb.pkt_type == PacketType::Multicast) br_flood(br, skb, PacketType::Multicast);
    else if (dst_entry != nullptr) {
        if (dst_entry->is_local) {}
        else if (dst_entry->dst && dst_entry->dst->state == BridgePortState::Forwarding) {}
    } else br_flood(br, skb, PacketType::Unicast);
}

}
