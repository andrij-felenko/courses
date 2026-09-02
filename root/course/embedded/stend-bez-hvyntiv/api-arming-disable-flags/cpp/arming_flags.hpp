// Довідник прапорців Betaflight. Збирається як C++23 (std::expected).
#pragma once

#include <array>
#include <bit>
#include <cstdint>
#include <expected>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace bf {

enum class Flag : std::uint8_t {
    NoGyro = 0,
    Failsafe,
    RxFailsafe,
    BadRxRecovery,
    BoxFailsafe,
    Throttle,
    Cli,
    CmsMenu,
    OsdMenu,
    RollPitchClipped,
    ServoInit,
    MotorProtocol,
    AccCal,
    MotorTest,
    ArmSwitch,
    Msp,
    Paralyze,
    Gps,
    Rescue,
    RpmFilter,
    RebootRequired,
    NoPrearm,
    CpuLoad,
    Calibrating,
    Count
};

inline constexpr std::size_t kFlagCount = static_cast<std::size_t>(Flag::Count);

struct FlagInfo {
    std::string_view name;    // так прапорець друкує CLI-команда `status`
    std::string_view cause;
    std::string_view remedy;
};

inline constexpr std::array<FlagInfo, kFlagCount> kFlagTable{{
    {"NO_GYRO", "гіроскоп не відповідає по шині SPI",
     "перевірити пайку модуля IMU і живлення 3.3 В"},
    {"FAILSAFE", "активний режим Failsafe: валідних кадрів від приймача немає",
     "увімкнути передавач, перевірити живлення приймача"},
    {"RX_FAILSAFE", "приймач сам утримує власний прапорець failsafe",
     "відновити зв'язок пульта з радіомодулем (CRSF/ELRS/SBUS)"},
    {"BAD_RX_RECOVERY", "лінк щойно повернувся, триває захисна секунда",
     "віднести пульт на 1.5-2 м від апарата й дочекатися чистої секунди"},
    {"BOXFAILSAFE", "AUX-канал переведений у зону аварійного Failsafe",
     "перевести тумблер Failsafe на пульті у вимкнений стан"},
    {"THROTTLE", "стік газу вище порога min_check",
     "опустити газ до кінця (1000 мкс) або відкалібрувати канал"},
    {"CLI", "контролер у режимі командного рядка",
     "ввести exit або від'єднати термінал"},
    {"CMS_MENU", "відкрито конфігураційне меню на OSD",
     "закрити меню пунктом Exit"},
    {"OSD_MENU", "активний службовий екран телеметрії",
     "вийти з графічного режиму налаштування"},
    {"ROLLPITCH_CLIPPED", "стіки крену/тангажу вийшли за діапазон каналу",
     "відкалібрувати кінцеві точки 1000-2000 мкс на пульті"},
    {"SERVO_INIT", "сервоприводи ще не зайняли нульове положення",
     "дочекатися завершення стартового позиціювання"},
    {"MOTOR_PROTOCOL", "вибраний протокол ESC не лягає на таймери виходів",
     "перевірити конфігурацію DShot/PWM і ресурси таймерів"},
    {"ACC_CAL", "акселерометр не має збережених калібрувальних коефіцієнтів",
     "провести калібрування на рівній поверхні"},
    {"MOTOR_TEST", "увімкнено стендовий режим тестування двигунів",
     "вимкнути перемикач Enable motor testing у конфігураторі"},
    {"ARM_SWITCH", "плату ввімкнено з уже піднятим тумблером Arming",
     "фізично опустити тумблер у стан Disarm"},
    {"MSP", "конфігуратор утримує монопольний доступ",
     "закрити сесію GUI або від'єднати USB"},
    {"PARALYZE", "активовано режим повного блокування апарата",
     "перезавантажити контролер живленням"},
    {"GPS", "немає 3D-фікса, а режим GPS-Rescue вимагає його для армінгу",
     "зняти вимогу GPS для армінгу або вийти на відкрите місце"},
    {"RESC", "AUX-канал переведений у положення GPS-Rescue",
     "вимкнути тумблер повернення додому"},
    {"RPMFILTER", "увімкнено RPM-фільтр, а регулятори не віддають телеметрію обертів",
     "живити ESC від силової батареї, а не лише від USB"},
    {"REBOOT_REQUIRED", "змінені параметри потребують перезавантаження",
     "надіслати save або перезапустити плату"},
    {"NOPREARM", "не затиснуто запобіжний перемикач Prearm",
     "затиснути Prearm перед тумблером Arm"},
    {"LOAD", "середнє завантаження процесора вище безпечного ліміту",
     "знизити частоту PID-циклу або перемкнути DShot600 на DShot300"},
    {"CALIBRATING", "триває стартове калібрування гіроскопа",
     "покласти апарат нерухомо на 3-5 секунд"},
}};

[[nodiscard]] constexpr const FlagInfo& info(Flag flag) noexcept
{
    return kFlagTable[static_cast<std::size_t>(flag)];
}

[[nodiscard]] constexpr std::optional<Flag> flagByName(std::string_view name) noexcept
{
    for (std::size_t i = 0; i < kFlagCount; ++i) {
        if (kFlagTable[i].name == name) {
            return static_cast<Flag>(i);
        }
    }
    return std::nullopt;
}

// Маска armingDisableFlags. Тримає всі 32 біти, зокрема й ті, яких
// довідник не знає: прошивка на платі може бути новішою.
class Mask {
public:
    constexpr Mask() noexcept = default;
    constexpr explicit Mask(std::uint32_t raw) noexcept : bits_{raw} {}

    constexpr Mask& set(Flag flag, bool on = true) noexcept
    {
        const std::uint32_t bit = std::uint32_t{1} << static_cast<unsigned>(flag);
        bits_ = on ? (bits_ | bit) : (bits_ & ~bit);
        return *this;
    }

    [[nodiscard]] constexpr bool test(Flag flag) const noexcept
    {
        return ((bits_ >> static_cast<unsigned>(flag)) & 1u) != 0u;
    }

    [[nodiscard]] constexpr bool armingAllowed() const noexcept { return bits_ == 0; }
    [[nodiscard]] constexpr std::uint32_t raw() const noexcept { return bits_; }
    [[nodiscard]] constexpr int count() const noexcept { return std::popcount(bits_); }

    [[nodiscard]] std::vector<Flag> raised() const;
    [[nodiscard]] std::vector<unsigned> unknownBits() const;

    friend constexpr bool operator==(Mask, Mask) noexcept = default;

private:
    std::uint32_t bits_{};
};

struct CliStatus {
    Mask mask;
    std::vector<std::string> unknownNames;   // прошивка новіша за довідник
};

enum class CliError { NoFlagsField };

[[nodiscard]] std::string_view describe(CliError error) noexcept;

// Розбір рядка `Arming disable flags: THROTTLE CLI MSP` з виводу команди status.
[[nodiscard]] std::expected<CliStatus, CliError> parseCliStatus(std::string_view line);

// Багаторядковий звіт: біт, назва, причина, рецепт.
[[nodiscard]] std::string explain(Mask mask);

}  // namespace bf
