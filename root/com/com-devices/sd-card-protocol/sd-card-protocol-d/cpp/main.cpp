#include <cstdint>
#include <span>
#include <expected>

namespace sd {

enum class DriverStatus : uint8_t {
    Success,
    ResponseTimeout,
    CardStatusError,
    BusyTimeout
};

class SdProtocolEngine {
public:
    // Безпечний запис 512-байтного сектора в стилі C++20
    static std::expected<void, DriverStatus> write_sector(
        uint32_t sector_index, 
        std::span<const uint8_t, 512> sector_data) noexcept 
    {
        uint32_t r1_response = 0;

        send_raw_command(24, sector_index);
        if (!receive_r1_response(r1_response, 100)) {
            return std::unexpected(DriverStatus::ResponseTimeout);
        }

        // Перевірка бітів помилок у Card Status
        if ((r1_response & 0xFFD98008) != 0) {
            return std::unexpected(DriverStatus::CardStatusError);
        }

        transmit_dat_payload(sector_data);

        // Очікування зняття Busy на лінії DAT0
        if (!wait_dat0_ready(500)) {
            return std::unexpected(DriverStatus::BusyTimeout);
        }

        return {};
    }

private:
    static void send_raw_command(uint8_t cmd, uint32_t arg) noexcept;
    static bool receive_r1_response(uint32_t& out_r1, uint32_t timeout_ms) noexcept;
    static void transmit_dat_payload(std::span<const uint8_t, 512> data) noexcept;
    static bool wait_dat0_ready(uint32_t timeout_ms) noexcept;
};

} // namespace sd
