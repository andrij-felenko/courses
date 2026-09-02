#include "telemetry.hpp"

#include <algorithm>
#include <cstdio>
#include <utility>

namespace fc {
namespace {

// Копія без вимоги завершального нуля: поле фіксованої довжини, як у MAVLink.
template <std::size_t N>
void fill_field(std::array<char, N>& dst, std::string_view src) {
    dst.fill('\0');
    std::copy_n(src.begin(), std::min(src.size(), N), dst.begin());
}

std::pair<std::uint8_t, std::string_view> describe(Event e) {
    switch (e) {
        case Event::OverrideBegin:
            return {kSeverityWarning, "Pilot takeover: stick deflection > threshold"};
        case Event::ManualFull:
            return {kSeverityWarning, "Manual override: full pilot authority"};
        case Event::HandbackArmed:
            return {kSeverityInfo, "Sticks centered: handback timer running"};
        case Event::AutoResumed:
            return {kSeverityInfo, "Autopilot resumed from current position"};
        case Event::ThrottleEngaged:
            return {kSeverityInfo, "Throttle lever moved: speed loop to pilot"};
        case Event::RcLost:
            return {kSeverityCritical, "RC lost during override: failsafe RTL"};
        case Event::FenceReclaim:
            return {kSeverityCritical, "Geofence: autopilot reclaims control"};
    }
    return {kSeverityInfo, "Takeover: unknown event"};
}

std::string_view severity_name(std::uint8_t sev) {
    if (sev == kSeverityCritical) return "CRITICAL";
    if (sev == kSeverityWarning) return "WARNING";
    return "INFO";
}

// У прошивці ці три функції складають повідомлення пакувальниками MAVLink
// і кладуть їх у чергу телеметрії. Тут — друк, щоб потік було видно.
void send(const StatusText& m, Seconds now) {
    std::printf("      [%6.2f] STATUSTEXT %-8s %.50s\n", static_cast<double>(now.count()),
                severity_name(m.severity).data(), m.text.data());
}

void send(const Heartbeat& m, Seconds now) {
    std::printf("      [%6.2f] HEARTBEAT  base_mode=0x%02X custom_mode=%u\n",
                static_cast<double>(now.count()), m.base_mode, m.custom_mode);
}

void send(const NamedValueFloat& m) {
    std::printf("      [%6.2f] NAMED_VALUE_FLOAT %.10s = %.2f\n",
                static_cast<double>(m.time_boot_ms) / 1000.0, m.name.data(),
                static_cast<double>(m.value));
}

std::uint8_t base_mode_of(Phase p) {
    std::uint8_t flags = kModeFlagSafetyArmed | kModeFlagCustomModeEnabled;
    flags |= (p == Phase::AutoNav) ? kModeFlagAutoEnabled
                                   : (kModeFlagManualInputEnabled | kModeFlagStabilizeEnabled);
    return flags;
}

} // namespace

void Telemetry::report(std::span<const Event> events, Seconds now) {
    for (Event e : events) {
        const auto [severity, text] = describe(e);
        StatusText msg;
        msg.severity = severity;
        fill_field(msg.text, text);
        send(msg, now);
    }
}

void Telemetry::stream(const Status& st, Seconds now) {
    if (!started_) {
        started_ = true;
        last_heartbeat_ = now;
        last_named_ = now;
    }

    if (now - last_heartbeat_ >= kHeartbeatPeriod) {
        last_heartbeat_ = now;
        // Стан автомата їде в custom_mode. Нумерація наша: у ArduPlane своя
        // (MANUAL=0, FBWA=5, AUTO=10, RTL=11), і плутати їх не можна.
        send(Heartbeat{base_mode_of(st.phase),
                       static_cast<std::uint32_t>(st.phase)},
             now);
    }

    // Коефіцієнт змішування окремого поля в NAV_CONTROLLER_OUTPUT не має,
    // тому α йде named-значенням — його наземна станція кладе на графік.
    if (now - last_named_ >= kNamedValuePeriod) {
        last_named_ = now;
        if (st.alpha.attitude > 0.0f || st.alpha.throttle > 0.0f) {
            NamedValueFloat nv;
            fill_field(nv.name, "BLEND_A");
            nv.value = st.alpha.attitude;
            nv.time_boot_ms = static_cast<std::uint32_t>(now.count() * 1000.0f);
            send(nv);
        }
    }
}

} // namespace fc
