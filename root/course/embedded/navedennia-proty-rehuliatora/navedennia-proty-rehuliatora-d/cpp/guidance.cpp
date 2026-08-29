#include "guidance.hpp"

#include <algorithm>
#include <cmath>

namespace flight {
namespace {

// Обмежувач кута нахилу: вісь тяги не відхиляється від вертикалі далі maxTilt.
// Саме тут наведення отримує відмову виконувати свій наказ — заради підйомної сили.
[[nodiscard]] Vec3 limitTilt(Vec3 zb, float maxTilt) noexcept {
    const float cosMax = std::cos(maxTilt);
    if (zb.z >= cosMax) {
        return zb;
    }

    const float xy = std::sqrt(zb.x * zb.x + zb.y * zb.y);
    if (xy < 1e-4F) {
        // Вироджений випадок: потрібна сила спрямована ВНИЗ (наведення просить
        // прискорення до землі, більше за g). Мультиротор так не вміє —
        // тримаємо горизонт і віддаємо мінімальну тягу.
        return Vec3{0.0F, 0.0F, 1.0F};
    }

    const float k = std::sin(maxTilt) / xy;
    return Vec3{zb.x * k, zb.y * k, cosMax};
}

// Ортонормований тригранник із бажаної осі тяги та курсу.
[[nodiscard]] Quat basisToQuat(const Vec3& zb, float yaw) noexcept {
    Vec3 xc{std::cos(yaw), std::sin(yaw), 0.0F};   // напрямок носа в NED
    Vec3 yb = cross(zb, xc);
    float yn = yb.norm();

    if (yn < 1e-4F) {
        // Ніс збігся з віссю тяги — беремо перпендикулярний опорний напрямок,
        // інакше базис вироджується в пряму.
        xc = Vec3{-std::sin(yaw), std::cos(yaw), 0.0F};
        yb = cross(zb, xc);
        yn = yb.norm();
        if (yn < 1e-4F) {
            return Quat{};
        }
    }

    yb = yb * (1.0F / yn);
    return Quat::fromBasis(cross(yb, zb), yb, zb);
}

}  // namespace

Setpoint Guidance::step(const NavState& nav,
                        const Vec3& targetPosition,
                        float yawSetpoint,
                        float dt,
                        bool actuatorsSaturated,
                        Micros now) noexcept {
    // 1. Позиція -> швидкість. Ріжемо ДОВЖИНУ вектора: інакше по діагоналі
    //    апарат летів би в 1.41 раза швидше за дозволене.
    const Vec3 posError = targetPosition - nav.position;
    const Vec3 velSetpoint = (posError * kKpPosition).clampedNorm(kMaxSpeed);

    // 2. Швидкість -> прискорення, PI з анти-вінд-апом.
    const Vec3 velError = velSetpoint - nav.velocity;

    if (!actuatorsSaturated) {
        velIntegral_ += velError * (kKiVelocity * dt);
        velIntegral_ = velIntegral_.clampedNorm(kMaxIntegral);
    }
    // Інакше інтегратор ЗАМОРОЖЕНО: мотори вже на стелі, накопичувати похибку
    // нема куди — після стихання вітру апарат перелетів би ціль на десятки метрів.

    Vec3 accel = velError * kKpVelocity + velIntegral_;
    const Vec3 accelXY = Vec3{accel.x, accel.y, 0.0F}.clampedNorm(kMaxAccelXY);
    accel = Vec3{accelXY.x, accelXY.y, std::clamp(accel.z, -kMaxAccelZ, kMaxAccelZ)};

    // 3. Питома сила f = a - g. У NED вісь Z вниз, тож у висінні
    //    f = (0, 0, -9.81): сила спрямована вгору.
    const Vec3 force{accel.x, accel.y, accel.z - kGravity};

    // 4. Бажана вісь Z корпуса (вниз крізь дно): z_body = -f / ||f||.
    const Vec3 zb = limitTilt((-force).normalizedOr(Vec3{0.0F, 0.0F, 1.0F}), kMaxTilt);

    // 5–6. Тригранник -> кватерніон -> обмежувач швидкості зміни уставки.
    // Перемикання вейпойнта під 90 градусів дає сходинку; без різання вона
    // б'є в D-ланку регулятора орієнтації одним тактом.
    const Quat rawTarget = basisToQuat(zb, yawSetpoint);

    Setpoint sp{};
    if (!previousTarget_.has_value()) {
        sp.qTarget = rawTarget;
        sp.rateFeedForward = Vec3{};
    } else {
        const SlewStep step = slewLimited(*previousTarget_, rawTarget, kMaxSlewRate * dt);
        sp.qTarget = step.target;
        // Фактичний поворот уставки за такт — це і є прямий зв'язок за швидкістю:
        // регулятор дізнається, куди уставка їде, не чекаючи появи похибки.
        sp.rateFeedForward = (dt > 1e-6F) ? step.rotation * (1.0F / dt) : Vec3{};
    }
    previousTarget_ = sp.qTarget;

    // 7. Колективна тяга. Ділення на zb.z — компенсація 1/cos(theta): при нахилі
    //    30 гр. вертикальна складова падає до 0.866, і рівно на стільки ж
    //    підіймається уставка газу. Поки tilt-ліміт мовчить, це тотожно ||f||.
    const float forceUp = std::max(-force.z, 0.5F);   // від'ємної тяги гвинт не дає
    sp.thrust = std::clamp(forceUp / zb.z / kMaxThrustAccel, kMinThrust, 1.0F);
    sp.stamp = now;
    return sp;
}

}  // namespace flight
