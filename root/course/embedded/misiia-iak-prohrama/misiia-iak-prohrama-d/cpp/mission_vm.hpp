#pragma once

#include <array>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>

#include "conditions.hpp"
#include "geo.hpp"

namespace mission {

/* Опкоди байткоду — це числа MAV_CMD: транслятор із MISSION_ITEM_INT
   лишається тривіальним, а байткод читається поруч із протоколом. */
enum class Opcode : std::uint8_t {
    NavWaypoint       = 16,
    NavLoiterTime     = 19,
    NavRtl            = 20,
    NavLand           = 21,
    NavTakeoff        = 22,
    ConditionDelay    = 112,
    ConditionDistance = 114,
    ConditionYaw      = 115,
    DoJump            = 177,
    DoChangeSpeed     = 178,
    DoSetServo        = 183,
    JumpIfBatteryLow  = 240   /* поза MAVLink: вендорний діапазон */
};

inline constexpr std::uint8_t kFlagAutocontinue = 0x01U;

/* Інструкція байткоду. Значущих байтів 18, але між p2 та lat_e7
   компілятор лишає 2 байти вирівнювання під int32 — саме тому
   інструкція важить рівно 20. */
struct Instruction {
    Opcode       opcode{Opcode::NavWaypoint};
    std::uint8_t flags{kFlagAutocontinue};
    std::int16_t p1{0};
    std::int16_t p2{0};
    std::int32_t lat_e7{0};
    std::int32_t lon_e7{0};
    float        alt_m{0.0F};
};

static_assert(sizeof(Instruction) == 20,
              "інструкція місії мусить лишатися 20-байтною");

enum class LoadError {
    Empty,
    TooManyItems,
    UnknownOpcode,
    BadJumpTarget,      /* → MAV_MISSION_INVALID_PARAM1 */
    BadParameter,
    TooManyJumps,
    JumpNestingTooDeep
};

enum class Status {
    Idle,
    Running,
    Paused,             /* autocontinue = 0: чекаємо команди з НСУ */
    Finished,
    AbortJumpBudget,
    AbortItemTimeout,
    AbortFailsafe
};

[[nodiscard]] std::string_view describe(LoadError e) noexcept;
[[nodiscard]] std::string_view describe(Status s) noexcept;
[[nodiscard]] std::string_view describe(Opcode op) noexcept;

struct Telemetry {
    Millis   now{};
    GeoPoint position{};
    float    yaw_deg{0.0F};
    float    battery_v{0.0F};
    float    battery_soc_pct{100.0F};
    bool     gnss_ok{true};
    bool     link_ok{true};
};

/* Те, що VM віддає решті системи: прості дані, а не інтерфейс.
   Контур навігації читає уставку, драйвер сервоприводів — PWM. */
struct Outputs {
    GeoPoint             target{};
    float                speed_mps{12.0F};
    std::optional<float> yaw_setpoint_deg{};   /* порожньо — курс не нав'язуємо */
    std::array<std::uint16_t, 4> servo_pwm{};
};

class MissionVm {
public:
    static constexpr std::size_t   kMaxItems       = 64;
    static constexpr std::size_t   kMaxJumpSlots   = 16;
    static constexpr std::uint16_t kMaxTotalJumps  = 256;
    static constexpr int           kMaxJumpDepth   = 2;
    static constexpr std::uint32_t kItemTimeoutMs  = 120'000;
    static constexpr std::size_t   kServoChannels  = 4;

    /* Рівень 1 захисту: статичний верифікатор. Місія, що його не
       пройшла, взагалі не стає об'єктом VM — конструктор приватний. */
    [[nodiscard]] static std::expected<MissionVm, LoadError>
    load(std::span<const Instruction> program);

    void start(GeoPoint home, Millis now) noexcept;
    void tick(const Telemetry& t) noexcept;

    void resume() noexcept;                     /* MAV_CMD_MISSION_START */
    void set_current(std::uint16_t seq) noexcept; /* MISSION_SET_CURRENT */
    void failsafe() noexcept;                   /* аварія рівня 3 */

    [[nodiscard]] Status status() const noexcept { return status_; }
    [[nodiscard]] bool stopped() const noexcept;
    [[nodiscard]] const Outputs& outputs() const noexcept { return out_; }

    /* Порожньо, поки жодна NAV-команда не активна. */
    [[nodiscard]] std::optional<std::uint16_t> active_nav() const noexcept;
    [[nodiscard]] Opcode opcode_at(std::uint16_t seq) const noexcept;

private:
    MissionVm() = default;

    struct JumpSlot {
        std::uint16_t pc{0};
        std::int32_t  remaining{0};   /* -1 — нескінченний цикл */
        bool          used{false};
    };

    enum class DoResult { Next, Jumped, Hold, Abort };

    void       arm_nav(std::uint16_t pc, const Telemetry& t) noexcept;
    void       nav_update(const Telemetry& t) noexcept;
    [[nodiscard]] bool nav_complete(const Telemetry& t) noexcept;
    void       pump_do_queue(const Telemetry& t) noexcept;
    [[nodiscard]] bool eval_condition(const Instruction& in, const Telemetry& t) noexcept;
    [[nodiscard]] DoResult exec_do(const Instruction& in, const Telemetry& t) noexcept;
    [[nodiscard]] DoResult exec_jump(const Instruction& in) noexcept;
    [[nodiscard]] std::optional<std::size_t> slot_for(std::uint16_t pc,
                                                      std::int32_t repeats) noexcept;
    [[nodiscard]] bool battery_low(const Telemetry& t, float threshold_pct) const noexcept;
    void       abort_mission(Status why) noexcept;

    std::array<Instruction, kMaxItems> code_{};
    std::uint16_t len_{0};

    /* Два паралельних показники стану — як у AP_Mission. */
    std::uint16_t nav_pc_{0};
    std::uint16_t do_pc_{0};
    bool          nav_active_{false};
    bool          nav_reached_{false};
    Millis        loiter_started_{};

    std::optional<Condition>            condition_{};
    std::array<JumpSlot, kMaxJumpSlots> jumps_{};
    std::uint16_t                       total_jumps_{0};

    Millis        item_started_{};
    Millis        last_tick_{};
    BatteryFilter battery_{3.0F};

    GeoPoint home_{};
    Outputs  out_{};
    Status   status_{Status::Idle};
};

}  // namespace mission
