// ===========================================================================
//  session.cpp — переходи автомата, гейти якості й запис у Flash
// ===========================================================================

#include "mag_cal/session.hpp"

#include <cmath>

namespace mag_cal {
namespace {

// Радіус підігнаної сфери, що розійшовся з очікуваним полем більше ніж на
// третину, майже завжди означає калібрування біля сталевої конструкції.
constexpr float kRadiusTolerance = 0.30F;

[[nodiscard]] bool radius_is_bad(const Calibration& cal) noexcept {
    if (!(cal.earth_field > 1.0F)) {
        return true;
    }
    return std::abs(cal.sphere_radius / cal.earth_field - 1.0F) > kRadiusTolerance;
}

}  // namespace

CalibrationSession::CalibrationSession(std::uint8_t system_id,
                                       std::uint8_t component_id,
                                       std::uint8_t compass_id,
                                       float earth_field_ut) noexcept
    : collector_{earth_field_ut}, reporter_{system_id, component_id, compass_id} {
    active_.earth_field = collector_.earth_field();
    active_.sphere_radius = collector_.earth_field();
    active_.compass_id = compass_id;
    candidate_ = active_;
}

void CalibrationSession::enter(State next, std::uint32_t now_ms) noexcept {
    state_ = next;
    state_since_ms_ = now_ms;
}

// Прапорець відмови й діод рухаються разом: інакше буває стан, коли стек
// знає про несправність, а зовні цього не видно.
void CalibrationSession::set_fault(bool fault) noexcept {
    mag_fault_ = fault;
    board_port::set_fault_led(fault);
}

std::expected<Calibration, StorageError> CalibrationSession::boot(
    std::uint32_t now_ms) noexcept {
    auto loaded = load();
    if (loaded) {
        active_ = *loaded;
        active_.compass_id = reporter_.compass_id();
        set_fault(false);
    } else {
        // Биті або відсутні коефіцієнти: летимо на сирому компасі лише
        // після усвідомленого рішення оператора, тож піднімаємо відмову.
        active_ = Calibration{};
        active_.earth_field = collector_.earth_field();
        active_.sphere_radius = collector_.earth_field();
        active_.compass_id = reporter_.compass_id();
        set_fault(true);
    }

    enter(State::Idle, now_ms);
    return loaded;
}

bool CalibrationSession::start(std::uint32_t now_ms) noexcept {
    if (state_ == State::Collecting || state_ == State::Solving ||
        state_ == State::Validating) {
        return false;   // процедура вже йде
    }

    collector_.reset(active_.earth_field, now_ms);
    reporter_.next_attempt();
    enter(State::Collecting, now_ms);

    // Відлік тайм-ауту бездіяльності починається зі старту, а не з першої
    // точки: оператор, що взагалі не взяв апарат у руки, теж має здатися.
    static_cast<void>(reporter_.progress(collector_, CalStatus::Waiting, now_ms));
    return true;
}

void CalibrationSession::cancel(std::uint32_t now_ms) noexcept {
    if (state_ == State::Idle) {
        return;
    }

    collector_.reset(active_.earth_field, now_ms);

    // Повертаємо ті коефіцієнти, з якими апарат літав, — саме з Flash, а не
    // з оперативної копії: так відкат перевіряє ще й читаність запису.
    if (auto restored = load()) {
        active_ = *restored;
        active_.compass_id = reporter_.compass_id();
        set_fault(false);
    } else {
        set_fault(true);
    }

    reporter_.report(active_, false, false);
    enter(State::Idle, now_ms);
}

PushResult CalibrationSession::push(const Vec3& raw, const Vec3& gyro_rad_s,
                                    std::uint32_t now_ms) noexcept {
    if (state_ != State::Collecting) {
        return PushResult::BinFull;
    }
    return collector_.push(raw, gyro_rad_s, now_ms);
}

bool CalibrationSession::ready_to_solve() const noexcept {
    return state_ == State::Collecting &&
           collector_.coverage_percent() >= limits::kSolveCoveragePct &&
           collector_.size() >= limits::kMinSamples;
}

void CalibrationSession::begin_solve(std::uint32_t now_ms) noexcept {
    if (state_ == State::Collecting) {
        enter(State::Solving, now_ms);
    }
}

void CalibrationSession::submit(
    const std::expected<Calibration, SolveFailure>& outcome,
    std::uint32_t now_ms) noexcept {
    if (state_ != State::Solving) {
        return;   // результат від уже скасованої спроби
    }

    if (!outcome) {
        // Гілка REJECT: чинні коефіцієнти лишаються ті, що були
        candidate_ = outcome.error().partial;
        candidate_.compass_id = reporter_.compass_id();
        enter(State::Rejected, now_ms);
        static_cast<void>(reporter_.progress(collector_,
                                             radius_is_bad(candidate_)
                                                 ? CalStatus::BadRadius
                                                 : CalStatus::Failed,
                                             now_ms));
        reporter_.report(candidate_, false, false);
        return;
    }

    candidate_ = *outcome;
    candidate_.compass_id = reporter_.compass_id();

    // Нев'язка пройшла — дивимось на геометрію матриці W
    enter(State::Validating, now_ms);
    if (!candidate_.passes_quality_gates()) {
        enter(State::Rejected, now_ms);
        reporter_.report(candidate_, false, false);
        return;
    }

    if (!save(candidate_)) {
        // Порахували добре, а зберегти не змогли: приймати такі коефіцієнти
        // в пам'ять не можна — після перезавантаження апарат полетів би з
        // іншими, і причину шукали б уже в повітрі.
        enter(State::Rejected, now_ms);
        reporter_.report(candidate_, false, false);
        return;
    }

    active_ = candidate_;
    set_fault(false);
    enter(State::Saved, now_ms);
    reporter_.report(active_, true, true);
}

void CalibrationSession::service(std::uint32_t now_ms) noexcept {
    switch (state_) {
        case State::Collecting: {
            const std::uint32_t idle_ms = now_ms - collector_.last_accept_ms();
            if (idle_ms > limits::kIdleTimeoutMs) {
                cancel(now_ms);
                return;
            }
            static_cast<void>(
                reporter_.progress(collector_, CalStatus::Collecting, now_ms));
            break;
        }
        case State::Solving:
        case State::Validating:
            static_cast<void>(
                reporter_.progress(collector_, CalStatus::Solving, now_ms));
            break;
        case State::Saved:
            static_cast<void>(
                reporter_.progress(collector_, CalStatus::Success, now_ms));
            break;
        case State::Rejected:
            static_cast<void>(
                reporter_.progress(collector_, CalStatus::Failed, now_ms));
            break;
        case State::Idle:
            break;
    }
}

bool CalibrationSession::arming_allowed() const noexcept {
    // Озброєння блокує і відмова компаса, і сама незавершена процедура:
    // крутити апарат у руках із розкрученими двигунами нікому не треба.
    if (mag_fault_ || !active_.valid) {
        return false;
    }
    return state_ == State::Idle || state_ == State::Saved || state_ == State::Rejected;
}

}  // namespace mag_cal
