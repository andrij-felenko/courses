#include "vehicle_registry.h"

#include <iostream>

const char* vehicleTypeName(std::uint8_t type) {
    switch (type) {
        case MAV_TYPE_FIXED_WING:   return "літак";
        case MAV_TYPE_QUADROTOR:    return "квадрокоптер";
        case MAV_TYPE_HEXAROTOR:    return "гексакоптер";
        case MAV_TYPE_OCTOROTOR:    return "октокоптер";
        case MAV_TYPE_GROUND_ROVER: return "наземний ровер";
        case MAV_TYPE_VTOL_TILTROTOR: return "конвертоплан";
        default: return "невідома платформа";
    }
}

const char* autopilotName(std::uint8_t autopilot) {
    switch (autopilot) {
        case MAV_AUTOPILOT_ARDUPILOTMEGA: return "ArduPilot";
        case MAV_AUTOPILOT_PX4:           return "PX4";
        case MAV_AUTOPILOT_INVALID:       return "не автопілот";
        default: return "інший стек";
    }
}

const char* systemStateName(std::uint8_t state) {
    switch (state) {
        case MAV_STATE_BOOT:        return "завантаження";
        case MAV_STATE_CALIBRATING: return "калібрування сенсорів";
        case MAV_STATE_STANDBY:     return "очікування зльоту";
        case MAV_STATE_ACTIVE:      return "у польоті";
        case MAV_STATE_CRITICAL:    return "КРИТИЧНИЙ СТАН";
        case MAV_STATE_EMERGENCY:   return "АВАРІЯ";
        default: return "невизначений стан";
    }
}

const char* componentRole(std::uint8_t compid) {
    switch (compid) {
        case MAV_COMP_ID_AUTOPILOT1: return "польотний контролер";
        case 154: return "підвіс камери";
        case 191: return "бортовий комп'ютер";
        case 160: return "трекер антени";
        default:  return "інший вузол шини";
    }
}

bool VehicleRegistry::onHeartbeat(const mavlink_message_t& msg, Clock::time_point now) {
    if (msg.sysid == 255) return false;  // це луна власного серцебиття станції

    mavlink_heartbeat_t hb;
    mavlink_msg_heartbeat_decode(&msg, &hb);

    const std::uint16_t k = key(msg.sysid, msg.compid);
    auto [it, inserted] = comps_.try_emplace(k);
    Component& c = it->second;

    const bool was_silent = !inserted && !c.alive;
    const bool armed_before = c.armed();

    c.sysid = msg.sysid;
    c.compid = msg.compid;
    c.type = hb.type;
    c.autopilot = hb.autopilot;
    c.base_mode = hb.base_mode;
    c.system_status = hb.system_status;
    c.mavlink_version = hb.mavlink_version;
    c.custom_mode = hb.custom_mode;
    c.last_seen = now;
    c.alive = true;

    if (inserted) {
        std::cout << "[1/5] HEARTBEAT: SysID=" << int(c.sysid) << " CompID=" << int(c.compid)
                  << " (" << componentRole(c.compid) << ")\n";
        if (c.isAutopilot()) {
            std::cout << "      платформа: " << vehicleTypeName(c.type)
                      << ", стек: " << autopilotName(c.autopilot)
                      << ", стан: " << systemStateName(c.system_status)
                      << ", мотори: " << (c.armed() ? "ARMED" : "DISARMED")
                      << ", протокол v" << int(c.mavlink_version) << "\n";
        }
    } else if (was_silent) {
        std::cout << "[link] SysID=" << int(c.sysid) << " CompID=" << int(c.compid)
                  << " знову в ефірі\n";
    } else if (armed_before != c.armed()) {
        // Біт 7 base_mode — єдине джерело правди про напругу на регуляторах.
        std::cout << "[!] SysID=" << int(c.sysid)
                  << ": мотори " << (c.armed() ? "ARMED" : "DISARMED") << "\n";
    }

    return c.isAutopilot();
}

void VehicleRegistry::onAutopilotVersion(const mavlink_message_t& msg) {
    mavlink_autopilot_version_t av;
    mavlink_msg_autopilot_version_decode(&msg, &av);

    auto it = comps_.find(key(msg.sysid, msg.compid));
    if (it == comps_.end()) return;
    it->second.capabilities = av.capabilities;

    std::cout << "[1/5] AUTOPILOT_VERSION: маска можливостей 0x" << std::hex << av.capabilities
              << std::dec << "\n";
    const struct { std::uint64_t bit; const char* text; } known[] = {
        {MAV_PROTOCOL_CAPABILITY_MISSION_INT,          "цілочислові координати місії"},
        {MAV_PROTOCOL_CAPABILITY_PARAM_UNION,          "коректні типи параметрів"},
        {MAV_PROTOCOL_CAPABILITY_SET_MESSAGE_INTERVAL, "індивідуальні інтервали потоків (#511)"},
        {MAV_PROTOCOL_CAPABILITY_COMPASS_CALIBRATION,  "бортове калібрування магнітометра"},
    };
    for (const auto& cap : known) {
        std::cout << "      " << ((av.capabilities & cap.bit) ? "+ " : "- ") << cap.text << "\n";
    }
}

bool VehicleRegistry::tick(Clock::time_point now) {
    bool autopilot_silent = false;
    for (auto& [k, c] : comps_) {
        const bool overdue = (now - c.last_seen) > kHeartbeatTimeout;
        if (overdue && c.alive) {
            c.alive = false;
            std::cout << "[!] LINK_LOST: SysID=" << int(c.sysid) << " CompID=" << int(c.compid)
                      << " мовчить понад 3.5 с\n";
        }
        if (c.isAutopilot() && !c.alive) autopilot_silent = true;
    }
    return autopilot_silent;
}

const Component* VehicleRegistry::autopilot() const {
    for (const auto& [k, c] : comps_) {
        if (c.isAutopilot()) return &c;  // map відсортована — беремо борт із найменшим SysID
    }
    return nullptr;
}

bool VehicleRegistry::supports(std::uint64_t capability_bit) const {
    const Component* ap = autopilot();
    return ap != nullptr && (ap->capabilities & capability_bit) != 0;
}
