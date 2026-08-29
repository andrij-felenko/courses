#pragma once

#include <string_view>

#include "arming.hpp"
#include "controllers.hpp"
#include "debounce.hpp"
#include "failsafe.hpp"
#include "guards.hpp"
#include "land_detector.hpp"
#include "mode.hpp"
#include "params.hpp"
#include "reporter.hpp"
#include "telemetry.hpp"

namespace fm {

/* Автомат польотних режимів. Уся мінлива правда про те, який контур зараз
   активний, живе тут і більше ніде: жодного глобального прапорця «ми в
   PosHold», який хтось поставить повз перевірку. */
class FlightModeFsm {
public:
    FlightModeFsm(Params params, Reporter& reporter, const VehicleState& s);

    /* Штатний запит зміни режиму: тумблер пульта, MAV_CMD_DO_SET_MODE,
       перехоплення стіками. Відмова АТОМАРНА: жодне поле автомата й жоден
       контур не зачеплено. */
    GuardResult request(Mode target, Priority priority, const VehicleState& s);

    /* Озброєння — теж перехід під охоронцем, а не перемикання прапорця. */
    GuardResult requestArm(const VehicleState& s);
    GuardResult requestDisarm(const VehicleState& s);

    /* Зовнішня цілевказівка для Guided і навігатора місії. */
    void setPositionTarget(GeoPoint target, float altRelM);

    /* Один такт: детектор польоту, арбітр аварій, перехоплення стіками,
       каскадна деградація, детектор посадки, контури. Викликається з 50–100 Гц. */
    void update(const VehicleState& s);

    [[nodiscard]] Mode                mode() const noexcept { return mode_; }
    [[nodiscard]] Priority            priority() const noexcept { return priority_; }
    [[nodiscard]] float               throttle() const noexcept { return throttle_; }
    [[nodiscard]] bool                inAir() const noexcept { return arming_.inAir(); }
    [[nodiscard]] bool                armed() const noexcept { return arming_.armed(); }
    [[nodiscard]] LandDetector::Phase landPhase() const noexcept { return land_.phase(); }
    [[nodiscard]] const ControllerStack& controllers() const noexcept { return controllers_; }

private:
    void applyTransition(Mode target, Priority priority, const VehicleState& s,
                         std::string_view reason, Severity severity);
    void deny(Mode target, Deny reason, Tone tone);
    [[nodiscard]] bool guardStable(Mode target) const noexcept;

    void handleFailsafe(const VehicleState& s, bool inAir);
    void handlePilotOverride(const VehicleState& s);
    void handleDegradation(const VehicleState& s, bool inAir);

    Params    params_;
    Reporter& reporter_;

    Mode      mode_{Mode::Stabilize};
    Mode      previousMode_{Mode::Stabilize};
    Priority  priority_{Priority::None};
    TimePoint modeSince_{};
    TimePoint lastStep_{};
    bool      primed_{false};

    ArmingState     arming_{};
    LandDetector    land_{};
    ControllerStack controllers_{};

    /* Гістерезис охоронців: щоб автомат не деренчав, коли HDOP гойдається
       навколо порога, дозвіл на підйом угору ієрархією вимагає витримки. */
    Debounce altGuardOk_{false};
    Debounce posGuardOk_{false};

    float throttle_{0.0F};
};

}  // namespace fm
