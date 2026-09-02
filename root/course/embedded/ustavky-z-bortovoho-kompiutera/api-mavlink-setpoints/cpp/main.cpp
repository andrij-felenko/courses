#include <chrono>
#include <expected>
#include <iostream>
#include <stdexcept>
#include <string>

#include "offboard_session.hpp"
#include "setpoints.hpp"

using namespace std::chrono_literals;

namespace {

constexpr float kHoverThrust = 0.35f;   // типова тяга зависання коптера
constexpr float kClimbSpeed = 1.5f;
constexpr float kDescendSpeed = 0.7f;
constexpr float kTurnRate = 0.4f;

void check(const std::expected<void, std::string>& r)
{
    if (!r) throw std::runtime_error(r.error());
}

}  // namespace

int main()
{
    try {
        px4::OffboardSession session{14540};

        std::cout << "чекаємо HEARTBEAT автопілота на UDP :14540...\n";
        session.wait_for_heartbeat(10s);

        const sp::Ids ids = session.ids();
        const auto yaw_now = [&] { return session.telemetry().yaw.value_or(0.0f); };

        /* Кожна фаза — свій набір заповнених полів; маску #84 з них
           збирає sp::local_ned, тому руками її ніде не набирають. */
        const px4::OffboardSession::Builder hold = [&](double) {
            return sp::local_ned(ids, 0, sp::LocalTarget{.velocity = sp::Vec3{}, .yaw = yaw_now()});
        };
        const px4::OffboardSession::Builder climb = [&](double) {
            // вісь Z дивиться вниз: підйом — від'ємна швидкість
            return sp::local_ned(ids, 0, sp::LocalTarget{.velocity = sp::Vec3{.down = -kClimbSpeed},
                                                         .yaw = yaw_now()});
        };
        const px4::OffboardSession::Builder transit = [&](double) {
            // позиція плюс випереджувальна швидкість від генератора траєкторії
            return sp::local_ned(ids, 0, sp::LocalTarget{.position = sp::Vec3{10.0f, 0.0f, -5.0f},
                                                         .velocity = sp::Vec3{1.5f, 0.0f, 0.0f},
                                                         .yaw = 0.0f});
        };
        const px4::OffboardSession::Builder station = [&](double) {
            return sp::local_ned(ids, 0, sp::LocalTarget{.position = sp::Vec3{10.0f, 0.0f, -5.0f},
                                                         .yaw = 0.0f});
        };
        const px4::OffboardSession::Builder turn = [&](double) {
            return sp::local_ned(ids, 0, sp::LocalTarget{.velocity = sp::Vec3{},
                                                         .yaw_rate = kTurnRate});
        };
        const px4::OffboardSession::Builder level = [&](double) {
            return sp::attitude_target(
                ids, 0,
                sp::AttitudeTarget{.attitude = sp::Quaternion::from_euler(0.0f, 0.0f, yaw_now()),
                                   .thrust = kHoverThrust});
        };
        const px4::OffboardSession::Builder rates = [&](double) {
            return sp::attitude_target(ids, 0,
                                       sp::AttitudeTarget{.rates = sp::BodyRates{.yaw = kTurnRate},
                                                          .thrust = kHoverThrust});
        };
        const px4::OffboardSession::Builder descend = [&](double) {
            return sp::local_ned(ids, 0, sp::LocalTarget{.velocity = sp::Vec3{.down = kDescendSpeed},
                                                         .yaw = yaw_now()});
        };

        /* Потік уставок мусить іти ДО перемикання режиму: без свіжих цілей
           PX4 віддає TEMPORARILY_REJECTED. */
        check(session.stream(1s, hold, false));
        check(session.enable_offboard(hold));
        check(session.arm(true, hold));

        check(session.stream(4s, climb));
        check(session.stream(6s, transit));
        check(session.stream(4s, station));
        check(session.stream(3s, turn));
        check(session.stream(2s, level));
        check(session.stream(2s, rates));
        // після кадрів #83 повертаємо керування швидкістю й лише тоді сідаємо
        check(session.stream(1s, hold));
        check(session.stream(6s, descend));

        check(session.arm(false, hold));
        return 0;
    } catch (const std::exception& e) {
        // деструктор сесії сам переведе апарат у режим утримання
        std::cerr << "збій: " << e.what() << '\n';
        return 1;
    }
}
