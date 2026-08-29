#include "failsafe.hpp"

#include <cmath>

#include "guards.hpp"
#include "mission.hpp"

namespace fm {

std::string_view name(Priority priority) noexcept
{
    switch (priority) {
    case Priority::None:          return "none";
    case Priority::Routine:       return "routine";
    case Priority::PilotOverride: return "pilot override";
    case Priority::NavFailsafe:   return "nav failsafe";
    case Priority::Critical:      return "critical failsafe";
    case Priority::Hardware:      return "hardware";
    }
    return "unknown";
}

namespace failsafe {
namespace {

/* Куди повертатися, коли повертатися вже нікуди: RTL за наявності точки старту
   й справної горизонтальної оцінки, інакше — негайна посадка на місці, а без
   вертикальної оцінки — аварійний спуск на фіксованій тязі. Це і є каскадна
   деградація, записана в одну функцію. */
Mode rescueMode(const VehicleState& s, const Params& p)
{
    if (guard::rtl(s, p)) {
        return Mode::Rtl;
    }
    if (guard::altitude(s, p)) {
        return Mode::Land;
    }
    return Mode::EmergencyLand;
}

}  // namespace

bool fenceBreached(const VehicleState& s, const Params& p) noexcept
{
    if (!std::isnan(s.vertical.altitudeRelM) && s.vertical.altitudeRelM > p.fenceAltM) {
        return true;
    }
    if (s.home && s.horizontal.ekfPosValid &&
        geoDistance(*s.home, s.horizontal.position) > p.fenceRadiusM) {
        return true;
    }
    return false;
}

std::optional<Preemption> evaluate(const VehicleState& s, const Params& p,
                                   Mode current, bool inAir)
{
    // Рівень 5: апаратна відсічка. Тумблер уже зняв живлення з регуляторів повз
    // автомат — нам лишається привести свій стан у відповідність.
    if (s.killSwitch) {
        return Preemption{Priority::Hardware, Mode::Terminate, Severity::Emergency,
                          "Failsafe: hardware kill switch"};
    }

    // Рівень 4: повна втрата кутової оцінки. Стабілізувати нічим, спускатися
    // нічим; лишається відсічка (на апаратах із парашутом — його розкриття).
    if (inAir && !guard::attitude(s)) {
        return Preemption{Priority::Critical, Mode::Terminate, Severity::Emergency,
                          "Failsafe: IMU lost, terminate"};
    }

    // Рівень 4: критичний розряд. Місія й оператор блокуються повністю.
    if (s.battery.cellVoltage < p.battCritCellV || s.battery.remaining < p.battCritRemaining) {
        const Mode mode = guard::altitude(s, p) ? Mode::Land : Mode::EmergencyLand;

        return Preemption{Priority::Critical, mode, Severity::Critical,
                          "Failsafe: battery stage 2, landing"};
    }

    // Рівень 4: обидві просторові оцінки розсипалися одночасно.
    if (inAir && !s.vertical.ekfPosValid && !s.horizontal.ekfPosValid) {
        return Preemption{Priority::Critical, Mode::EmergencyLand, Severity::Critical,
                          "Failsafe: EKF crash, emergency land"};
    }

    // Рівень 3 діє лише в повітрі: на землі втрата пульта — це просто вимкнений
    // пульт, і зривати з місця апарат, що стоїть, не можна.
    if (inAir) {
        if (s.age(s.links.lastRcFrame) > p.rcLoss) {
            return Preemption{Priority::NavFailsafe, rescueMode(s, p), Severity::Alert,
                              "Failsafe: RC link lost"};
        }
        if (fenceBreached(s, p)) {
            return Preemption{Priority::NavFailsafe, rescueMode(s, p), Severity::Alert,
                              "Failsafe: geofence breach"};
        }
        if (current == Mode::Guided && s.age(s.links.lastGcsHeartbeat) > p.gcsLoss) {
            // Guided без станції — політ за протермінованою точкою.
            return Preemption{Priority::NavFailsafe, rescueMode(s, p), Severity::Alert,
                              "Failsafe: GCS link lost"};
        }
        if (s.battery.cellVoltage < p.battLowCellV || s.battery.remaining < p.battLowRemaining) {
            return Preemption{Priority::NavFailsafe, rescueMode(s, p), Severity::Warning,
                              "Failsafe: battery stage 1, RTL"};
        }
    }

    return std::nullopt;
}

}  // namespace failsafe
}  // namespace fm
