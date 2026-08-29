// vm.hpp — бортова віртуальна машина виконання місії.
//
// Ті самі дві межі, що й у версії мовою C, але висловлені типами:
//
//   · пам'ять не виділяється ніде. std::span дивиться на байткод у Flash і не
//     копіює його, std::array тримає лічильники циклів, std::expected несе
//     причину відмови без винятків і без купи. Жодного new за весь політ;
//
//   · Vm::step() виконує рівно одну інструкцію й повертається. Циклів, чия
//     довжина залежить від даних, у машині немає.
//
// Потрібен C++23 (std::expected). Час — std::chrono::milliseconds: 64-бітний
// лічильник не переповниться за час життя апарата, тож на відміну від
// 32-бітних тиків його різницю можна брати прямо.
#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>
#include <type_traits>
#include <utility>

namespace mission {

using Millis = std::chrono::milliseconds;

inline constexpr std::uint16_t kMaxInstructions = 256;
inline constexpr std::uint16_t kMaxLoopSlots    = 16;
inline constexpr std::uint32_t kMaxTotalJumps   = 256;

inline constexpr float kWaypointRadiusM   = 2.0F;
inline constexpr float kYawToleranceDeg   = 5.0F;
inline constexpr float kTakeoffAltFraction = 0.95F;
inline constexpr float kRtlAltM            = 30.0F;

// Числа опкодів зафіксовані назавжди: за ними наземна станція складає той
// самий байткод, що читає борт. Клас операції видно по старшому півбайту.
enum class Opcode : std::uint8_t {
    Halt          = 0x00,
    NavTakeoff    = 0x01,
    NavWaypoint   = 0x02,
    NavLand       = 0x03,
    NavRtl        = 0x04,
    DoSetServo    = 0x10,
    DoChangeSpeed = 0x11,
    DoJump        = 0x20,
    JumpIfBatLow  = 0x21,
    CondDelay     = 0x30,
    CondDistance  = 0x31,
    CondYaw       = 0x32,
};

enum class Flag : std::uint8_t {
    // Уставку видано — і одразу наступна інструкція, не чекаючи досягнення.
    // Саме так між двома точками вставляють умову «за 30 метрів до точки».
    AutoContinue = 0x01,
    // alt_m задано над рівнем моря, а не над домашньою точкою.
    AltAbsolute = 0x02,
};

constexpr std::uint8_t operator|(Flag a, Flag b) noexcept
{
    return static_cast<std::uint8_t>(std::to_underlying(a) | std::to_underlying(b));
}

constexpr bool has(std::uint8_t flags, Flag f) noexcept
{
    return (flags & std::to_underlying(f)) != 0;
}

// Рівно 20 байтів із ПРИРОДНИМ вирівнюванням: кожне поле стоїть на своїй межі
// саме, без alignas і без пакування. Упакована структура коштувала б
// невирівняних читань на кожному кроці, а в пам'яті не виграла б нічого —
// байткод і так лежить у Flash.
struct Instruction {
    Opcode        opcode{Opcode::Halt};
    std::uint8_t  flags{};
    std::int16_t  param1{};  // час (с), канал, кут, поріг батареї, індекс
    std::int16_t  param2{};  // повтори, ширина імпульсу (мкс), швидкість (см/с)
    std::int32_t  lat_1e7{}; // широта × 10⁷ — дискретність близько 1 см
    std::int32_t  lon_1e7{};
    float         alt_m{};
};

static_assert(sizeof(Instruction) == 20,
              "інструкція мусить лишатися 20-байтовою: за цим числом наземна "
              "станція нарізає байткод");
static_assert(std::is_trivially_copyable_v<Instruction>);

enum class Status : std::uint8_t {
    Idle,
    Running,
    WaitingNav,
    WaitingCond,
    Completed,
    ErrorInfiniteLoop,
    ErrorOutOfBounds,
    ErrorInvalidOpcode,
};

// Чому місію не взято до виконання. Відхилити програму ДО зльоту дешевше, ніж
// упертися в її ваду посеред польоту.
enum class LoadError : std::uint8_t {
    Empty,
    TooLong,
    NoHome,
    BadOpcode,
    BadParam,
    BadJump,
    TooManyLoops,
    NoTerminator,
};

struct Home {
    std::int32_t lat_1e7{};
    std::int32_t lon_1e7{};
    float        alt_m{}; // над рівнем моря
};

// Знімок стану апарата. Машина його лише читає.
struct Telemetry {
    std::int32_t lat_1e7{};
    std::int32_t lon_1e7{};
    float        alt_m{};        // над домашньою точкою
    float        yaw_deg{};
    float        dist_to_wp_m{}; // до активної уставки; NaN — позиції немає
    float        battery_soc_pct{};
    bool         wp_reached{};
    // Машина сюди НЕ дивиться: втрата зв'язку з наземною станцією не спиняє
    // автономну програму. Поле тут заради того, хто читає телеметрію далі.
    bool gcs_link_ok{true};
};

// Усе, що машина віддає назовні за такт.
struct Actuators {
    bool          nav_valid{};
    std::int32_t  target_lat_1e7{};
    std::int32_t  target_lon_1e7{};
    float         target_alt_m{};     // завжди над домашньою точкою
    float         target_speed_mps{}; // 0 — швидкості не задавали
    std::uint8_t  servo_channel{};
    std::uint16_t servo_pwm_us{};
    bool          rtl_triggered{};
    bool          land_triggered{};
    bool          failsafe_request{}; // машина спинилася аварійно
};

constexpr bool is_error(Status s) noexcept
{
    return s == Status::ErrorInfiniteLoop || s == Status::ErrorOutOfBounds ||
           s == Status::ErrorInvalidOpcode;
}

constexpr bool is_active(Status s) noexcept
{
    return s == Status::Running || s == Status::WaitingNav || s == Status::WaitingCond;
}

std::string_view to_string(Status s) noexcept;
std::string_view to_string(LoadError e) noexcept;

// Лічильники повторів DO_JUMP. Слот прив'язано до АДРЕСИ САМОГО СТРИБКА, а не
// до його цілі: інакше два різні DO_JUMP на ту саму мітку ділили б один
// лічильник і вкладені цикли рахувалися б неправильно.
class LoopTable {
public:
    struct Slot {
        std::uint16_t jump_pc{};
        std::uint16_t remaining{};
        bool          active{};
    };

