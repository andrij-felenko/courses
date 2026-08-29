#include "arming.hpp"

#include <cmath>

namespace fm {

bool ArmingState::inAirSignature(const VehicleState& s, const Params& p) const noexcept
{
    if (!armed_) {
        return false;
    }

    const bool motorsSpun = s.propulsion.motorOutput > p.inAirMotorMin;
    const bool moving     = s.imu.accelZVariance > p.inAirAccelVar ||
                            std::fabs(s.vertical.velocityMs) > 0.5F;

    if (std::isnan(s.vertical.altitudeRelM)) {
        // Висоти немає — лишаються силові й інерціальні ознаки.
        return motorsSpun && moving;
    }
    return s.vertical.altitudeRelM > p.inAirAltM || (motorsSpun && moving);
}

bool ArmingState::update(const VehicleState& s, const Params& p)
{
    // Озброєння — стан САМОГО автомата, а не поле телеметрії: інакше наступний
    // такт скасував би щойно виконане роззброєння, бо драйвер ще не встиг
    // оновити свій прапорець.
    if (killLatched_) {
        armed_ = false;
    }
    // Вхід у політ визнаємо швидко (щоб заборона роззброєння встигла набути
    // чинності на відриві), вихід — повільно: короткий підскок не є посадкою.
    return inAir_.update(inAirSignature(s, p), s.now, p.inAirRise, p.inAirFall);
}

GuardResult ArmingState::requestArm(const VehicleState& s)
{
    if (killLatched_) {
        // Після апаратної відсічки озброєння дозволене лише повним циклом
        // живлення: інакше причина відсічки поїхала б у політ разом з нами.
        return std::unexpected(Deny::FailsafeLock);
    }
    if (inAir()) {
        return std::unexpected(Deny::InAir);
    }
    if (auto ok = guard::attitude(s); !ok) {
        return ok;
    }
    armed_ = true;
    return {};
}

GuardResult ArmingState::requestDisarm()
{
    if (!armed_) {
        return {};   // уже роззброєні — запит нічого не змінює
    }
    if (inAir()) {
        // Комбінація стіків у польоті ігнорується завжди. Пілот, який справді
        // хоче зупинити мотори в повітрі, має виділений апаратний тумблер.
        return std::unexpected(Deny::InAir);
    }
    armed_ = false;
    return {};
}

void ArmingState::disarmAfterLanding() noexcept
{
    armed_ = false;
    notifyLanded();
}

void ArmingState::kill() noexcept
{
    killLatched_ = true;
    armed_       = false;
}

}  // namespace fm
