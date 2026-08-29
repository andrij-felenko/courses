#include "control.hpp"

#include <algorithm>
#include <cmath>

namespace flight {

AttitudeController::Command AttitudeController::update(const ImuSample& imu,
                                                       const std::optional<Setpoint>& incoming,
                                                       bool actuatorsSaturated,
                                                       float dt,
                                                       Micros now) noexcept {
    // 1. Свіжа уставка приймається лише якщо вона не старша за попередню.
    //    Розірване читання Seqlock — не аварія: живемо на останній цілісній копії,
    //    її вік однаково перевірить сторож.
    if (incoming.has_value() &&
        (!lastGood_.has_value() || incoming->stamp >= lastGood_->stamp)) {
        lastGood_ = *incoming;
    }

    const bool stale = !lastGood_.has_value() || (now - lastGood_->stamp) > kSetpointTimeout;

    Quat targetAttitude{};
    Vec3 rateFeedForward{};

    // 2. Сторож застарівання. Задача навігації зависла або зник радіоканал —
    //    регулятор нікого не питає: горизонт і плавне зниження тяги.
    if (stale) {
        thrustCommand_ = std::max(thrustCommand_ - kLandingRampPerSecond * dt, kLandingThrust);
    } else {
        targetAttitude = lastGood_->qTarget;
        rateFeedForward = lastGood_->rateFeedForward;
        thrustCommand_ = lastGood_->thrust;
    }

    // 3. Петля орієнтації — пропорційна, від векторної частини похибки.
    const Quat error = imu.attitude.conjugate() * targetAttitude;
    const float sign = (error.w >= 0.0F) ? 1.0F : -1.0F;   // найкоротший поворот

    const Vec3 rawRateTarget{
        2.0F * sign * error.x * kKpAttitude + rateFeedForward.x,
        2.0F * sign * error.y * kKpAttitude + rateFeedForward.y,
        2.0F * sign * error.z * kKpAttitudeYaw + rateFeedForward.z};

    const Vec3 rateTarget = clampAxes(rawRateTarget,
                                      Vec3{-kMaxRateXY, -kMaxRateXY, -kMaxRateZ},
                                      Vec3{kMaxRateXY, kMaxRateXY, kMaxRateZ});

    // 4. Петля кутових швидкостей: повний PID на кожному такті.
    const Vec3 rateError = rateTarget - imu.gyro;

    if (!actuatorsSaturated) {
        rateIntegral_ += rateError * (kKiRate * dt);
        rateIntegral_ = clampAxes(rateIntegral_,
                                  Vec3{-kMaxRateIntegral, -kMaxRateIntegral, -kMaxRateIntegral},
                                  Vec3{kMaxRateIntegral, kMaxRateIntegral, kMaxRateIntegral});
    }

    // Похідна береться від ВИМІРЮВАННЯ, а не від похибки: сходинка уставки інакше
    // дає нескінченний сплеск. Плюс фільтр першого порядку на 60 Гц — сирий шум
    // гіроскопа в D-ланці розігріває мотори швидше, ніж керує ними.
    const Vec3 rawDerivative = (dt > 1e-6F) ? (previousGyro_ - imu.gyro) * (1.0F / dt) : Vec3{};
    const float rc = 1.0F / (2.0F * kPi * kDerivativeCutoffHz);
    const float alpha = dt / (dt + rc);
    filteredDerivative_ += (rawDerivative - filteredDerivative_) * alpha;
    previousGyro_ = imu.gyro;

    const Vec3 rawTorque = rateError * kKpRate + rateIntegral_ + filteredDerivative_ * kKdRate;

    return Command{
        .torque = clampAxes(rawTorque, Vec3{-1.0F, -1.0F, -1.0F}, Vec3{1.0F, 1.0F, 1.0F}),
        .thrust = std::clamp(thrustCommand_, 0.0F, 1.0F),
        .fallback = stale};
}

}  // namespace flight
