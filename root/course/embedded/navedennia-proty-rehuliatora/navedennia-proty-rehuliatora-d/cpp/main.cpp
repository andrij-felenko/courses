// ============================================================================
// Демонстрація розділення наведення й регулювання на імітаторі мультиротора.
//
// Швидкий домен  — 1000 Гц: AttitudeController + мікшер + фізика.
// Повільний домен —   50 Гц: Guidance.
// Обмін — тільки через Seqlock-скриньку та два атомарні біти назад.
//
// Сценарій: висіння на 5 м; бічний порив; низхідний потік із насиченням моторів;
// на 4-й секунді задача навігації "зависає" — спрацьовує сторож уставки.
//
// Збірка: c++ -O2 -std=c++20 *.cpp -o guidance_demo
// ============================================================================

#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>

#include "control.hpp"
#include "geometry.hpp"
#include "guidance.hpp"
#include "mixer.hpp"
#include "setpoint.hpp"

namespace {

using namespace flight;

constexpr float kDtFast = 0.001F;      // 1000 Гц
constexpr int kGuidanceDivider = 20;   // 50 Гц
constexpr float kSimSeconds = 6.5F;

// Груба модель рами: нормовані тяга й момент -> прискорення.
constexpr float kMaxThrustAccel = 2.0F * kGravity;
constexpr float kMaxAngularAccelXY = 600.0F;   // рад/с^2 на одиничний момент
constexpr float kMaxAngularAccelZ = 120.0F;
constexpr float kLinearDrag = 0.25F;           // 1/с
constexpr float kAngularDrag = 0.60F;

struct Vehicle {
    Vec3 position{0.0F, 0.0F, -5.0F};   // NED: -5 означає висоту 5 м
    Vec3 velocity{};
    Quat attitude{};
    Vec3 rates{};

    void step(const Wrench& wrench, const Vec3& disturbAccel, const Vec3& disturbAlpha, float dt) noexcept {
        // Трансляція: тяга вздовж -Z корпуса, гравітація вниз, лінійний опір.
        Vec3 accel = attitude.rotate(Vec3{0.0F, 0.0F, -wrench.thrust * kMaxThrustAccel});
        accel += Vec3{0.0F, 0.0F, kGravity};
        accel += velocity * -kLinearDrag;
        accel += disturbAccel;

        velocity += accel * dt;
        position += velocity * dt;

        // Обертання: момент -> кутове прискорення плюс аеродинамічний демпфер.
        Vec3 alpha{wrench.torque.x * kMaxAngularAccelXY,
                   wrench.torque.y * kMaxAngularAccelXY,
                   wrench.torque.z * kMaxAngularAccelZ};
        alpha += rates * -kAngularDrag;
        alpha += disturbAlpha;

        rates += alpha * dt;

        // Інтегрування кватерніона: q += 0.5 * q * (0, omega) * dt.
        const Quat dq = attitude * Quat{0.0F, rates.x, rates.y, rates.z};
        attitude = Quat{attitude.w + 0.5F * dq.w * dt,
                        attitude.x + 0.5F * dq.x * dt,
                        attitude.y + 0.5F * dq.y * dt,
                        attitude.z + 0.5F * dq.z * dt}
                       .normalized();
    }

    // Кут між віссю тяги й вертикаллю — те, що обмежує tilt limiter.
    [[nodiscard]] float tiltDegrees() const noexcept {
        const Vec3 zb = attitude.rotate(Vec3{0.0F, 0.0F, 1.0F});
        return std::acos(std::clamp(zb.z, -1.0F, 1.0F)) * 180.0F / kPi;
    }
};

}  // namespace

