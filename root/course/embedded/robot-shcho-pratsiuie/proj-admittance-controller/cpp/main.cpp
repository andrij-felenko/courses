// Демонстраційний контур 1 кГц: рука підводить інструмент до жорсткої
// деталі, працює податливо, переживає зрив із деталі й удар.
// Модель довкілля тут груба — важливий саме порядок обробки:
// давач → компенсація ваги → адмітанс → DLS → швидкості суглобів.

#include <array>
#include <cmath>
#include <cstddef>
#include <print>
#include <random>
#include <string_view>

#include "admittance.hpp"
#include "arm.hpp"

namespace {

using robot::arm::Vec3;
using robot::compliance::Command;
using robot::compliance::Fault;
using robot::compliance::Mode;
using robot::compliance::Vector6;
namespace compliance = robot::compliance;

constexpr int kSimSteps = 4000;
constexpr float kApproachSpeed = 0.020f;   // м/с уздовж осі інструмента
constexpr float kWallGap = 0.010f;         // зазор до деталі на старті, м
constexpr float kEnvStiffness = 25000.0f;  // Н/м — жорстка металева деталь
constexpr int kSlipStep = 2000;            // t = 2.0 с: зрив із деталі
constexpr int kHitStep = 2600;             // t = 2.6 с: удар по інструменту
constexpr int kHitLength = 30;
constexpr float kHitForce = 220.0f;        // Н

// Сталий зсув нуля п'єзорезистивних мостів після прогрівання —
// саме його знімає тарування.
constexpr Vector6 kThermalBias{0.9f, -1.4f, 2.2f, 0.05f, -0.03f, 0.02f};

[[nodiscard]] std::string_view mode_name(Mode m) noexcept
{
    switch (m) {
    case Mode::Idle:          return "IDLE";
    case Mode::Taring:        return "TARING";
    case Mode::Active:        return "ACTIVE";
    case Mode::ForceExceeded: return "FORCE_EXCEEDED";
    case Mode::Retract:       return "RETRACT";
    default:                  return "FAULT";
    }
}

[[nodiscard]] std::string_view fault_name(Fault f) noexcept
{
    switch (f) {
    case Fault::InvalidConfig: return "негодящі коефіцієнти";
    case Fault::TareDisturbed: return "тарування під навантаженням";
    default:                   return "перевищено ліміт сили";
    }
}

[[nodiscard]] Vec3 cross(const Vec3& a, const Vec3& b) noexcept
{
    return Vec3{a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0]};
}

} // namespace

