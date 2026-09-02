#include "status.hpp"

#include <bit>
#include <format>
#include <utility>

namespace autopilot::failsafe {

std::string_view toString(Fault f) noexcept
{
    switch (f) {
    case Fault::RcLost:       return "RC_LOST";
    case Fault::GcsLost:      return "GCS_LOST";
    case Fault::GnssHdop:     return "GNSS_HDOP";
    case Fault::GnssLost:     return "GNSS_LOST";
    case Fault::EkfDiverged:  return "EKF_DIVERGED";
    case Fault::BattLow:      return "BATT_LOW";
    case Fault::BattCrit:     return "BATT_CRIT";
    case Fault::FenceRadius:  return "FENCE_RADIUS";
    case Fault::FenceAlt:     return "FENCE_ALT";
    case Fault::EscFail:      return "ESC_FAIL";
    case Fault::AttitudeLost: return "ATTITUDE_LOST";
    case Fault::None:         return "CLEAN";
    }
    return "?";
}

std::string_view toString(Action a) noexcept
{
    switch (a) {
    case Action::None:      return "FS_ACTION_NONE";
    case Action::Warn:      return "FS_ACTION_WARN";
    case Action::AltHold:   return "FS_ACTION_ALTHOLD";
    case Action::Rtl:       return "FS_ACTION_RTL";
    case Action::Land:      return "FS_ACTION_LAND";
    case Action::Terminate: return "FS_ACTION_TERMINATE";
    }
    return "FS_ACTION_?";
}

std::string_view toString(Arbiter a) noexcept
{
    switch (a) {
    case Arbiter::None:       return "none";
    case Arbiter::RcLink:     return "rc_link";
    case Arbiter::Gcs:        return "gcs_link";
    case Arbiter::Navigation: return "navigation";
    case Arbiter::Battery:    return "battery";
    case Arbiter::Geofence:   return "geofence";
    case Arbiter::Propulsion: return "propulsion";
    }
    return "?";
}

std::string_view toString(Severity s) noexcept
{
    switch (s) {
    case Severity::Emergency: return "EMERGENCY";
    case Severity::Alert:     return "ALERT";
    case Severity::Critical:  return "CRITICAL";
    case Severity::Error:     return "ERROR";
    case Severity::Warning:   return "WARNING";
    case Severity::Notice:    return "NOTICE";
    case Severity::Info:      return "INFO";
    }
    return "?";
}

Decision ruleFor(Fault fault, Fault active, const ParamBlock& p) noexcept
{
    switch (fault) {
    case Fault::RcLost:
        switch (p.getInt(ParamId::ThrEnable)) {
        case 0:  return { Action::None, Arbiter::RcLink };
        case 1:  return { Action::Rtl,  Arbiter::RcLink };
        case 2:  return { Action::Warn, Arbiter::RcLink };  // продовжити місію
        default: // 3 — вимкнено, поки живий канал телеметрії
            return { has(active, Fault::GcsLost) ? Action::Rtl : Action::Warn, Arbiter::RcLink };
        }

    case Fault::GcsLost:
        switch (p.getInt(ParamId::GcsEnable)) {
        case 0:  return { Action::None, Arbiter::Gcs };
        case 1:  return { Action::Rtl,  Arbiter::Gcs };
        default: return { Action::Land, Arbiter::Gcs };
        }

    case Fault::GnssHdop:  // якість погіршилась, фіксацію ще не втрачено
        return { Action::Warn, Arbiter::Navigation };

    case Fault::GnssLost:
    case Fault::EkfDiverged:  // безсупутниковий режим утримання висоти
        return { Action::AltHold, Arbiter::Navigation };

    case Fault::BattLow:
        switch (p.getInt(ParamId::BattAct)) {
        case 1:  return { Action::Warn, Arbiter::Battery };
        case 3:  return { Action::Land, Arbiter::Battery };
        default: return { Action::Rtl,  Arbiter::Battery };  // 2 — RTL, 4 — SmartRTL
        }

    case Fault::BattCrit:  // конфігурацією не скасовується
        return { Action::Land, Arbiter::Battery };

    case Fault::FenceRadius:
    case Fault::FenceAlt:
        if (p.getInt(ParamId::FenceEnable) == 0)
            return { Action::None, Arbiter::Geofence };
        switch (p.getInt(ParamId::FenceAct)) {
        case 2:  return { Action::Land, Arbiter::Geofence };
        case 3:  return { Action::AltHold, Arbiter::Geofence };  // зависання Loiter/Brake
        default: return { Action::Rtl,  Arbiter::Geofence };
        }

    case Fault::EscFail:  // із втратою променя тримаємось лише до землі
        return { Action::Land, Arbiter::Propulsion };

    case Fault::AttitudeLost:  // без горизонту керований політ неможливий
        return { Action::Terminate, Arbiter::Navigation };

    case Fault::None:
        break;
    }
    return {};
}

Action degrade(Action action, Fault active) noexcept
{
    // Повернення додому потребує позиції: без GNSS і зі зруйнованим фільтром
    // замість RTL сідаємо там, де стоїмо.
    if (action == Action::Rtl && (has(active, Fault::GnssLost) || has(active, Fault::EkfDiverged)))
        action = Action::Land;

    // Без оцінки орієнтації не виконується навіть посадка.
    if (has(active, Fault::AttitudeLost) && action >= Action::AltHold)
        action = Action::Terminate;

    return action;
}

Decision decide(Fault active, const ParamBlock& p) noexcept
{
    Decision best{};

    for (Fault f : kAllFaults) {
        if (!has(active, f))
            continue;
        const Decision d = ruleFor(f, active, p);
        if (d.action > best.action)  // суворіша перекриває, за рівних виграє перша
            best = d;
    }

    best.action = degrade(best.action, active);
    return best;
}

Severity severityOf(Fault fault) noexcept
{
    switch (fault) {
    case Fault::AttitudeLost:
        return Severity::Emergency;
    case Fault::BattCrit:
    case Fault::FenceRadius:
    case Fault::FenceAlt:
        return Severity::Alert;
    case Fault::RcLost:
    case Fault::GcsLost:
    case Fault::GnssLost:
    case Fault::EkfDiverged:
    case Fault::EscFail:
        return Severity::Critical;
    case Fault::BattLow:
    case Fault::GnssHdop:
        return Severity::Warning;
    default:
        return Severity::Info;
    }
}

namespace {

void putU16(std::byte* p, std::uint16_t v) noexcept
{
    p[0] = static_cast<std::byte>(v);
    p[1] = static_cast<std::byte>(v >> 8);
}
void putU32(std::byte* p, std::uint32_t v) noexcept
{
    for (int i = 0; i < 4; ++i)
        p[i] = static_cast<std::byte>(v >> (8 * i));
}
void putU64(std::byte* p, std::uint64_t v) noexcept
{
    putU32(p, static_cast<std::uint32_t>(v));
    putU32(p + 4, static_cast<std::uint32_t>(v >> 32));
}
std::uint16_t getU16(const std::byte* p) noexcept
{
    return static_cast<std::uint16_t>(std::to_integer<unsigned>(p[0]) |
                                      (std::to_integer<unsigned>(p[1]) << 8));
}
std::uint32_t getU32(const std::byte* p) noexcept
{
    std::uint32_t v = 0;
    for (int i = 0; i < 4; ++i)
        v |= static_cast<std::uint32_t>(std::to_integer<unsigned>(p[i])) << (8 * i);
    return v;
}
std::uint64_t getU64(const std::byte* p) noexcept
{
    return getU32(p) | (static_cast<std::uint64_t>(getU32(p + 4)) << 32);
}

constexpr std::uint32_t kKnownFaultBits = []{
    std::uint32_t m = 0;
    for (Fault f : kAllFaults)
        m |= std::to_underlying(f);
    return m;
}();

} // namespace

std::array<std::byte, kFrameSize> pack(const TelemetryFrame& t) noexcept
{
    std::array<std::byte, kFrameSize> buf{};

    putU64(buf.data() + 0, t.timestamp_us);
    putU32(buf.data() + 8, std::to_underlying(t.active_faults));
    buf[12] = static_cast<std::byte>(std::to_underlying(t.active_action));
    buf[13] = static_cast<std::byte>(std::to_underlying(t.arbiter));
    putU16(buf.data() + 14, t.rc_valid_frames_sec);
    putU32(buf.data() + 16, std::bit_cast<std::uint32_t>(t.gnss_hdop));
    putU32(buf.data() + 20, std::bit_cast<std::uint32_t>(t.batt_cell_min_v));
    putU32(buf.data() + 24, std::bit_cast<std::uint32_t>(t.distance_to_fence_m));
    return buf;
}

std::expected<TelemetryFrame, FrameError> unpack(std::span<const std::byte> raw) noexcept
{
    if (raw.size() < kFrameSize)
        return std::unexpected(FrameError::TooShort);

    const std::uint32_t mask = getU32(raw.data() + 8);
    const std::uint8_t  act  = std::to_integer<std::uint8_t>(raw[12]);
    // Кадр міг прийти з новішої прошивки з невідомими нам бітами.
    if ((mask & ~kKnownFaultBits) != 0 || act > std::to_underlying(Action::Terminate))
        return std::unexpected(FrameError::UnknownBits);

    TelemetryFrame t{};
    t.timestamp_us        = getU64(raw.data() + 0);
    t.active_faults       = static_cast<Fault>(mask);
    t.active_action       = static_cast<Action>(act);
    t.arbiter             = static_cast<Arbiter>(std::to_integer<std::uint8_t>(raw[13]));
    t.rc_valid_frames_sec = getU16(raw.data() + 14);
    t.gnss_hdop           = std::bit_cast<float>(getU32(raw.data() + 16));
    t.batt_cell_min_v     = std::bit_cast<float>(getU32(raw.data() + 20));
    t.distance_to_fence_m = std::bit_cast<float>(getU32(raw.data() + 24));
    return t;
}

Notice statusText(Fault fault, Fault active, const ParamBlock& p, const TelemetryFrame& t)
{
    const auto act = toString(degrade(ruleFor(fault, active, p).action, active));

    switch (fault) {
    case Fault::RcLost:
        return { severityOf(fault),
                 std::format("RC link lost > {:.1f}s -> {}", p.get(ParamId::RcTimeout), act) };
    case Fault::GcsLost:
        return { severityOf(fault),
                 std::format("GCS heartbeat timeout {:.1f}s -> {}", p.get(ParamId::GcsTimeout), act) };
    case Fault::GnssHdop:
        return { severityOf(fault),
                 std::format("GNSS HDOP {:.2f} > {:.2f}, position degraded",
                             t.gnss_hdop, p.get(ParamId::GnssHdopMax)) };
    case Fault::GnssLost:
        return { severityOf(fault),
                 std::format("GNSS fix lost for {:.1f}s (HDOP {:.2f}) -> {}",
                             p.get(ParamId::GnssTimeout), t.gnss_hdop, act) };
    case Fault::EkfDiverged:
        return { severityOf(fault),
                 std::format("EKF innovation ratio above {:.2f} -> {}",
                             p.get(ParamId::EkfThresh), act) };
    case Fault::BattLow:
        return { severityOf(fault),
                 std::format("Battery low {:.2f}V/cell < {:.2f}V -> {}",
                             t.batt_cell_min_v, p.get(ParamId::BattLowV), act) };
    case Fault::BattCrit:
        return { severityOf(fault),
                 std::format("Battery critical {:.2f}V/cell < {:.2f}V -> {}",
                             t.batt_cell_min_v, p.get(ParamId::BattCritV), act) };
    case Fault::FenceRadius:
        return { severityOf(fault),
                 std::format("Fence radius {:.0f}m breached ({:.1f}m to boundary) -> {}",
                             p.get(ParamId::FenceRadius), t.distance_to_fence_m, act) };
    case Fault::FenceAlt:
        return { severityOf(fault),
                 std::format("Fence ceiling {:.0f}m breached -> {}",
                             p.get(ParamId::FenceAltMax), act) };
    case Fault::EscFail:
        return { severityOf(fault), std::format("ESC/motor failure -> {}", act) };
    case Fault::AttitudeLost:
        return { severityOf(fault), std::format("Attitude estimate lost -> {}", act) };
    case Fault::None:
        break;
    }
    return { Severity::Info, "no active fault" };
}

Notice recoveryNotice(const ParamBlock& p)
{
    return { Severity::Info,
             std::format("RC link recovered, manual control restored after {:.1f}s",
                         p.get(ParamId::RcRecover)) };
}

} // namespace autopilot::failsafe
