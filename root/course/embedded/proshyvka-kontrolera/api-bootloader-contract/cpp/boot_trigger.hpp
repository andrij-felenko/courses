#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace fc::boot {

using namespace std::chrono_literals;

// Магічні маркери резервного домену RTC. ASCII у значеннях — щоб їх було
// видно в дампі при відлагодженні.
enum class Marker : std::uint32_t {
    ForceBootloader = 0x424C'6F6F,  // "BLoo"
    BetaflightDfu   = 0x4246'5400,  // "BFT\0"
    UsbTouch        = 0x544F'5543,  // "TOUC"
    Rollback        = 0x524F'4C4C,  // "ROLL"
};

// Пауза між рішенням перезапуститись і скиданням: хост має встигнути
// прийняти COMMAND_ACK і закрити свій кінець порту.
inline constexpr std::chrono::milliseconds kRebootDelay = 100ms;

void arm(Marker marker);
[[nodiscard]] std::optional<Marker> take();      // читає й ОДРАЗУ чистить BKP0R
void arm_rollback();
[[nodiscard]] bool take_rollback();

[[noreturn]] void system_reset() noexcept;

// Відкладене скидання: маркер ставимо зараз, скидаємось із головного циклу.
class RebootRequest {
public:
    void request(std::optional<Marker> marker, std::chrono::milliseconds now);
    void service(std::chrono::milliseconds now) const;

private:
    std::optional<std::chrono::milliseconds> deadline_;
};

// Метод 1: 1200 bps touch на віртуальному COM-порту.
class CdcTouch {
public:
    explicit CdcTouch(RebootRequest& reboot) noexcept : reboot_{reboot} {}

    void on_line_coding(std::span<const std::byte, 7> coding) noexcept;
    void on_control_line_state(std::uint16_t value, std::chrono::milliseconds now);

private:
    RebootRequest& reboot_;
    std::uint32_t rate_ = 0;
    bool dtr_ = false;
};

// DFU_DETACH з боку польотної прошивки (стан appIDLE).
void handle_detach(RebootRequest& reboot, std::chrono::milliseconds detach_timeout,
                   std::chrono::milliseconds now);

// Метод 3: MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN усередині COMMAND_LONG.
enum class MavResult : std::uint8_t {
    Accepted            = 0,
    TemporarilyRejected = 1,
    Denied              = 2,
    Unsupported         = 3,
    Failed              = 4,
};

inline constexpr std::uint16_t kCmdPreflightRebootShutdown = 246;
inline constexpr std::size_t kCommandLongLength = 33;

MavResult handle_command_long(std::span<const std::byte> payload,
                              std::uint8_t our_system, std::uint8_t our_component,
                              RebootRequest& reboot, std::chrono::milliseconds now);

}  // namespace fc::boot
