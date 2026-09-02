#pragma once
// Фаза 1: хто на іншому кінці лінії. Розбір HEARTBEAT, облік компонентів апарата
// й сторожовий таймер присутності.
#include <map>

#include "serial_link.h"

struct Component {
    std::uint8_t sysid = 0;
    std::uint8_t compid = 0;
    std::uint8_t type = 0;            // MAV_TYPE: квадрокоптер, літак, ровер…
    std::uint8_t autopilot = 0;       // MAV_AUTOPILOT: ArduPilot чи PX4
    std::uint8_t base_mode = 0;
    std::uint8_t system_status = 0;   // MAV_STATE
    std::uint8_t mavlink_version = 0;
    std::uint32_t custom_mode = 0;    // код польотного режиму, семантика залежить від стека
    std::uint64_t capabilities = 0;   // маска з AUTOPILOT_VERSION
    Clock::time_point last_seen{};
    bool alive = true;

    bool armed() const { return (base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0; }
    bool isAutopilot() const { return compid == MAV_COMP_ID_AUTOPILOT1; }
};

const char* vehicleTypeName(std::uint8_t type);
const char* autopilotName(std::uint8_t autopilot);
const char* systemStateName(std::uint8_t state);
const char* componentRole(std::uint8_t compid);

class VehicleRegistry {
public:
    // Три пропущені серцебиття поспіль (1 Гц) — зв'язок вважається втраченим.
    static constexpr auto kHeartbeatTimeout = std::chrono::milliseconds(3500);

    // Повертає true, якщо це серцебиття від головного автопілота.
    bool onHeartbeat(const mavlink_message_t& msg, Clock::time_point now);
    void onAutopilotVersion(const mavlink_message_t& msg);

    // Позначає замовклі компоненти; true — головний автопілот мовчить.
    bool tick(Clock::time_point now);

    const Component* autopilot() const;
    bool supports(std::uint64_t capability_bit) const;

private:
    static std::uint16_t key(std::uint8_t sysid, std::uint8_t compid) {
        return static_cast<std::uint16_t>(sysid) << 8 | compid;
    }
    std::map<std::uint16_t, Component> comps_;
};
