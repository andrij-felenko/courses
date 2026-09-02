#include "sensor.hpp"

namespace bringup {
namespace {
using namespace std::chrono_literals;

constexpr auto kResetQuiet = 5ms;    // мінімальна тиша після команди скидання
constexpr auto kResetTimeout = 50ms; // стеля очікування готовності
constexpr auto kPollStep = 2ms;      // інтервал між опитуваннями
}  // namespace

Sensor::Sensor(platform::I2cBus& bus, platform::PowerRail& rail, std::uint8_t addr,
               std::string_view name, bool critical) noexcept
    : bus_{bus}, rail_{rail}, addr_{addr}, name_{name}, critical_{critical} {}

// Реакція на NACK — головне місце всієї процедури: поки чип усередині скидання,
// він відключає інтерфейсний блок і не підтверджує адресу. Це нормальна
// відповідь. Фатальні тут лише вичерпаний таймаут і притиснута SDA.
std::expected<void, Fault> Sensor::software_reset() {
    if (!bus_.write(addr_, reg::ResetCtrl, bits::SwReset)) {
        return std::unexpected(Fault{InitError::Bus, reg::ResetCtrl});
    }
    platform::sleep(kResetQuiet);

    const auto deadline = platform::Clock::now() + kResetTimeout;
    while (true) {
        const auto ctrl = bus_.read(addr_, reg::ResetCtrl);
        const auto status = bus_.read(addr_, reg::Status);

        if (ctrl && status) {
            const bool reset_done = (*ctrl & bits::SwReset) == 0;  // біт самоочисний
            const bool device_ready = (*status & bits::StatusReady) != 0;
            if (reset_done && device_ready) {
                return {};
            }
        } else {
            const auto error = !ctrl ? ctrl.error() : status.error();
            if (error == platform::BusError::Stuck) {
                return std::unexpected(Fault{InitError::Bus, reg::Status});
            }
            // Nack — чип ще перезавантажується, чекаємо далі
        }

        if (platform::Clock::now() >= deadline) {
            return std::unexpected(Fault{InitError::Timeout, reg::Status});
        }
        platform::sleep(kPollStep);
    }
}

// Одне читання ловить три різні біди: обірвану лінію (0x00 чи 0xFF), чужий
// пристрій на тій самій адресі й несумісну ревізію кремнію.
std::expected<void, Fault> Sensor::check_id() {
    const auto id = bus_.read(addr_, reg::WhoAmI);
    if (!id) {
        return std::unexpected(Fault{InitError::Bus, reg::WhoAmI});
    }
    if (*id != WhoAmIValue) {
        return std::unexpected(Fault{InitError::WrongId, reg::WhoAmI});
    }
    return {};
}

std::expected<bool, Fault> Sensor::data_ready() {
    const auto status = bus_.read(addr_, reg::Status);
    if (!status) {
        return std::unexpected(Fault{InitError::Bus, reg::Status});
    }
    return (*status & bits::StatusDrdy) != 0;
}

}  // namespace bringup
