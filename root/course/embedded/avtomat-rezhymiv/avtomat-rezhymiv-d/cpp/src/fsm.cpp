#include "fsm.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <format>

#include "throttle.hpp"

namespace fm {
namespace {

[[nodiscard]] bool isLandingMode(Mode mode) noexcept
{
    return mode == Mode::Land || mode == Mode::EmergencyLand;
}

}  // namespace

FlightModeFsm::FlightModeFsm(Params params, Reporter& reporter, const VehicleState& s)
    : params_{params}, reporter_{reporter}
{
    // Стан за замовчуванням — найнижчий стабілізований: він потребує лише
    // інерціального блока, тож у нього можна впасти з будь-якої відмови.
    mode_         = Mode::Stabilize;
    previousMode_ = Mode::Stabilize;
    priority_     = Priority::None;
    modeSince_    = s.now;
    lastStep_     = s.now;
    throttle_     = s.propulsion.motorOutput;
    controllers_.init(s);
}

void FlightModeFsm::deny(Mode target, Deny reason, Tone tone)
{
    reporter_.statusText(Severity::Error, denyText(target, reason));
    reporter_.commandAck(kMavCmdDoSetMode, toMavResult(reason));
    reporter_.tone(tone);
}

/* Єдине місце, де змінюється поточний режим. Усе, що мусить статися разом зі
   зміною — фіксація уставок, передустановка інтеграторів, скидання детектора
   посадки, латч апаратної відсічки, — стається тут, і ніде більше. */
void FlightModeFsm::applyTransition(Mode target, Priority priority, const VehicleState& s,
                                    std::string_view reason, Severity severity)
{
    previousMode_ = mode_;
    mode_         = target;
    priority_     = priority;
    modeSince_    = s.now;

    if (target == Mode::Terminate) {
        arming_.kill();
    }
    if (!isLandingMode(target)) {
        land_.reset();
    }

    controllers_.enter(target, s, params_);

    const std::string text = reason.empty()
        ? std::format("Mode: {} -> {}", name(previousMode_), name(target))
        : std::string{reason};

    reporter_.statusText(severity, text);
}

/* Витриманість охоронця: перехід УГОРУ ієрархією дозволено лише тоді, коли
   умова тримається guardStable. Падіння вниз витримки не потребує. */
bool FlightModeFsm::guardStable(Mode target) const noexcept
{
    if (traits(target).needsPosition && !posGuardOk_.state()) {
        return false;
    }
    if (traits(target).needsAltitude && !altGuardOk_.state()) {
        return false;
    }
    return true;
}

GuardResult FlightModeFsm::request(Mode target, Priority priority, const VehicleState& s)
{
    if (!valid(target)) {
        deny(target, Deny::InvalidMode, Tone::ModeRejected);
        return std::unexpected(Deny::InvalidMode);
    }

    // Сходинка пріоритетів: критичний failsafe не поступається нікому, крім
    // апаратної відсічки.
    if (!overrides(priority, priority_)) {
        deny(target, Deny::FailsafeLock, Tone::ModeRejected);
        return std::unexpected(Deny::FailsafeLock);
    }

    if (target == mode_) {
        reporter_.commandAck(kMavCmdDoSetMode, MavResult::Accepted);
        return {};
    }

    // 1. Заслінка газу — перед охоронцями: навіть ідеально справні сенсори не
    //    виправдають стрибка тяги з 48% у нуль.
    if (auto lock = throttleInterlock(mode_, target, s, params_, arming_.inAir()); !lock) {
        deny(target, lock.error(), Tone::ThrottleLock);
        return lock;
    }

    // 2. Параметричні охоронці цільового режиму.
    if (auto verdict = guard::check(target, s, params_); !verdict) {
        // Відмова нічого не чіпає: ні режиму, ні контурів, ні виходу на мотори.
        deny(target, verdict.error(), Tone::ModeRejected);
        return verdict;
    }
    if (!guardStable(target)) {
        deny(target, Deny::GuardUnstable, Tone::ModeRejected);
        return std::unexpected(Deny::GuardUnstable);
    }

    applyTransition(target, priority, s, {}, Severity::Info);
    reporter_.commandAck(kMavCmdDoSetMode, MavResult::Accepted);
    reporter_.tone(Tone::ModeAccepted);
    return {};
}

GuardResult FlightModeFsm::requestArm(const VehicleState& s)
{
    if (auto verdict = arming_.requestArm(s); !verdict) {
        reporter_.statusText(Severity::Error, denyText(mode_, verdict.error()));
        reporter_.tone(Tone::ModeRejected);
        return verdict;
    }

    // Озброєння скидає контури на поточні покази: тяга ще нульова, висота
    // нульова, і саме від цих значень має початися перший політ.
    controllers_.enter(mode_, s, params_);
    reporter_.statusText(Severity::Info, "Armed");
    reporter_.tone(Tone::ModeAccepted);
    return {};
}

GuardResult FlightModeFsm::requestDisarm(const VehicleState&)
{
    if (auto verdict = arming_.requestDisarm(); !verdict) {
        reporter_.statusText(Severity::Warning, "Disarm refused: vehicle is airborne");
        reporter_.tone(Tone::ModeRejected);
        return verdict;
    }
    reporter_.statusText(Severity::Info, "Disarmed");
    reporter_.tone(Tone::Disarm);
    return {};
}

void FlightModeFsm::setPositionTarget(GeoPoint target, float altRelM)
{
    controllers_.setPositionTarget(mode_, target, altRelM);
}

/* Перехоплення пілотом (рівень 2): рух стіків у автономному режимі скасовує
   автономію. Цілимося в найвищий режим, який дозволяють сенсори Й заслінка
   газу: скинути людину одразу в ручну тягу було б тим самим стрибком газу,
   від якого ми захищаємося. */
void FlightModeFsm::handlePilotOverride(const VehicleState& s)
{
    static constexpr std::array<Mode, 3> kLadder{Mode::PosHold, Mode::AltHold, Mode::Stabilize};

    if (!traits(mode_).autonomous) {
        return;
    }
    if (s.age(s.links.lastRcFrame) > params_.rcLoss) {
        return;   // стіки з мертвого лінка — не воля пілота, а шум
    }

    const float dead = params_.pilotOverrideStick;

    if (std::fabs(s.sticks.roll) <= dead && std::fabs(s.sticks.pitch) <= dead &&
        std::fabs(s.sticks.yaw) <= dead) {
        return;
    }

    for (Mode candidate : kLadder) {
        if (!guard::check(candidate, s, params_)) {
            continue;
        }
        if (!throttleInterlock(mode_, candidate, s, params_, arming_.inAir())) {
            continue;
        }
        applyTransition(candidate, Priority::PilotOverride, s,
                        "Pilot override: mission cancelled", Severity::Notice);
        reporter_.tone(Tone::ModeAccepted);
        return;
    }
}

/* Каскадна деградація: сенсорна база просіла під поточним режимом. Спускаємося
   рівно на одну сходинку — до рівня, який ще забезпечений. */
void FlightModeFsm::handleDegradation(const VehicleState& s, bool inAir)
{
    if (!inAir) {
        return;
    }

    if (traits(mode_).needsPosition && !posGuardOk_.state()) {
        applyTransition(degrade(mode_), priority_, s,
                        "Degraded: position estimate lost", Severity::Alert);
        reporter_.tone(Tone::Failsafe);
    }
    if (traits(mode_).needsAltitude && !altGuardOk_.state()) {
        applyTransition(degrade(mode_), priority_, s,
                        "Degraded: altitude estimate lost", Severity::Alert);
        reporter_.tone(Tone::Failsafe);
    }
}

void FlightModeFsm::handleFailsafe(const VehicleState& s, bool inAir)
{
    const std::optional<Preemption> event = failsafe::evaluate(s, params_, mode_, inAir);

    if (!event) {
        // Причина зникла: режим лишається, але замок знімається — пілот знову
        // може перемикати. Апаратна відсічка з-під замка не виходить ніколи.
        if (priority_ >= Priority::NavFailsafe && priority_ < Priority::Hardware &&
            mode_ != Mode::Terminate) {
            priority_ = Priority::Routine;
        }
        return;
    }

    if (!overrides(event->priority, priority_)) {
        return;
    }

    if (mode_ == event->mode) {
        // Уже там, куди веде аварія: піднімаємо замок і мовчимо, щоб не сипати
        // той самий STATUSTEXT сто разів на секунду.
        priority_ = std::max(priority_, event->priority);
        return;
    }

    applyTransition(event->mode, event->priority, s, event->reason, event->severity);
    reporter_.tone(Tone::Failsafe);
}

void FlightModeFsm::update(const VehicleState& s)
{
    Seconds dt{0.01F};

    if (primed_) {
        dt = std::chrono::duration_cast<Seconds>(s.now - lastStep_);
    } else {
        primed_ = true;
    }
    lastStep_ = s.now;

    // 1. Детектор польоту — від нього залежать і заслінка газу, і заборона
    //    роззброєння, і те, які аварії взагалі мають сенс.
    const bool inAir = arming_.update(s, params_);

    // 2. Витриманість охоронців. Рахуємо ЩОТАКТУ, незалежно від того, чи хтось
    //    просить зміни режиму: інакше витримка почала б відлік з моменту
    //    запиту, а не з моменту, коли сенсори справді вичистилися.
    altGuardOk_.update(guard::altitude(s, params_).has_value(), s.now,
                       params_.guardStable, Millis{0});
    posGuardOk_.update(guard::position(s, params_).has_value(), s.now,
                       params_.guardStable, Millis{0});

    // 3. Аварії — до всього іншого: вони мають право перебити й місію, і пілота.
    handleFailsafe(s, inAir);

    // 4. Перехоплення стіками (рівень 2) — лише якщо аварія не тримає замок.
    if (priority_ <= Priority::PilotOverride) {
        handlePilotOverride(s);
    }

    // 5. Каскадна деградація за наявними оцінювачами.
    handleDegradation(s, inAir);

    // 6. Комбінація стіків роззброєння — у повітрі ігнорується.
    if (s.sticks.disarmCombo && arming_.armed()) {
        (void)requestDisarm(s);
    }

    // 7. Детектор посадки й завершення циклу.
    land_.update(s, params_, isLandingMode(mode_), inAir);

    if (land_.consumeDisarmEvent()) {
        arming_.disarmAfterLanding();
        reporter_.statusText(Severity::Info, "Landing detected: disarmed");
        reporter_.tone(Tone::Disarm);
        applyTransition(Mode::Stabilize, Priority::None, s,
                        "Safe state: on ground, disarmed", Severity::Info);
    }

    // 8. Контури. Автомат уже вирішив, що активне; тут це просто рахується.
    throttle_ = controllers_.step(mode_, s, params_, land_, dt);

    if (!arming_.armed()) {
        controllers_.cut();
        throttle_ = 0.0F;
    }
}

}  // namespace fm
