#include <cstdint>
#include <string_view>
#include <array>
#include <bitset>

namespace flight_safety {

enum class ArmingFlag : uint8_t {
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

struct FlagDescriptor {
    ArmingFlag flag;
    std::string_view name;
    std::string_view remedy;
};

inline constexpr std::array<FlagDescriptor, 24> kFlagRegistry = {{
    {ArmingFlag::NoGyro, "NO_GYRO", "Перевірити живлення та пайку шини SPI гіроскопа"},
    {ArmingFlag::Failsafe, "FAILSAFE", "Увімкнути пульт керування та перевірити лінк"},
    {ArmingFlag::RxFailsafe, "RX_FAILSAFE", "Відновити зв'язок приймача з радіомодулем"},
    {ArmingFlag::BadRxRecovery, "BAD_RX_RECOVERY", "Зачекати 1 с до завершення захисного інтервалу"},
    {ArmingFlag::BoxFailsafe, "BOXFAILSAFE", "Вимкнути аварійний AUX-тумблер Failsafe на пульті"},
    {ArmingFlag::Throttle, "THROTTLE", "Опустити стік газу в крайнє нижнє положення"},
    {ArmingFlag::Cli, "CLI", "Ввести команду exit у терміналі або від'єднати CLI"},
    {ArmingFlag::CmsMenu, "CMS_MENU", "Закрити екранне меню конфігурації OSD"},
    {ArmingFlag::OsdMenu, "OSD_MENU", "Вийти з меню службових налаштувань графіки"},
    {ArmingFlag::RollPitchClipped, "ROLLPITCH_CLIPPED", "Відкалібрувати межі каналів керування 1000..2000 мкс"},
    {ArmingFlag::ServoInit, "SERVO_INIT", "Дочекатися стартового калібрування приводів"},
    {ArmingFlag::MotorProtocol, "MOTOR_PROTOCOL", "Перевірити відповідність DShot таймерам виходів"},
    {ArmingFlag::AccCal, "ACC_CAL", "Провести калібрування акселерометра на столі"},
    {ArmingFlag::MotorTest, "MOTOR_TEST", "Вимкнути вкладку тестування моторів у конфігураторі"},
    {ArmingFlag::ArmSwitch, "ARM_SWITCH", "Перевести тумблер Arming у стан Disarm"},
    {ArmingFlag::Msp, "MSP", "Закрити сесію конфігуратора або від'єднати USB-кабель"},
    {ArmingFlag::Paralyze, "PARALYZE", "Перезавантажити контролер живленням"},
    {ArmingFlag::Gps, "GPS", "Отримати 3D-фікс або вимкнути блокування GPS-Rescue"},
    {ArmingFlag::Rescue, "RESC", "Вимкнути тумблер повернення додому"},
    {ArmingFlag::RpmFilter, "RPMFILTER", "Підключити силову LiPo батарею для живлення ESC"},
    {ArmingFlag::RebootRequired, "REBOOT_REQUIRED", "Зберегти параметри та перезавантажити плату"},
    {ArmingFlag::NoPrearm, "NOPREARM", "Затиснути запобіжну кнопку/тумблер Prearm"},
    {ArmingFlag::CpuLoad, "LOAD", "Зменшити частоту циклу PID loop у налаштуваннях"},
    {ArmingFlag::Calibrating, "CALIBRATING", "Забезпечити повну нерухомість плати на 3 секунди"}
}};

class ArmingStatusChecker {
public:
    explicit constexpr ArmingStatusChecker(uint32_t rawMask) noexcept : mask_(rawMask) {}

    [[nodiscard]] constexpr bool isArmedAllowed() const noexcept {
        return mask_.none();
    }

    [[nodiscard]] constexpr bool hasFlag(ArmingFlag flag) const noexcept {
        return mask_.test(static_cast<size_t>(flag));
    }

private:
    std::bitset<32> mask_;
};

} // namespace flight_safety
