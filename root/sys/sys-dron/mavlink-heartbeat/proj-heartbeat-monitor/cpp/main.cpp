#include <iostream>
#include <cstdint>
#include <chrono>
#include <unordered_map>
#include <functional>
#include <string_view>
#include <mutex>

namespace mavlink {

enum class LinkState {
    Offline,
    Online,
    Warning,
    Lost
};

struct NodeAddress {
    uint8_t sysid{0};
    uint8_t compid{0};

    bool operator==(const NodeAddress& other) const noexcept {
        return sysid == other.sysid && compid == other.compid;
    }
};

struct NodeAddressHash {
    std::size_t operator()(const NodeAddress& addr) const noexcept {
        return (static_cast<std::size_t>(addr.sysid) << 8) | static_cast<std::size_t>(addr.compid);
    }
};

struct NodeRecord {
    NodeAddress address{};
    uint8_t     type{0};
    uint8_t     autopilot{0};
    uint8_t     base_mode{0};
    uint32_t    custom_mode{0};
    uint8_t     system_status{0};
    std::chrono::steady_clock::time_point last_heartbeat{};
    LinkState   state{LinkState::Offline};

    [[nodiscard]] constexpr bool is_armed() const noexcept {
        return (base_mode & 0x80) != 0;
    }
};

class HeartbeatService {
public:
    using StateChangeHandler = std::function<void(const NodeRecord&, LinkState)>;
    using HeartbeatEmitter   = std::function<void(uint8_t sysid, uint8_t compid, uint8_t type,
                                                  uint8_t autopilot, uint8_t base_mode,
                                                  uint32_t custom_mode, uint8_t system_status)>;

    HeartbeatService(uint8_t sysid, uint8_t compid, uint8_t type, uint8_t autopilot) noexcept
        : my_sysid_(sysid), my_compid_(compid), my_type_(type), my_autopilot_(autopilot) {}

    void on_state_change(StateChangeHandler handler) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        state_handler_ = std::move(handler);
    }

    void process_incoming_heartbeat(uint8_t sysid, uint8_t compid, uint8_t type,
                                   uint8_t autopilot, uint8_t base_mode,
                                   uint32_t custom_mode, uint8_t system_status) {
        const auto now = std::chrono::steady_clock::now();
        const NodeAddress addr{sysid, compid};

        std::lock_guard<std::mutex> lock(mutex_);
        auto it = nodes_.find(addr);

        if (it == nodes_.end()) {
            NodeRecord record{
                .address = addr,
                .type = type,
                .autopilot = autopilot,
                .base_mode = base_mode,
                .custom_mode = custom_mode,
                .system_status = system_status,
                .last_heartbeat = now,
                .state = LinkState::Online
            };
            auto [new_it, _] = nodes_.emplace(addr, record);
            dispatch_event(new_it->second, LinkState::Online);
        } else {
            auto& record = it->second;
            record.type = type;
            record.autopilot = autopilot;
            record.base_mode = base_mode;
            record.custom_mode = custom_mode;
            record.system_status = system_status;
            record.last_heartbeat = now;

            if (record.state != LinkState::Online) {
                record.state = LinkState::Online;
                dispatch_event(record, LinkState::Online);
            }
        }
    }

    void update_timers(const HeartbeatEmitter& emitter) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Періодична відправка власного серцебиття 1 Гц
        if (now - last_broadcast_ >= std::chrono::milliseconds(1000)) {
            last_broadcast_ = now;
            if (emitter) {
                const uint8_t base_mode = 0x80 | 0x10 | 0x01; // ARMED | STABILIZED | CUSTOM
                const uint32_t custom_mode = 0x00030000;      // PX4 POSCTL
                const uint8_t system_status = 4;               // MAV_STATE_ACTIVE
                emitter(my_sysid_, my_compid_, my_type_, my_autopilot_,
                        base_mode, custom_mode, system_status);
            }
        }

        // 2. Перевірка сторожових таймерів віддалених вузлів
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& [addr, record] : nodes_) {
            const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - record.last_heartbeat);

            if (elapsed >= std::chrono::milliseconds(4500)) {
                if (record.state != LinkState::Lost) {
                    record.state = LinkState::Lost;
                    dispatch_event(record, LinkState::Lost);
                }
            } else if (elapsed >= std::chrono::milliseconds(3000)) {
                if (record.state == LinkState::Online) {
                    record.state = LinkState::Warning;
                    dispatch_event(record, LinkState::Warning);
                }
            }
        }
    }

private:
    void dispatch_event(const NodeRecord& record, LinkState state) const noexcept {
        if (state_handler_) {
            state_handler_(record, state);
        }
    }

    uint8_t my_sysid_{1};
    uint8_t my_compid_{1};
    uint8_t my_type_{2};
    uint8_t my_autopilot_{12};
    std::chrono::steady_clock::time_point last_broadcast_{};

    mutable std::mutex mutex_;
    std::unordered_map<NodeAddress, NodeRecord, NodeAddressHash> nodes_;
    StateChangeHandler state_handler_;
};

} // namespace mavlink
