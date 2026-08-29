#include "mission_vm.hpp"

#include <algorithm>
#include <cmath>

namespace mission {
namespace {

constexpr float kDefaultAcceptM  = 3.0F;
constexpr float kDefaultSpeedMps = 12.0F;
constexpr float kRtlAltM         = 50.0F;
constexpr float kTouchdownAltM   = 0.3F;
constexpr float kTakeoffTolM     = 0.5F;
constexpr float kBatMinV         = 14.2F;   /* 4S, ~3.55 В на банку ПІСЛЯ фільтра */

[[nodiscard]] bool is_nav(Opcode op) noexcept
{
    switch (op) {
        case Opcode::NavWaypoint:
        case Opcode::NavLoiterTime:
        case Opcode::NavRtl:
        case Opcode::NavLand:
        case Opcode::NavTakeoff:
            return true;
        default:
            return false;
    }
}

[[nodiscard]] bool is_condition(Opcode op) noexcept
{
    return op == Opcode::ConditionDelay || op == Opcode::ConditionDistance ||
           op == Opcode::ConditionYaw;
}

[[nodiscard]] bool is_known(Opcode op) noexcept
{
    return is_nav(op) || is_condition(op) || op == Opcode::DoJump ||
           op == Opcode::JumpIfBatteryLow || op == Opcode::DoChangeSpeed ||
           op == Opcode::DoSetServo;
}

[[nodiscard]] float accept_radius(const Instruction& in) noexcept
{
    return in.p2 > 0 ? static_cast<float>(in.p2) : kDefaultAcceptM;
}

/* Нульові координати в MAVLink означають «тут же, де апарат». */
[[nodiscard]] GeoPoint item_point(const Instruction& in, const Telemetry& t) noexcept
{
    GeoPoint p{ .lat_e7 = in.lat_e7, .lon_e7 = in.lon_e7, .alt_m = in.alt_m };
    if (in.lat_e7 == 0 && in.lon_e7 == 0) {
        p.lat_e7 = t.position.lat_e7;
        p.lon_e7 = t.position.lon_e7;
    }
    return p;
}

[[nodiscard]] std::optional<LoadError> lint_item(const Instruction& in,
                                                 std::size_t len) noexcept
{
    if (!is_known(in.opcode)) {
        return LoadError::UnknownOpcode;
    }

    switch (in.opcode) {
        case Opcode::DoJump:
            if (in.p1 < 0 || static_cast<std::size_t>(in.p1) >= len) {
                return LoadError::BadJumpTarget;
            }
            if (in.p2 < -1) {
                return LoadError::BadParameter;
            }
            break;

        case Opcode::JumpIfBatteryLow:
            if (in.p2 < 0 || static_cast<std::size_t>(in.p2) >= len) {
                return LoadError::BadJumpTarget;
            }
            if (in.p1 <= 0 || in.p1 > 100) {
                return LoadError::BadParameter;
            }
            break;

        case Opcode::DoSetServo:
            if (in.p1 < 1 || static_cast<std::size_t>(in.p1) > MissionVm::kServoChannels) {
                return LoadError::BadParameter;
            }
            if (in.p2 < 800 || in.p2 > 2200) {
                return LoadError::BadParameter;
            }
            break;

        case Opcode::DoChangeSpeed:
            if (in.p2 <= 0 || in.p2 > 60) {
                return LoadError::BadParameter;
            }
            break;

        case Opcode::ConditionDelay:
        case Opcode::ConditionDistance:
            if (in.p1 < 0) {
                return LoadError::BadParameter;
            }
            break;

        default:
            break;
    }
    return std::nullopt;
}

/* Зворотний стрибок i → t накриває інтервал [t, i]. Глибина вкладеності
   в точці x — скільки таких інтервалів її містять. */
[[nodiscard]] int max_jump_depth(std::span<const Instruction> program) noexcept
{
    int worst = 0;
    for (std::size_t x = 0; x < program.size(); ++x) {
        int depth = 0;
        for (std::size_t i = 0; i < program.size(); ++i) {
            if (program[i].opcode != Opcode::DoJump) {
                continue;
            }
            const auto target = static_cast<std::size_t>(program[i].p1);
            if (target <= i && x >= target && x <= i) {
                ++depth;
            }
        }
        worst = std::max(worst, depth);
    }
    return worst;
}

}  // namespace

std::expected<MissionVm, LoadError> MissionVm::load(std::span<const Instruction> program)
{
    if (program.empty()) {
        return std::unexpected(LoadError::Empty);
    }
    if (program.size() > kMaxItems) {
        return std::unexpected(LoadError::TooManyItems);
    }

    std::size_t jumps = 0;
    for (const auto& in : program) {
        if (const auto e = lint_item(in, program.size())) {
            return std::unexpected(*e);
        }
        if (in.opcode == Opcode::DoJump) {
            ++jumps;
        }
    }
    if (jumps > kMaxJumpSlots) {
        return std::unexpected(LoadError::TooManyJumps);
    }
    if (max_jump_depth(program) > kMaxJumpDepth) {
        return std::unexpected(LoadError::JumpNestingTooDeep);
    }

    MissionVm vm;
    std::ranges::copy(program, vm.code_.begin());
    vm.len_ = static_cast<std::uint16_t>(program.size());
    return vm;
}

void MissionVm::start(GeoPoint home, Millis now) noexcept
{
    home_        = home;
    nav_pc_      = 0;
    do_pc_       = 0;
    nav_active_  = false;
    nav_reached_ = false;
    loiter_started_ = now;
    total_jumps_ = 0;
    item_started_ = now;
    last_tick_    = now;

    /* Лічильники циклів існують лише в RAM — тому повторний старт
       тієї самої місії завжди має повний набір повторів. */
    jumps_.fill(JumpSlot{});
    condition_.reset();
    battery_ = BatteryFilter{3.0F};

    out_ = Outputs{};
    out_.target    = home;
    out_.speed_mps = kDefaultSpeedMps;
    status_        = Status::Running;
}

bool MissionVm::stopped() const noexcept
{
    return status_ == Status::Finished || status_ == Status::AbortJumpBudget ||
           status_ == Status::AbortItemTimeout || status_ == Status::AbortFailsafe;
}

std::optional<std::uint16_t> MissionVm::active_nav() const noexcept
{
    return nav_active_ ? std::optional<std::uint16_t>{nav_pc_} : std::nullopt;
}

Opcode MissionVm::opcode_at(std::uint16_t seq) const noexcept
{
    return seq < len_ ? code_[seq].opcode : Opcode::NavWaypoint;
}

void MissionVm::abort_mission(Status why) noexcept
{
    /* Рівень 3: VM більше нічого не веде, ціль забирає контур повернення. */
    status_      = why;
    nav_active_  = false;
    condition_.reset();
    out_.target       = home_;
    out_.target.alt_m = kRtlAltM;
    out_.yaw_setpoint_deg.reset();
}

void MissionVm::failsafe() noexcept
{
    if (status_ == Status::Running || status_ == Status::Paused) {
        abort_mission(Status::AbortFailsafe);
    }
}

void MissionVm::resume() noexcept
{
    if (status_ == Status::Paused) {
        status_       = Status::Running;
        item_started_ = last_tick_;
    }
}

void MissionVm::set_current(std::uint16_t seq) noexcept
{
    if (seq >= len_ || stopped()) {
        return;
    }
    do_pc_        = seq;
    nav_active_   = false;
    condition_.reset();
    item_started_ = last_tick_;
    status_       = Status::Running;
}

void MissionVm::nav_update(const Telemetry& t) noexcept
{
    const Instruction& in = code_[nav_pc_];
    const float r  = accept_radius(in);
    const float r2 = r * r;

    /* Посадка й повернення мають дві фази: спершу горизонталь,
       і лише над точкою — зниження. */
    switch (in.opcode) {
        case Opcode::NavRtl: {
            GeoPoint p = home_;
            p.alt_m = distance_sq(t.position, home_) > r2 ? kRtlAltM : 0.0F;
            out_.target = p;
            break;
        }
        case Opcode::NavLand: {
            GeoPoint p = item_point(in, t);
            p.alt_m = distance_sq(t.position, p) > r2 ? t.position.alt_m : 0.0F;
            out_.target = p;
            break;
        }
        default:
            out_.target = item_point(in, t);
            break;
    }
}

bool MissionVm::nav_complete(const Telemetry& t) noexcept
{
    const Instruction& in = code_[nav_pc_];
    const float r  = accept_radius(in);
    const float r2 = r * r;
    const float d2 = distance_sq(t.position, out_.target);

    switch (in.opcode) {
        case Opcode::NavTakeoff:
            return t.position.alt_m >= out_.target.alt_m - kTakeoffTolM;

        case Opcode::NavLand:
        case Opcode::NavRtl:
            return d2 <= r2 && t.position.alt_m <= kTouchdownAltM;

        case Opcode::NavWaypoint:
        case Opcode::NavLoiterTime: {
            if (d2 > r2) {
                nav_reached_ = false;
                return false;
            }
            /* p1 — час утримання над точкою, секунди. */
            const auto hold_ms = in.p1 > 0
                               ? static_cast<std::uint32_t>(in.p1) * 1000U : 0U;
            if (!nav_reached_) {
                nav_reached_    = true;
                loiter_started_ = t.now;
            }
            return t.now.since(loiter_started_) >= hold_ms;
        }

        default:
            return true;
    }
}

void MissionVm::arm_nav(std::uint16_t pc, const Telemetry& t) noexcept
{
    nav_pc_         = pc;
    nav_active_     = true;
    nav_reached_    = false;
    loiter_started_ = t.now;
    item_started_   = t.now;   /* сторожовий таймер пункту */
    nav_update(t);
}

std::optional<std::size_t> MissionVm::slot_for(std::uint16_t pc,
                                               std::int32_t repeats) noexcept
{
    for (std::size_t i = 0; i < jumps_.size(); ++i) {
        if (jumps_[i].used && jumps_[i].pc == pc) {
            return i;
        }
    }
    for (std::size_t i = 0; i < jumps_.size(); ++i) {
        if (!jumps_[i].used) {
            /* Запису немає — заряджаємо слот повним repeat_count із Flash.
               Саме через це внутрішній цикл перезаряджається на кожному
               витку зовнішнього. */
            jumps_[i] = JumpSlot{ .pc = pc, .remaining = repeats, .used = true };
            return i;
        }
    }
    return std::nullopt;   /* верифікатор такого пропустити не мав */
}

MissionVm::DoResult MissionVm::exec_jump(const Instruction& in) noexcept
{
    const auto idx = slot_for(do_pc_, static_cast<std::int32_t>(in.p2));
    if (!idx) {
        abort_mission(Status::AbortJumpBudget);
        return DoResult::Abort;
    }
    JumpSlot& slot = jumps_[*idx];

    if (slot.remaining == 0) {
        /* Цикл вичерпано: запис інвалідуємо й крокуємо далі. */
        slot.used = false;
        return DoResult::Next;
    }
    if (total_jumps_ >= kMaxTotalJumps) {
        abort_mission(Status::AbortJumpBudget);
        return DoResult::Abort;
    }

    if (slot.remaining > 0) {
        --slot.remaining;   /* -1 лишається -1: нескінченний цикл */
    }
    ++total_jumps_;
    do_pc_ = static_cast<std::uint16_t>(in.p1);
    return DoResult::Jumped;
}

bool MissionVm::battery_low(const Telemetry& t, float threshold_pct) const noexcept
{
    /* Основне джерело — SoC із кулонівського лічильника; фільтрована
       напруга страхує, поки лічильник не відкалібрований. Сира напруга
       не бере участі взагалі. */
    if (t.battery_soc_pct <= threshold_pct) {
        return true;
    }
    const auto filtered = battery_.value();
    return filtered && *filtered <= kBatMinV;
}

MissionVm::DoResult MissionVm::exec_do(const Instruction& in, const Telemetry& t) noexcept
{
    switch (in.opcode) {
        case Opcode::DoChangeSpeed:
            out_.speed_mps = static_cast<float>(in.p2);
            return DoResult::Next;

        case Opcode::DoSetServo:
            /* Канал і межі PWM перевірив верифікатор при завантаженні. */
            out_.servo_pwm[static_cast<std::size_t>(in.p1) - 1] =
                static_cast<std::uint16_t>(in.p2);
            return DoResult::Next;

        case Opcode::JumpIfBatteryLow:
            /* Переходи чіпають навігаційну ціль, тому чекають, поки
               поточна NAV-команда завершиться. */
            if (nav_active_) {
                return DoResult::Hold;
            }
            if (!battery_low(t, static_cast<float>(in.p1))) {
                return DoResult::Next;
            }
            do_pc_ = static_cast<std::uint16_t>(in.p2);
            return DoResult::Jumped;

        case Opcode::DoJump:
            if (nav_active_) {
                return DoResult::Hold;
            }
            return exec_jump(in);

        default:
            return DoResult::Next;
    }
}

bool MissionVm::eval_condition(const Instruction& in, const Telemetry& t) noexcept
{
    const ConditionContext ctx{ .now = t.now,
                                .position = t.position,
                                .next_waypoint = out_.target,
                                .yaw_deg = t.yaw_deg,
                                .battery_soc_pct = t.battery_soc_pct };

    if (!condition_) {
        switch (in.opcode) {
            case Opcode::ConditionDelay:
                condition_ = make_delay(static_cast<float>(in.p1), ctx);
                break;
            case Opcode::ConditionDistance:
                condition_ = make_distance(static_cast<float>(in.p1));
                break;
            case Opcode::ConditionYaw:
                condition_ = make_yaw(static_cast<float>(in.p1),
                                      static_cast<float>(in.p2), ctx);
                break;
            default:
                return true;
        }
    }

    if (const auto yaw = yaw_setpoint(*condition_, ctx)) {
        out_.yaw_setpoint_deg = yaw;
    }
    if (!is_met(*condition_, ctx)) {
        return false;   /* блокує ЛИШЕ чергу DO, апарат летить далі */
    }

    out_.yaw_setpoint_deg.reset();
    condition_.reset();
    return true;
}

/* Конвеєр допоміжних дій: за один такт вичитує все, що лежить між
   поточною NAV-командою та наступною, поки не впреться в незакриту
   умову або в чергову NAV. */
void MissionVm::pump_do_queue(const Telemetry& t) noexcept
{
    while (do_pc_ < len_ && status_ == Status::Running) {
        const Instruction& in = code_[do_pc_];

        if (is_nav(in.opcode)) {
            if (nav_active_) {
                return;   /* попередня ціль ще не досягнута */
            }
            arm_nav(do_pc_, t);
            ++do_pc_;
            continue;     /* і одразу читаємо DO-хвіст за нею */
        }

        if (is_condition(in.opcode)) {
            if (!eval_condition(in, t)) {
                return;
            }
            ++do_pc_;
            continue;
        }

        switch (exec_do(in, t)) {
            case DoResult::Next:   ++do_pc_; break;
            case DoResult::Jumped: break;
            case DoResult::Hold:   return;
            case DoResult::Abort:  return;
        }
    }
}

void MissionVm::tick(const Telemetry& t) noexcept
{
    if (status_ != Status::Running && status_ != Status::Paused) {
        return;
    }

    const float dt_s = static_cast<float>(t.now.since(last_tick_)) / 1000.0F;
    last_tick_ = t.now;
    battery_.update(t.battery_v, dt_s);

    /* Рівень 3 — перший за пріоритетом: апаратна відмова вища за місію. */
    if (!t.gnss_ok || !t.link_ok) {
        abort_mission(Status::AbortFailsafe);
        return;
    }

    if (status_ == Status::Paused) {
        /* autocontinue = 0: тримаємо зависання над досягнутою точкою
           й чекаємо MISSION_START або MISSION_SET_CURRENT з НСУ. */
        return;
    }

    /* Рівень 2 — таймаут на пункт: недосяжна умова не вішає місію назавжди. */
    if (t.now.since(item_started_) > kItemTimeoutMs) {
        abort_mission(Status::AbortItemTimeout);
        return;
    }

    pump_do_queue(t);
    if (status_ != Status::Running) {
        return;
    }

    if (nav_active_) {
        nav_update(t);
        if (nav_complete(t)) {
            const Instruction& nav = code_[nav_pc_];
            nav_active_ = false;

            if (nav.opcode == Opcode::NavLand || nav.opcode == Opcode::NavRtl) {
                status_ = Status::Finished;
                return;
            }
            if ((nav.flags & kFlagAutocontinue) == 0U) {
                status_ = Status::Paused;
                return;
            }
            pump_do_queue(t);
        }
    }

    if (status_ == Status::Running && !nav_active_ && do_pc_ >= len_) {
        status_ = Status::Finished;
    }
}

std::string_view describe(LoadError e) noexcept
{
    switch (e) {
        case LoadError::Empty:              return "порожня місія";
        case LoadError::TooManyItems:       return "забагато пунктів";
        case LoadError::UnknownOpcode:      return "невідомий опкод";
        case LoadError::BadJumpTarget:      return "ціль переходу поза межами (INVALID_PARAM1)";
        case LoadError::BadParameter:       return "неприпустимий параметр";
        case LoadError::TooManyJumps:       return "більше стрибків, ніж слотів у RAM";
        case LoadError::JumpNestingTooDeep: return "занадто глибока вкладеність циклів";
    }
    return "?";
}

std::string_view describe(Status s) noexcept
{
    switch (s) {
        case Status::Idle:             return "очікує старту";
        case Status::Running:          return "виконується";
        case Status::Paused:           return "пауза (autocontinue = 0)";
        case Status::Finished:         return "місію завершено";
        case Status::AbortJumpBudget:  return "АВАРІЯ: вичерпано бюджет стрибків";
        case Status::AbortItemTimeout: return "АВАРІЯ: таймаут пункту";
        case Status::AbortFailsafe:    return "АВАРІЯ: failsafe перехопив керування";
    }
    return "?";
}

std::string_view describe(Opcode op) noexcept
{
    switch (op) {
        case Opcode::NavWaypoint:       return "NAV_WAYPOINT";
        case Opcode::NavLoiterTime:     return "NAV_LOITER_TIME";
        case Opcode::NavRtl:            return "NAV_RETURN_TO_LAUNCH";
        case Opcode::NavLand:           return "NAV_LAND";
        case Opcode::NavTakeoff:        return "NAV_TAKEOFF";
        case Opcode::ConditionDelay:    return "CONDITION_DELAY";
        case Opcode::ConditionDistance: return "CONDITION_DISTANCE";
        case Opcode::ConditionYaw:      return "CONDITION_YAW";
        case Opcode::DoJump:            return "DO_JUMP";
        case Opcode::DoChangeSpeed:     return "DO_CHANGE_SPEED";
        case Opcode::DoSetServo:        return "DO_SET_SERVO";
        case Opcode::JumpIfBatteryLow:  return "JUMP_IF_BAT_LOW";
    }
    return "?";
}

}  // namespace mission
