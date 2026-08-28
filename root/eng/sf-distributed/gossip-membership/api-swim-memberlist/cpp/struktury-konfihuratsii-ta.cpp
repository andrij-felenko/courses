#include <cstdint>
#include <chrono>
#include <functional>
#include <string_view>
#include <span>

namespace swim {

enum class NodeStatus : uint8_t {
    Alive   = 0,
    Suspect = 1,
    Dead    = 2,
    Left    = 3
};

struct Member {
    uint32_t ip{0};
    uint16_t port{0};
    uint64_t incarnation{0};
    NodeStatus status{NodeStatus::Alive};
    std::chrono::steady_clock::time_point state_change_time;
    uint8_t suspect_confirmations{0};
};

struct Config {
    uint32_t bind_ip{0};
    uint16_t bind_port{0};
    std::chrono::milliseconds probe_interval{1000};
    std::chrono::milliseconds probe_timeout{200};
    uint32_t indirect_checks_k{3};
    uint32_t suspicion_multiplier{4};
    uint32_t retransmit_multiplier{3};

    std::function<void(const Member&)> on_node_join;
    std::function<void(const Member&)> on_node_leave;
    std::function<void(const Member&)> on_node_failed;
    std::function<void(std::span<const uint8_t>)> on_user_message;
};

} // namespace swim