int main()
{
    compliance::Config cfg{
        .virtual_mass = {4.0f, 4.0f, 4.0f, 0.06f, 0.06f, 0.06f},
        .virtual_stiffness = {350.0f, 350.0f, 350.0f, 8.0f, 8.0f, 8.0f},
        .deadband = {0.8f, 0.8f, 0.8f, 0.05f, 0.05f, 0.05f},
        .max_force = {60.0f, 60.0f, 60.0f, 6.0f, 6.0f, 6.0f},
        .max_disp = {0.030f, 0.030f, 0.030f, 0.20f, 0.20f, 0.20f},
        .max_vel = {0.15f, 0.15f, 0.15f, 1.0f, 1.0f, 1.0f},
        .filter_alpha = compliance::Config::alpha_for_cutoff(20.0f),
        .retract_speed = 0.05f,
    };
    cfg.set_critical_damping(); // zeta = 1

    auto controller = compliance::Controller::create(cfg);
    if (!controller) {
        std::print(stderr, "регулятор не створено: {}\n", fault_name(controller.error()));
        return 1;
    }

    const robot::arm::ToolInertia tool{.mass = 0.8f, .com = {0.0f, 0.0f, 0.075f}};
    constexpr Vec3 tip_offset{0.0f, 0.0f, 0.150f}; // вістря у системі фланця

    std::array<float, robot::arm::kJoints> q{0.0f, -0.40f, 0.80f, 0.0f, 0.60f, 0.0f};
    robot::arm::Model arm;
    arm.update(q);

    // Поверхня деталі: площина, перпендикулярна осі інструмента,
    // за kWallGap попереду вістря на старті.
    const Vec3 wall_normal = robot::arm::rotate(arm.orientation(), Vec3{0.0f, 0.0f, 1.0f});
    const Vec3 tip0 = arm.tool_point(tip_offset);
    const Vec3 wall_point{tip0[0] + kWallGap * wall_normal[0],
                          tip0[1] + kWallGap * wall_normal[1],
                          tip0[2] + kWallGap * wall_normal[2]};

    controller->start_tare();

    std::mt19937 rng{2026u};
    std::uniform_real_distribution<float> force_noise{-0.40f, 0.40f};
    std::uniform_real_distribution<float> torque_noise{-0.03f, 0.03f};

    Vector6 x_nominal{};
    Vector6 v_nominal{};
    bool wall_present = true;
    bool acknowledged = false;
    float slip_overshoot = 0.0f;
    Mode previous = controller->mode();

    std::print("   t,с | режим          | Fz_filt,Н | зміщ.,мм | зазор,мм |    w   | lambda\n");

    for (int step = 0; step < kSimSteps; ++step) {
        const float t = static_cast<float>(step) * compliance::kDtSec;
        arm.update(q);

        // --- Модель контакту ---
        const Vec3 tip = arm.tool_point(tip_offset);
        float depth = 0.0f;
        for (std::size_t i = 0; i < 3; ++i) {
            depth += (tip[i] - wall_point[i]) * wall_normal[i];
        }

        if (step == kSlipStep && wall_present) {
            wall_present = false;
            std::print("  t={:.3f} с: інструмент зірвався з деталі, сила зникла\n", t);
        }

        Vec3 f_world{};
        if (wall_present && depth > 0.0f) {
            for (std::size_t i = 0; i < 3; ++i) {
                f_world[i] = -kEnvStiffness * depth * wall_normal[i];
            }
        }
        if (step >= kHitStep && step < kHitStep + kHitLength) {
            for (std::size_t i = 0; i < 3; ++i) {
                f_world[i] += -kHitForce * wall_normal[i];
            }
        }

        // --- Сирий вимір давача на зап'ястку (система фланця) ---
        const Vec3 f_contact = robot::arm::rotate_inverse(arm.orientation(), f_world);
        const Vec3 m_contact = cross(tip_offset, f_contact);
        const Vector6 gravity = robot::arm::tool_gravity_wrench(tool, arm.orientation());

        Vector6 raw{};
        for (std::size_t i = 0; i < 3; ++i) {
            raw[i] = f_contact[i] + gravity[i] + kThermalBias[i] + force_noise(rng);
            raw[3 + i] = m_contact[i] + gravity[3 + i] + kThermalBias[3 + i] + torque_noise(rng);
        }

        // --- Компенсація ваги інструмента ---
        const Vector6 external = robot::arm::compensate_tool_gravity(tool, arm.orientation(), raw);
        // Давач віддає силу, ЩО ДІЄ НА інструмент; рівняння адмітансу
        // записане для сили реакції — тому знак міняємо тут, один раз.
        Vector6 reaction{};
        for (std::size_t i = 0; i < compliance::kDof; ++i) {
            reaction[i] = -external[i];
        }

        // --- Номінальна траєкторія: подача вздовж осі інструмента ---
        v_nominal.fill(0.0f);
        if (controller->mode() == Mode::Active && step < kSlipStep) {
            v_nominal[2] = kApproachSpeed;
        }
        for (std::size_t i = 0; i < compliance::kDof; ++i) {
            x_nominal[i] += v_nominal[i] * compliance::kDtSec;
        }

        const auto result = controller->step(reaction, x_nominal, v_nominal);
        Command command{};
        if (result) {
            command = *result;
        } else {
            std::print("  t={:.3f} с: {}\n", t, fault_name(result.error()));
            if (controller->mode() == Mode::Fault) {
                std::print(stderr, "цикл зупинено\n");
                return 2;
            }
            // Такт спрацювання ліміту: приводи стоять, з наступного такту
            // автомат сам поведе інструмент від деталі.
            for (std::size_t i = 0; i < compliance::kDof; ++i) {
                command.pose[i] = x_nominal[i] + controller->displacement()[i];
            }
        }

        if (controller->mode() != previous) {
            std::print("  t={:.3f} с: {} → {}\n", t, mode_name(previous),
                       mode_name(controller->mode()));
            previous = controller->mode();
        }

        // --- Декартова команда з системи інструмента в базову ---
        const Vector6 twist_base = robot::arm::rotate_to_base(arm.orientation(), command.twist);
        const auto motion = arm.joint_velocity(twist_base, 0.08f, 0.02f);
        if (!motion) {
            std::print(stderr, "t={:.3f} с: рука в сингулярності, рух зупинено\n", t);
            return 3;
        }
        for (std::size_t j = 0; j < robot::arm::kJoints; ++j) {
            q[j] += motion->q_dot[j] * compliance::kDtSec;
        }

        // Під час контакту зміщення від'ємне (інструмент поступається).
        // Після зриву воно повертається до нуля — і при zeta = 1 не має
        // перескочити в плюс, тобто вистрілити вперед.
        const float disp_z = controller->displacement()[2];
        if (step > kSlipStep && step < kHitStep && disp_z > slip_overshoot) {
            slip_overshoot = disp_z;
        }

        if (!acknowledged && controller->retract_finished()) {
            std::print("  t={:.3f} с: відхід завершено, квитуємо аварію\n", t);
            controller->acknowledge();
            acknowledged = true;
            previous = controller->mode();
        }

        if (step % 100 == 0) {
            std::print("{:6.3f} | {:<14} | {:9.2f} | {:8.2f} | {:8.2f} | {:6.4f} | {:6.4f}\n",
                       t, mode_name(controller->mode()), controller->filtered_force()[2],
                       disp_z * 1000.0f, -depth * 1000.0f, arm.manipulability(),
                       motion->lambda);
        }
    }

    std::print("\nПеререгулювання після зриву: {:.3f} мм (zeta = 1 → без вистрілювання)\n",
               slip_overshoot * 1000.0f);
    return 0;
}