int main() {
    SetpointMailbox mailbox;
    ControlFeedback feedback;
    Guidance guidance;
    AttitudeController controller;
    Vehicle vehicle;

    const Vec3 target{0.0F, 0.0F, -5.0F};   // висіння над точкою старту
    constexpr float kYawSetpoint = 0.0F;

    Micros now{0};
    bool navFrozen = false;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "  t, с | пн, м | сх, м | вис, м | нахил | газ | режим  | насич\n";
    std::cout << "-------+-------+-------+--------+-------+-----+--------+------\n";

    const long totalTicks = static_cast<long>(kSimSeconds / kDtFast);

    for (long tick = 0; tick <= totalTicks; ++tick) {
        const float t = static_cast<float>(tick) * kDtFast;

        // --- Збурення середовища ------------------------------------------
        Vec3 disturbAccel{};
        Vec3 disturbAlpha{};

        if (t >= 1.0F && t < 1.6F) {
            disturbAccel.y = 8.0F;                 // бічний порив на схід
            if (t < 1.05F) {
                disturbAlpha.x = 45.0F;            // удар по рамі перекидає її
            }
        }
        if (t >= 2.5F && t < 3.5F) {
            disturbAccel.z = 7.0F;                 // низхідний потік: газ біля стелі
            disturbAccel.x = -4.0F;
        }

        // --- Повільний домен: наведення, 50 Гц -----------------------------
        if (tick % kGuidanceDivider == 0) {
            if (t >= 4.0F) {
                // Імітуємо зависання задачі навігації: уставок більше немає.
                if (!navFrozen) {
                    std::cout << "       |  <<< задача наведення зупинилась (t = " << t << " с) >>>\n";
                    navFrozen = true;
                }
            } else {
                const Guidance::NavState nav{
                    .position = vehicle.position,
                    .velocity = vehicle.velocity,
                    .yaw = kYawSetpoint};

                mailbox.publish(guidance.step(nav, target, kYawSetpoint,
                                              kDtFast * kGuidanceDivider,
                                              feedback.saturated(), now));
            }
        }

        // --- Швидкий домен: регулятор + мікшер, 1000 Гц --------------------
        const AttitudeController::ImuSample imu{.attitude = vehicle.attitude,
                                                .gyro = vehicle.rates};

        const auto command = controller.update(imu, mailbox.consume(),
                                               feedback.saturated(), kDtFast, now);
        const MotorOutputs motors = mixQuadX(command.torque, command.thrust);

        // Насичення актуаторів — назад угору: його читають і петля кутових
        // швидкостей регулятора, і петля позиції наведення.
        feedback.setSaturated(motors.saturated);
        feedback.setFallback(command.fallback);

        vehicle.step(motorsToWrench(std::span<const float, kMotorCount>{motors.motors}),
                     disturbAccel, disturbAlpha, kDtFast);

        // --- Незручні випадки, які буває видно лише в польоті --------------
        if (!std::isfinite(vehicle.position.z) || !std::isfinite(vehicle.attitude.w)) {
            std::cout << "\nМодель розійшлася на t = " << t << " с — контур нестійкий.\n";
            return 1;
        }
        if (vehicle.position.z >= 0.0F) {
            std::cout << std::setw(6) << t << " |" << std::setw(6) << vehicle.position.x
                      << " |" << std::setw(6) << vehicle.position.y
                      << " |" << std::setw(7) << -vehicle.position.z
                      << " |" << std::setw(6) << vehicle.tiltDegrees()
                      << " |" << std::setw(4) << command.thrust << " | ТОРКАННЯ ЗЕМЛІ\n";
            std::cout << "\nСторож уставки посадив апарат замість того, щоб віддати\n"
                         "керування контуру, який мовчить уже понад 100 мс.\n";
            return 0;
        }

        if (tick % 100 == 0) {   // друк кожні 100 мс
            std::cout << std::setw(6) << t << " |" << std::setw(6) << vehicle.position.x
                      << " |" << std::setw(6) << vehicle.position.y
                      << " |" << std::setw(7) << -vehicle.position.z
                      << " |" << std::setw(6) << vehicle.tiltDegrees()
                      << " |" << std::setw(4) << command.thrust
                      << " | " << (command.fallback ? "АВАРІЯ" : "НАВЕД.")
                      << " | " << (motors.saturated ? "так" : "-") << '\n';
        }

        now += Micros{1000};
    }

    std::cout << "\nСимуляція завершена: " << kSimSeconds << " с, " << totalTicks
              << " тактів регулятора, " << totalTicks / kGuidanceDivider << " тактів наведення.\n";
    return 0;
}
