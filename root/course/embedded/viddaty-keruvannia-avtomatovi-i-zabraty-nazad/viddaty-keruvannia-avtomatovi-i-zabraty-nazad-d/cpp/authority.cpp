#include "authority.hpp"

#include <algorithm>
#include <cmath>

namespace fc {
namespace {

constexpr Seconds kDtMin{0.0002f};
constexpr Seconds kDtMax{0.1f};

} // namespace

ControlCommand blend(const Authority& a,
                     const ControlCommand& autopilot,
                     const ControlCommand& pilot) noexcept {
    // u = (1 − α)·u_auto + α·u_pilot, окремо для орієнтації й окремо для газу.
    const float ap = std::clamp(a.attitude, 0.0f, 1.0f);
    const float at = std::clamp(a.throttle, 0.0f, 1.0f);

    return ControlCommand{
        (1.0f - ap) * autopilot.roll     + ap * pilot.roll,
        (1.0f - ap) * autopilot.pitch    + ap * pilot.pitch,
        (1.0f - ap) * autopilot.yaw      + ap * pilot.yaw,
        (1.0f - at) * autopilot.throttle + at * pilot.throttle};
}

void AuthorityManager::emit(Event e) noexcept {
    if (event_count_ < kMaxEvents) events_[event_count_++] = e;
}

bool AuthorityManager::attitude_deflected(const RcCommand& rc) const noexcept {
    // Осі орієнтації пружинять у нейтраль — їх судимо за абсолютним відхиленням.
    return std::abs(rc.roll) > cfg_.deadband ||
           std::abs(rc.pitch) > cfg_.deadband ||
           std::abs(rc.yaw) > cfg_.deadband;
}

Status AuthorityManager::status(bool request_rtl) const noexcept {
    return Status{phase_, alpha_,
                  alpha_.attitude > kActiveEps || alpha_.throttle > kActiveEps,
                  request_rtl};
}

Status AuthorityManager::update(const std::optional<RcCommand>& rc,
                                bool fence_breach,
                                Seconds dt_raw) noexcept {
    event_count_ = 0;

    // Пропущений такт планувальника не має права перестрибнути всю рампу.
    const Seconds dt = std::clamp(dt_raw, kDtMin, kDtMax);

    if (!rc) {
        // Пастка перша: втрата зв'язку посеред ручного маневру. Тримати
        // останні стіки не можна — вони вже нічого не означають.
        if (!rc_lost_) emit(Event::RcLost);
        phase_ = Phase::AutoNav;
        alpha_ = Authority{};
        hold_timer_ = Seconds{0.0f};
        throttle_engaged_ = false;
        prev_switch_manual_ = false;
        rc_lost_ = true;
        return status(true);
    }

    if (rc_lost_ || !primed_) {
        // Перший дійсний кадр (чи повернення зв'язку): похідну газу заводимо
        // з поточного положення важеля, інакше стрибок із нуля виглядатиме
        // як рвучкий рух пілота.
        rc_lost_ = false;
        primed_ = true;
        throttle_prev_ = rc->throttle;
        throttle_rate_ = 0.0f;
    }

    // Рух важеля газу вимірюємо ШВИДКІСТЮ, а не відхиленням від центру:
    // у літака газ не пружинить у нейтраль, і поріг |thr − 0.5| > db дав би
    // вічне перехоплення на пульті, що просто лежить у нулі.
    const float raw_rate = (rc->throttle - throttle_prev_) / dt.count();
    throttle_prev_ = rc->throttle;
    throttle_rate_ += (raw_rate - throttle_rate_) *
                      (dt.count() / (cfg_.throttle_rate_tau.count() + dt.count()));
    const bool throttle_moving = std::abs(throttle_rate_) > cfg_.throttle_move_rate;

    const bool switch_manual = (rc->mode == FlightMode::Manual);
    const bool released_switch = prev_switch_manual_ && !switch_manual;
    prev_switch_manual_ = switch_manual;

    bool demand = attitude_deflected(*rc) || throttle_moving || switch_manual;

    // Пастка третя: геозона. Її авторитет вищий за авторитет пілота, тому
    // вимога перехоплення просто перестає існувати, доки триває порушення.
    if (fence_breach) {
        if (!fence_latched_) {
            fence_latched_ = true;
            emit(Event::FenceReclaim);
        }
        demand = false;
        if (phase_ == Phase::OverrideIn || phase_ == Phase::ManualHold ||
            phase_ == Phase::HandbackWait) {
            phase_ = Phase::BlendingOut; // примусово, але через ту саму рампу
            hold_timer_ = Seconds{0.0f};
        }
    } else {
        fence_latched_ = false;
    }

    switch (phase_) {
        case Phase::AutoNav:
            alpha_.attitude = 0.0f;
            if (demand) {
                phase_ = Phase::OverrideIn;
                emit(Event::OverrideBegin);
            }
            break;

        case Phase::OverrideIn:
            alpha_.attitude += dt / cfg_.blend_in;
            if (alpha_.attitude >= 1.0f) {
                alpha_.attitude = 1.0f;
                phase_ = Phase::ManualHold;
                emit(Event::ManualFull);
            }
            break;

        case Phase::ManualHold:
            alpha_.attitude = 1.0f;
            if (!demand) {
                hold_timer_ = Seconds{0.0f};
                if (released_switch) {
                    phase_ = Phase::BlendingOut; // тумблер — свідома дія
                } else {
                    phase_ = Phase::HandbackWait;
                    emit(Event::HandbackArmed);
                }
            }
            break;

        case Phase::HandbackWait:
            alpha_.attitude = 1.0f;
            if (demand) {
                // Прохід стіка через нуль по дорозі в інший бік — не віддача.
                phase_ = Phase::ManualHold;
                hold_timer_ = Seconds{0.0f};
            } else {
                hold_timer_ += dt;
                if (released_switch || hold_timer_ >= cfg_.handback_hold) {
                    phase_ = Phase::BlendingOut;
                }
            }
            break;

        case Phase::BlendingOut:
            if (demand) {
                phase_ = Phase::OverrideIn;
                emit(Event::OverrideBegin);
            } else {
                alpha_.attitude -= dt / cfg_.blend_out;
                if (alpha_.attitude <= 0.0f) {
                    alpha_.attitude = 0.0f;
                    phase_ = Phase::AutoNav;
                    throttle_engaged_ = false;
                    emit(Event::AutoResumed);
                }
            }
            break;
    }

    // Пастка друга: неузгодженість газу. Крен і тангаж віддаємо стікам одразу,
    // а контур швидкості лишається за автопілотом, доки важіль газу фізично
    // не зрушить з місця.
    if (phase_ != Phase::AutoNav && throttle_moving && !throttle_engaged_) {
        throttle_engaged_ = true;
        emit(Event::ThrottleEngaged);
    }

    const float target = throttle_engaged_ ? alpha_.attitude : 0.0f;
    if (alpha_.throttle < target) {
        alpha_.throttle = std::min(target, alpha_.throttle + dt / cfg_.blend_in);
    } else {
        alpha_.throttle = std::max(target, alpha_.throttle - dt / cfg_.blend_out);
    }

    return status(false);
}

} // namespace fc
