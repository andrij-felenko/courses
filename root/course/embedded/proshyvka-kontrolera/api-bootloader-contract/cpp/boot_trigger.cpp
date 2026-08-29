#include "boot_trigger.hpp"

#include <cstring>

namespace fc::boot {
namespace {

// STM32F4: резервні регістри в домені RTC (RTC_BKP0R = 0x40002850).
// У STM32H7 той самий масив живе в блоці TAMP (0x5800B100) — інша база,
// та сама логіка.
constexpr std::uintptr_t kRccBase = 0x4002'3800;
constexpr std::uintptr_t kPwrBase = 0x4000'7000;
constexpr std::uintptr_t kRtcBase = 0x4000'2800;
constexpr std::uintptr_t kScbAircr = 0xE000'ED0C;
constexpr std::uint32_t kPwrCrDbp = 1u << 8;
constexpr std::uint32_t kRccPwrEn = 1u << 28;

volatile std::uint32_t& reg(std::uintptr_t address) noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(address);
}

// RAII замість пари «зняв захист — не забудь поставити»: вихід із будь-якої
// гілки сам закриває резервний домен.
class BackupAccess {
public:
    BackupAccess() noexcept
    {
        reg(kRccBase + 0x40) |= kRccPwrEn;  // APB1ENR.PWREN
        static_cast<void>(reg(kRccBase + 0x40));  // такт шини APB
        was_open_ = (reg(kPwrBase) & kPwrCrDbp) != 0;
        reg(kPwrBase) |= kPwrCrDbp;
    }

    ~BackupAccess()
    {
        if (!was_open_) {
            reg(kPwrBase) &= ~kPwrCrDbp;
        }
    }

    BackupAccess(const BackupAccess&) = delete;
    BackupAccess& operator=(const BackupAccess&) = delete;

    static volatile std::uint32_t& backup(unsigned index) noexcept
    {
        return reg(kRtcBase + 0x50 + 4u * index);
    }

private:
    bool was_open_ = false;
};

constexpr bool is_known(std::uint32_t value) noexcept
{
    return value == static_cast<std::uint32_t>(Marker::ForceBootloader)
        || value == static_cast<std::uint32_t>(Marker::BetaflightDfu)
        || value == static_cast<std::uint32_t>(Marker::UsbTouch);
}

}  // namespace

void arm(Marker marker)
{
    BackupAccess access;
    BackupAccess::backup(0) = static_cast<std::uint32_t>(marker);
}

std::optional<Marker> take()
{
    const std::uint32_t value = BackupAccess::backup(0);
    if (!is_known(value)) {
        return std::nullopt;  // сміття або чистий регістр — стартує застосунок
    }

    // Чистимо ОДРАЗУ: зависання в завантажувачі інакше зациклить вхід,
    // і плата вже ніколи не дійде до польотного коду.
    BackupAccess access;
    BackupAccess::backup(0) = 0;
    return static_cast<Marker>(value);
}

void arm_rollback()
{
    BackupAccess access;
    BackupAccess::backup(1) = static_cast<std::uint32_t>(Marker::Rollback);
}

bool take_rollback()
{
    if (BackupAccess::backup(1) != static_cast<std::uint32_t>(Marker::Rollback)) {
        return false;
    }
    BackupAccess access;
    BackupAccess::backup(1) = 0;
    return true;
}

void system_reset() noexcept
{
    // Бар'єр: записи в резервний домен мають лягти до скидання.
    asm volatile("dsb 0xF" ::: "memory");
    reg(kScbAircr) = 0x05FA'0004u;  // AIRCR: VECTKEY | SYSRESETREQ
    asm volatile("dsb 0xF" ::: "memory");
    for (;;) {
    }
}

void RebootRequest::request(std::optional<Marker> marker, std::chrono::milliseconds now)
{
    if (marker) {
        arm(*marker);
    }
    deadline_ = now + kRebootDelay;
}

void RebootRequest::service(std::chrono::milliseconds now) const
{
    if (deadline_ && now >= *deadline_) {
        system_reset();
    }
}

void CdcTouch::on_line_coding(std::span<const std::byte, 7> coding) noexcept
{
    // dwDTERate — перші чотири байти структури line coding, Little-Endian.
    rate_ = static_cast<std::uint32_t>(coding[0])
          | (static_cast<std::uint32_t>(coding[1]) << 8)
          | (static_cast<std::uint32_t>(coding[2]) << 16)
          | (static_cast<std::uint32_t>(coding[3]) << 24);
}

void CdcTouch::on_control_line_state(std::uint16_t value, std::chrono::milliseconds now)
{
    const bool dtr = (value & 0x1u) != 0;
    const bool falling_edge = dtr_ && !dtr;
    dtr_ = dtr;

    // Ловимо саме фронт 1->0 на швидкості 1200: драйвер хоста смикає DTR
    // і при відкритті порту, а це ще не команда прошивати.
    if (rate_ == 1200 && falling_edge) {
        reboot_.request(Marker::UsbTouch, now);
    }
}

void handle_detach(RebootRequest& reboot, std::chrono::milliseconds detach_timeout,
                   std::chrono::milliseconds now)
{
    // bitWillDetach = 1: шину скидаємо самі, але паузу wDetachTimeOut поважаємо.
    arm(Marker::ForceBootloader);
    reboot.request(std::nullopt, now + detach_timeout);
}

MavResult handle_command_long(std::span<const std::byte> payload,
                              std::uint8_t our_system, std::uint8_t our_component,
                              RebootRequest& reboot, std::chrono::milliseconds now)
{
    if (payload.size() < kCommandLongLength) {
        return MavResult::Failed;
    }

    // Розкладка COMMAND_LONG: сім float-параметрів, далі command,
    // target_system, target_component, confirmation.
    const auto command = static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(payload[28])
        | (static_cast<std::uint16_t>(payload[29]) << 8));
    if (command != kCmdPreflightRebootShutdown) {
        return MavResult::Unsupported;
    }

    const auto target_system = static_cast<std::uint8_t>(payload[30]);
    const auto target_component = static_cast<std::uint8_t>(payload[31]);
    if (target_system != 0 && target_system != our_system) {
        return MavResult::Failed;
    }
    if (target_component != 0 && target_component != our_component) {
        return MavResult::Failed;
    }

    float param1 = 0.0F;
    // memcpy — жодних припущень про вирівнювання буфера прийому.
    std::memcpy(&param1, payload.data(), sizeof param1);
    if (param1 < -0.5F || param1 > 10.0F) {
        return MavResult::Denied;
    }

    switch (static_cast<int>(param1 + 0.5F)) {  // по дроту йде float
    case 0:
        return MavResult::Accepted;  // нічого не робимо
    case 1:
        reboot.request(std::nullopt, now);  // звичайний старт польотного коду
        return MavResult::Accepted;
    case 3:
        reboot.request(Marker::ForceBootloader, now);
        return MavResult::Accepted;
    default:
        // Вимикання живлення (2) та інші режими польотний контролер не вміє.
        return MavResult::Unsupported;
    }
}

}  // namespace fc::boot
