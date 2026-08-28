#include <iostream>
#include <vector>
#include <cstdint>
#include <algorithm>

struct RipRoute {
    uint32_t dest_ip;
    uint32_t metric;
};

struct RipUpdatePacket {
    uint32_t sender_ip;
    std::vector<RipRoute> routes;
};

class RoutingTable {
public:
    static constexpr uint32_t RIP_INFINITY = 16;

    struct Entry {
        uint32_t dest_ip;
        uint32_t next_hop;
        uint32_t metric;
        int timer_seconds;
    };

    void process_update(const RipUpdatePacket& update) {
        for (const auto& route : update.routes) {
            uint32_t new_metric = std::min(route.metric + 1, RIP_INFINITY);

            auto it = std::find_if(table_.begin(), table_.end(), [&](const Entry& e) {
                return e.dest_ip == route.dest_ip;
            });

            if (it != table_.end()) {
                if (it->next_hop == update.sender_ip || new_metric < it->metric) {
                    it->metric = new_metric;
                    it->next_hop = update.sender_ip;
                    it->timer_seconds = 180;
                }
            } else if (new_metric < RIP_INFINITY) {
                table_.push_back({route.dest_ip, update.sender_ip, new_metric, 180});
            }
        }
    }

private:
    std::vector<Entry> table_;
};