    void reset() noexcept { slots_ = {}; }

    // Знайти лічильник цього DO_JUMP, а якщо його ще немає — завести. nullptr
    // повертається лише коли вільних слотів немає; у перевіреній програмі це
    // неможливо, бо завантажувач порахував DO_JUMP-и наперед.
    [[nodiscard]] Slot *acquire(std::uint16_t jump_pc, std::uint16_t repeats) noexcept;

    // Слот вичерпаного циклу саме звільняємо, а не лишаємо з нулем: коли
    // зовнішній цикл заведе внутрішній на друге коло, той мусить почати
    // рахувати спочатку.
    void release(std::uint16_t jump_pc) noexcept;

private:
    std::array<Slot, kMaxLoopSlots> slots_{};
};

class Vm {
public:
    // Домашню точку задають ДО load(): від неї рахується відносна висота й до
    // неї повертає RTL.
    void set_home(Home home) noexcept { home_ = home; }

    // Байткод не копіюється — span мусить лишатися дійсним увесь політ.
    [[nodiscard]] std::expected<void, LoadError> load(std::span<const Instruction> code) noexcept;

    // Один такт. Викликається періодично (20–50 Гц) і ніколи не блокує: якщо
    // чекати ще рано, повертає Waiting* і віддає процесор.
    Status step(const Telemetry &telem, Actuators &act, Millis now) noexcept;

    [[nodiscard]] Status        status() const noexcept { return status_; }
    [[nodiscard]] std::uint16_t pc() const noexcept { return pc_; }
    [[nodiscard]] std::uint32_t total_jumps() const noexcept { return total_jumps_; }
    [[nodiscard]] std::uint32_t steps_executed() const noexcept { return steps_; }

    // Скільки машина сидить на поточній інструкції. Саме за цим числом
    // ЗОВНІШНІЙ супервізор вирішує, що очікування затяглося (наприклад, GNSS
    // не повертається): сама машина таймаутів не має й чекати може вічно.
    [[nodiscard]] Millis wait_elapsed(Millis now) const noexcept;

private:
    void  fail(Actuators &act, Status s) noexcept;
    void  advance() noexcept;
    float target_alt_rel(const Instruction &in) const noexcept;

    std::span<const Instruction> program_{};
    std::optional<Home>          home_{};

    std::uint16_t pc_{};
    Status        status_{Status::Idle};

    // Чи зроблено для поточної інструкції одноразову дію — видано уставку,
    // засічено час. Скидається на кожному переході.
    bool   entered_{};
    Millis entry_time_{};

    std::uint32_t total_jumps_{};
    std::uint32_t steps_{};
    LoopTable     loops_{};
};

} // namespace mission
