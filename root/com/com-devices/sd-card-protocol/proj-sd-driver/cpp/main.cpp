#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>

namespace sd {

enum class Error : uint8_t {
    Timeout,
    CrcMismatch,
    UnsupportedCardVersion,
    InvalidResponse,
    WriteProgrammingFailed,
    HardwareBusy
};

struct CardGeometry {
    uint16_t rca{0};
    bool is_high_capacity{false}; // SDHC / SDXC
    bool is_4bit_bus{false};
};

class SdHostDriver {
public:
    SdHostDriver() = default;

    // Ініціалізація карти з поверненням геометрії або коду помилки
    std::expected<CardGeometry, Error> initialize() noexcept {
        CardGeometry geo;

        // Початкова безпечна частота 400 кГц
        set_hardware_frequency(400'000);
        delay_ms(10);

        // CMD0: Скидання у стан Idle
        send_cmd(0, 0x00000000);
        delay_ms(2);

        // CMD8: Перевірка напруги та версії SD v2.0+
        send_cmd(8, 0x000001AA);
        const auto r7 = wait_r3_r7(100);
        if (!r7.has_value()) {
            return std::unexpected(Error::UnsupportedCardVersion);
        }
        if ((*r7 & 0xFF) != 0xAA) {
            return std::unexpected(Error::InvalidResponse);
        }

        // Опитування ACMD41 з бітом HCS (Host Capacity Support)
        uint32_t timeout_ms = 1000;
        bool ready = false;
        while (timeout_ms > 0) {
            send_cmd(55, 0x00000000); // Префікс APP_CMD
            if (!wait_r1(50).has_value()) {
                return std::unexpected(Error::Timeout);
            }

            send_cmd(41, 0x40FF8000); // HCS=1, 2.7-3.6В
            const auto ocr = wait_r3_r7(50);
            if (!ocr.has_value()) {
                return std::unexpected(Error::Timeout);
            }

            if (*ocr & (1UL << 31)) { // Busy біт готовий
                ready = true;
                geo.is_high_capacity = (*ocr & (1UL << 30)) != 0; // CCS біт
                break;
            }

            delay_ms(10);
            timeout_ms = (timeout_ms > 10) ? (timeout_ms - 10) : 0;
        }

        if (!ready) {
            return std::unexpected(Error::Timeout);
        }

        // CMD2: Зчитування 128-бітного CID
        send_cmd(2, 0x00000000);
        std::array<uint8_t, 16> cid_buffer{};
        if (!wait_r2(cid_buffer, 100)) {
            return std::unexpected(Error::Timeout);
        }

        // CMD3: Публікація RCA адреси
        send_cmd(3, 0x00000000);
        const auto rca_val = wait_r6(100);
        if (!rca_val.has_value()) {
            return std::unexpected(Error::Timeout);
        }
        geo.rca = *rca_val;

        // CMD7: Вибір карти в Transfer State
        send_cmd(7, static_cast<uint32_t>(geo.rca) << 16);
        if (!wait_r1(100).has_value()) {
            return std::unexpected(Error::Timeout);
        }

        // Перехід на робочу частоту 25 МГц
        set_hardware_frequency(25'000'000);

        // ACMD6: Перемикання в 4-бітний режим шини
        send_cmd(55, static_cast<uint32_t>(geo.rca) << 16);
        if (wait_r1(50).has_value()) {
            send_cmd(6, 0x00000002);
            if (wait_r1(50).has_value()) {
                set_hardware_bus_width_4bit(true);
                geo.is_4bit_bus = true;
            }
        }

        active_geometry_ = geo;
        return geo;
    }

    // Читання сектора 512 байт через безпечний буфер std::span
    std::expected<void, Error> read_sector(uint32_t sector_num, std::span<uint8_t, 512> output_buffer) noexcept {
        const uint32_t address = active_geometry_.is_high_capacity ? sector_num : (sector_num * 512);

        send_cmd(17, address);
        const auto r1 = wait_r1(100);
        if (!r1.has_value()) {
            return std::unexpected(Error::Timeout);
        }
        if (*r1 & 0xFFD98008) {
            return std::unexpected(Error::InvalidResponse);
        }

        if (!read_dat_stream(output_buffer)) {
            return std::unexpected(Error::CrcMismatch);
        }

        return {};
    }

    // Запис сектора 512 байт з очікуванням виходу з стану Busy
    std::expected<void, Error> write_sector(uint32_t sector_num, std::span<const uint8_t, 512> input_data) noexcept {
        const uint32_t address = active_geometry_.is_high_capacity ? sector_num : (sector_num * 512);

        send_cmd(24, address);
        const auto r1 = wait_r1(100);
        if (!r1.has_value()) {
            return std::unexpected(Error::Timeout);
        }
        if (*r1 & 0xFFD98008) {
            return std::unexpected(Error::InvalidResponse);
        }

        if (!write_dat_stream(input_data)) {
            return std::unexpected(Error::WriteProgrammingFailed);
        }

        // Очікування завершення запису у Flash-пам'ять
        uint32_t busy_timeout = 500;
        while (is_line_dat0_low() && busy_timeout > 0) {
            delay_ms(1);
            --busy_timeout;
        }

        if (busy_timeout == 0) {
            return std::unexpected(Error::HardwareBusy);
        }

        return {};
    }

private:
    CardGeometry active_geometry_{};

    // Внутрішні методи взаємодії з апаратурою
    static void send_cmd(uint8_t cmd, uint32_t arg) noexcept;
    static std::expected<uint32_t, Error> wait_r1(uint32_t timeout_ms) noexcept;
    static bool wait_r2(std::span<uint8_t, 16> out_cid, uint32_t timeout_ms) noexcept;
    static std::expected<uint32_t, Error> wait_r3_r7(uint32_t timeout_ms) noexcept;
    static std::expected<uint16_t, Error> wait_r6(uint32_t timeout_ms) noexcept;
    static void set_hardware_frequency(uint32_t hz) noexcept;
    static void set_hardware_bus_width_4bit(bool enable) noexcept;
    static bool read_dat_stream(std::span<uint8_t, 512> dest) noexcept;
    static bool write_dat_stream(std::span<const uint8_t, 512> src) noexcept;
    static bool is_line_dat0_low() noexcept;
    static void delay_ms(uint32_t ms) noexcept;
};

} // namespace sd
