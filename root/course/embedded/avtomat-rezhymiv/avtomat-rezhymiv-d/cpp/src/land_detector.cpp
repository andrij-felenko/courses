#include "land_detector.hpp"

#include <cmath>

namespace fm {

bool LandDetector::contactSignature(const VehicleState& s, const Params& p) noexcept
{
    if (std::isnan(s.vertical.velocityMs) || std::isnan(s.imu.accelZVariance)) {
        return false;
    }

    const float hover = (s.propulsion.hoverThrottle > 0.05F) ? s.propulsion.hoverThrottle : 0.5F;

    // Жодної ознаки поодинці не досить: зупинка зниження буває й у висінні,
    // мала тяга — у падінні, тиха вертикаль — у вільному спуску над водою.
    const bool vzStopped  = std::fabs(s.vertical.velocityMs) < p.landVzEpsilon;
    const bool thrustLow  = s.propulsion.motorOutput < (p.landThrMin * hover);
    const bool quietAccel = s.imu.accelZVariance < p.landAccelVarMax;

    return vzStopped && thrustLow && quietAccel;
}

void LandDetector::reset() noexcept
{
    phase_ = Phase::Idle;
    contact_.reset(false);
}

void LandDetector::update(const VehicleState& s, const Params& p, bool landingMode, bool inAir)
{
    if (!landingMode || !s.propulsion.armed) {
        reset();
        return;
    }

    if (!inAir) {
        // Режим посадки на землі — апарат уже стоїть (наприклад, Land увімкнули
        // після невдалого зльоту). Гасити мотори можна одразу.
        phase_       = Phase::Landed;
        disarmEvent_ = true;
        return;
    }

    // Витримка потрібна лише на вхід: варто ознакам розсипатися — контакт
    // знімається того ж такту, бо апарат, найімовірніше, відскочив від землі.
    const bool stable = contact_.update(contactSignature(s, p), s.now, p.landContact, Millis{0});

    if (!stable) {
        phase_ = Phase::Descent;
        return;
    }

    if (phase_ != Phase::GroundContact && phase_ != Phase::Landed) {
        phase_        = Phase::GroundContact;
        contactSince_ = s.now;
        return;
    }

    if (phase_ == Phase::GroundContact && (s.now - contactSince_) >= p.landConfirm) {
        phase_       = Phase::Landed;
        disarmEvent_ = true;
    }
}

bool LandDetector::consumeDisarmEvent() noexcept
{
    const bool pending = disarmEvent_;

    disarmEvent_ = false;
    return pending;
}

float LandDetector::targetClimbRate(const Params& p) const noexcept
{
    return (phase_ == Phase::Descent) ? -p.landSpeed : 0.0F;
}

std::string_view LandDetector::name(Phase phase) noexcept
{
    switch (phase) {
    case Phase::Idle:          return "idle";
    case Phase::Descent:       return "descent";
    case Phase::GroundContact: return "ground contact";
    case Phase::Landed:        return "landed";
    }
    return "unknown";
}

}  // namespace fm
