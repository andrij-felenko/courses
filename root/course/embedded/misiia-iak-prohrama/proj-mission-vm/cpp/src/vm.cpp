// vm.cpp — перевірка місії перед зльотом і сам інтерпретатор.
#include "mission/vm.hpp"

#include <cmath>
#include <limits>

namespace mission {
namespace {

// Звести різницю кутів у діапазон [−180; 180]. Робиться арифметикою, а не
// циклом «поки більше 180 — відняти 360»: на зіпсованому вході (курс у мільйон
// градусів, NaN) такий цикл крутився б невизначено довго, а крок машини мусить
// коштувати сталий час.
float wrap_180(float deg) noexcept
{
    if (!std::isfinite(deg)) {
        return std::numeric_limits<float>::quiet_NaN();
    }
    float w = std::fmod(deg + 180.0F, 360.0F);
    if (w < 0.0F) {
        w += 360.0F;
    }
    return w - 180.0F;
}

// NaN у відстані — це рівно те, що приходить, коли GNSS відмовив або
// оцінювач розійшовся.
bool position_valid(const Telemetry &t) noexcept
{
    return std::isfinite(t.dist_to_wp_m);
}

// Хибна позиція ніколи не дає «так»: машина лишиться в очікуванні, доки
// супервізор не вирішить інакше. Прапорець навігатора без позиції теж не
// приймаємо — він міг застаріти.
bool waypoint_reached(const Telemetry &t, float radius_m) noexcept
{
    return position_valid(t) && (t.wp_reached || t.dist_to_wp_m <= radius_m);
}

bool yaw_reached(float current_deg, float target_deg, float tolerance_deg) noexcept
{
    const float diff = wrap_180(current_deg - target_deg);
    return std::isfinite(diff) && std::fabs(diff) <= tolerance_deg;
}

constexpr bool opcode_known(Opcode op) noexcept
{
    switch (op) {
    case Opcode::Halt:
    case Opcode::NavTakeoff:
    case Opcode::NavWaypoint:
    case Opcode::NavLand:
    case Opcode::NavRtl:
    case Opcode::DoSetServo:
    case Opcode::DoChangeSpeed:
    case Opcode::DoJump:
    case Opcode::JumpIfBatLow:
    case Opcode::CondDelay:
    case Opcode::CondDistance:
    case Opcode::CondYaw:
        return true;
    }
    return false;
}

// Інструкція, після якої виконання не продовжується. Місія мусить нею
// закінчуватися — інакше читач байткоду не відрізнить завершену програму від
// обрізаної при передаванні.
constexpr bool is_terminator(Opcode op) noexcept
{
    return op == Opcode::Halt || op == Opcode::NavLand || op == Opcode::NavRtl;
}

std::expected<void, LoadError> validate(std::span<const Instruction> code) noexcept
{
    unsigned loops = 0;

    for (const Instruction &in : code) {
        if (!opcode_known(in.opcode)) {
            return std::unexpected(LoadError::BadOpcode);
        }

        const auto len = static_cast<std::int16_t>(code.size());

        switch (in.opcode) {
        case Opcode::NavTakeoff:
            if (!std::isfinite(in.alt_m) || in.alt_m <= 0.0F) {
                return std::unexpected(LoadError::BadParam);
            }
            break;

        case Opcode::NavWaypoint:
            if (!std::isfinite(in.alt_m)) {
                return std::unexpected(LoadError::BadParam);
            }
            // Координати поза глобусом означають зіпсоване передавання.
            if (in.lat_1e7 < -900'000'000 || in.lat_1e7 > 900'000'000 ||
                in.lon_1e7 < -1'800'000'000 || in.lon_1e7 > 1'800'000'000) {
                return std::unexpected(LoadError::BadParam);
            }
            break;

        case Opcode::DoSetServo:
            if (in.param1 < 1 || in.param1 > 16 || in.param2 < 800 || in.param2 > 2200) {
                return std::unexpected(LoadError::BadParam);
            }
            break;

        case Opcode::DoChangeSpeed:
            if (in.param2 < 10 || in.param2 > 3000) {
                return std::unexpected(LoadError::BadParam);
            }
            break;

        case Opcode::DoJump:
            if (in.param1 < 0 || in.param1 >= len) {
                return std::unexpected(LoadError::BadJump);
            }
            if (in.param2 < 1) {
                return std::unexpected(LoadError::BadParam);
            }
            if (++loops > kMaxLoopSlots) {
                return std::unexpected(LoadError::TooManyLoops);
            }
            break;

        case Opcode::JumpIfBatLow:
            if (in.param1 < 1 || in.param1 > 99) {
                return std::unexpected(LoadError::BadParam);
            }
            if (in.param2 < 0 || in.param2 >= len) {
                return std::unexpected(LoadError::BadJump);
            }
            break;

        case Opcode::CondDelay:
            if (in.param1 < 0 || in.param1 > 3600) {
                return std::unexpected(LoadError::BadParam);
            }
            break;

        case Opcode::CondDistance:
            if (in.param1 <= 0) {
                return std::unexpected(LoadError::BadParam);
            }
            break;

        case Opcode::CondYaw:
            if (in.param1 < -180 || in.param1 > 360) {
                return std::unexpected(LoadError::BadParam);
            }
            break;

        default:
            break;
        }
    }

    if (!is_terminator(code.back().opcode)) {
        return std::unexpected(LoadError::NoTerminator);
    }
    return {};
}

} // namespace

// ------------------------------------------------------------- LoopTable

LoopTable::Slot *LoopTable::acquire(std::uint16_t jump_pc, std::uint16_t repeats) noexcept
{
    for (Slot &s : slots_) {
        if (s.active && s.jump_pc == jump_pc) {
            return &s;
        }
    }
    for (Slot &s : slots_) {
        if (!s.active) {
            s = Slot{.jump_pc = jump_pc, .remaining = repeats, .active = true};
            return &s;
        }
    }
    return nullptr;
}

void LoopTable::release(std::uint16_t jump_pc) noexcept
{
    for (Slot &s : slots_) {
        if (s.active && s.jump_pc == jump_pc) {
            s.active = false;
            return;
        }
    }
}

// -------------------------------------------------------------- Vm

std::expected<void, LoadError> Vm::load(std::span<const Instruction> code) noexcept
{
    if (code.empty()) {
        return std::unexpected(LoadError::Empty);
    }
    if (code.size() > kMaxInstructions) {
        return std::unexpected(LoadError::TooLong);
    }
    if (!home_) {
        return std::unexpected(LoadError::NoHome);
    }
    if (auto verdict = validate(code); !verdict) {
        return verdict;
    }

    program_     = code;
    pc_          = 0;
    status_      = Status::Running;
    entered_     = false;
    entry_time_  = Millis{0};
    total_jumps_ = 0;
    steps_       = 0;
    loops_.reset();
    return {};
}

Millis Vm::wait_elapsed(Millis now) const noexcept
{
    return entered_ ? now - entry_time_ : Millis{0};
}

// Аварійна зупинка: знімаємо чинні уставки, щоб апарат не летів далі за
// інерцією плану, і піднімаємо прапорець супервізорові Failsafe. Рішення про
// посадку чи повернення ухвалює він — машина своє вже сказала.
void Vm::fail(Actuators &act, Status s) noexcept
{
    status_               = s;
    act.nav_valid         = false;
    act.target_speed_mps  = 0.0F;
    act.failsafe_request  = true;
}

void Vm::advance() noexcept
{
    ++pc_;
    status_ = Status::Running;
}

// Висота уставки завжди віддається назовні відносно домашньої точки: саме в
// цій системі відліку працює контур висоти.
float Vm::target_alt_rel(const Instruction &in) const noexcept
{
    return has(in.flags, Flag::AltAbsolute) ? in.alt_m - home_->alt_m : in.alt_m;
}

Status Vm::step(const Telemetry &telem, Actuators &act, Millis now) noexcept
{
    if (!is_active(status_)) {
        return status_;
    }
    if (pc_ >= program_.size()) {
        status_ = Status::Completed;
        return status_;
    }

    const Instruction  &in          = program_[pc_];
    const std::uint16_t pc_before   = pc_;
    const bool          first_visit = !entered_;

    if (first_visit) {
        entered_    = true;
        entry_time_ = now;
    }
    ++steps_;

    switch (in.opcode) {
    case Opcode::Halt:
        act.nav_valid = false;
        status_       = Status::Completed;
        break;

    case Opcode::NavTakeoff:
        if (first_visit) {
            act.nav_valid      = true;
            act.target_lat_1e7 = home_->lat_1e7;
            act.target_lon_1e7 = home_->lon_1e7;
            act.target_alt_m   = target_alt_rel(in);
            status_            = Status::WaitingNav;
        }
        if (has(in.flags, Flag::AutoContinue)) {
            advance();
            break;
        }
        if (std::isfinite(telem.alt_m) &&
            telem.alt_m >= act.target_alt_m * kTakeoffAltFraction) {
            advance();
        }
        break;

    case Opcode::NavWaypoint:
        if (first_visit) {
            act.nav_valid      = true;
            act.target_lat_1e7 = in.lat_1e7;
            act.target_lon_1e7 = in.lon_1e7;
            act.target_alt_m   = target_alt_rel(in);
            status_            = Status::WaitingNav;
        }
        // AutoContinue: уставку видано — і одразу далі. Апарат летить до точки,
        // а програма тим часом стоїть на наступній інструкції: так умова «за
        // 30 метрів до точки» встигає спрацювати в дорозі.
        if (has(in.flags, Flag::AutoContinue)) {
            advance();
            break;
        }
        // Позиції немає — лишаємося в WaitingNav скільки завгодно довго.
        // Таймаут не наша справа: його міряє супервізор за wait_elapsed().
        if (waypoint_reached(telem, kWaypointRadiusM)) {
            advance();
        }
        break;

    case Opcode::NavLand:
        act.nav_valid      = true;
        act.target_lat_1e7 = telem.lat_1e7;
        act.target_lon_1e7 = telem.lon_1e7;
        act.target_alt_m   = 0.0F;
        act.land_triggered = true;
        status_            = Status::Completed;
        break;

    case Opcode::NavRtl:
        act.nav_valid      = true;
        act.target_lat_1e7 = home_->lat_1e7;
        act.target_lon_1e7 = home_->lon_1e7;
        act.target_alt_m   = kRtlAltM;
        act.rtl_triggered  = true;
        status_            = Status::Completed;
        break;

    case Opcode::DoSetServo:
        act.servo_channel = static_cast<std::uint8_t>(in.param1);
        act.servo_pwm_us  = static_cast<std::uint16_t>(in.param2);
        advance();
        break;

    case Opcode::DoChangeSpeed:
        act.target_speed_mps = static_cast<float>(in.param2) * 0.01F;
        advance();
        break;

    case Opcode::DoJump: {
        // Бюджет перевіряємо ПЕРЕД стрибком: інакше остання дозволена ітерація
        // встигла б піти на друге коло.
        if (total_jumps_ >= kMaxTotalJumps) {
            fail(act, Status::ErrorInfiniteLoop);
            break;
        }
        LoopTable::Slot *slot = loops_.acquire(pc_, static_cast<std::uint16_t>(in.param2));
        if (slot == nullptr) {
            fail(act, Status::ErrorOutOfBounds);
            break;
        }
        if (slot->remaining > 0) {
            --slot->remaining;
            ++total_jumps_;
            pc_     = static_cast<std::uint16_t>(in.param1);
            status_ = Status::Running;
        } else {
            loops_.release(pc_);
            advance();
        }
        break;
    }

    case Opcode::JumpIfBatLow:
        // NaN у заряді дає «ні» на будь-яке порівняння — програма йде далі, а
        // рішення про несправний датчик ухвалює супервізор.
        if (telem.battery_soc_pct < static_cast<float>(in.param1)) {
            if (total_jumps_ >= kMaxTotalJumps) {
                fail(act, Status::ErrorInfiniteLoop);
                break;
            }
            ++total_jumps_;
            pc_     = static_cast<std::uint16_t>(in.param2);
            status_ = Status::Running;
        } else {
            advance();
        }
        break;

    case Opcode::CondDelay:
        status_ = Status::WaitingCond;
        if (now - entry_time_ >= std::chrono::seconds{in.param1}) {
            advance();
        }
        break;

    case Opcode::CondDistance:
        status_ = Status::WaitingCond;
        if (position_valid(telem) && telem.dist_to_wp_m <= static_cast<float>(in.param1)) {
            advance();
        }
        break;

    case Opcode::CondYaw:
        status_ = Status::WaitingCond;
        if (yaw_reached(telem.yaw_deg, static_cast<float>(in.param1), kYawToleranceDeg)) {
            advance();
        }
        break;

    default:
        // Сюди можна потрапити лише тоді, коли байткод зіпсувався вже після
        // завантаження — наприклад, збій Flash. Перевірка коштує один перехід,
        // а мовчазне виконання чужого байта коштувало б апарата.
        fail(act, Status::ErrorInvalidOpcode);
        break;
    }

    // Пішли на іншу інструкцію — її одноразові дії ще попереду.
    if (pc_ != pc_before) {
        entered_ = false;
    }
    return status_;
}

// ------------------------------------------------------------------ імена

std::string_view to_string(Status s) noexcept
{
    switch (s) {
    case Status::Idle:               return "IDLE";
    case Status::Running:            return "RUNNING";
    case Status::WaitingNav:         return "WAITING_NAV";
    case Status::WaitingCond:        return "WAITING_COND";
    case Status::Completed:          return "COMPLETED";
    case Status::ErrorInfiniteLoop:  return "ERROR_INFINITE_LOOP";
    case Status::ErrorOutOfBounds:   return "ERROR_OUT_OF_BOUNDS";
    case Status::ErrorInvalidOpcode: return "ERROR_INVALID_OPCODE";
    }
    return "?";
}

std::string_view to_string(LoadError e) noexcept
{
    switch (e) {
    case LoadError::Empty:        return "EMPTY";
    case LoadError::TooLong:      return "TOO_LONG";
    case LoadError::NoHome:       return "NO_HOME";
    case LoadError::BadOpcode:    return "BAD_OPCODE";
    case LoadError::BadParam:     return "BAD_PARAM";
    case LoadError::BadJump:      return "BAD_JUMP";
    case LoadError::TooManyLoops: return "TOO_MANY_LOOPS";
    case LoadError::NoTerminator: return "NO_TERMINATOR";
    }
    return "?";
}

} // namespace mission
