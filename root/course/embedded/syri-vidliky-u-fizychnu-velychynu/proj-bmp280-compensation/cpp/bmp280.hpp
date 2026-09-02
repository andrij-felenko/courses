#pragma once

/*
 * Пристрій BMP280 поверх довільної шини. Шина задається концептом:
 * драйвер не знає, I2C під ним чи SPI, і не платить за віртуальний виклик.
 */

#include "compensation.hpp"

#include <array>
#include <chrono>
#include <concepts>
#include <cstdint>
#include <expected>
#include <span>

namespace bmp280 {

namespace reg {
inline constexpr std::uint8_t calib_start = 0x88; // 24 байти, 0x88..0x9F
inline constexpr std::uint8_t id          = 0xD0;
inline constexpr std::uint8_t reset       = 0xE0;
inline constexpr std::uint8_t status      = 0xF3;
inline constexpr std::uint8_t ctrl_meas   = 0xF4;
inline constexpr std::uint8_t config      = 0xF5;
inline constexpr std::uint8_t data_start  = 0xF7; // 6 байтів, 0xF7..0xFC
} // namespace reg

inline constexpr std::uint8_t chip_id   = 0x58; // саме BMP280, не BME280
inline constexpr std::uint8_t reset_key = 0xB6;

inline constexpr std::uint8_t status_measuring = 1u << 3;
inline constexpr std::uint8_t status_im_update = 1u << 0;

// Кратність апаратного усереднення сигма-дельта АЦП.
enum class Oversampling : std::uint8_t { skip = 0, x1, x2, x4, x8, x16 };

// Коефіцієнт придушення вбудованого IIR-фільтра першого порядку.
enum class Filter : std::uint8_t { off = 0, x2, x4, x8, x16 };

enum class Mode : std::uint8_t { sleep = 0, forced = 1, normal = 3 };

// Пауза між автоциклами в режимі normal.
enum class Standby : std::uint8_t {
    ms0_5 = 0, ms62_5, ms125, ms250, ms500, ms1000, ms2000, ms4000
};

struct Config {
    Oversampling temperature = Oversampling::x2;
    Oversampling pressure    = Oversampling::x16;
    Filter       filter      = Filter::x4;
    Standby      standby     = Standby::ms125;
    Mode         mode        = Mode::normal;
};

// Максимальний час одного перетворення для заданої передискретизації.
[[nodiscard]] constexpr std::chrono::milliseconds
measurement_time(const Config& cfg) noexcept
{
    constexpr std::array<int, 6> mult{0, 1, 2, 4, 8, 16};

    int tenths = 13; // 1.25 мс на запуск циклу, округлено вгору
    tenths += 23 * mult[static_cast<std::size_t>(cfg.temperature)];
    if (cfg.pressure != Oversampling::skip) {
        tenths += 23 * mult[static_cast<std::size_t>(cfg.pressure)] + 6; // +0.575 мс
    }
    return std::chrono::milliseconds{(tenths + 9) / 10};
}

/*
 * Шина мусить уміти пакетне читання: одна транзакція на весь буфер —
 * єдина гарантія, що байти походять з одного вимірювання.
 */
template <class B>
concept RegisterBus = requires(B& bus, std::uint8_t r, std::span<std::uint8_t> dst,
                               std::uint8_t value, std::chrono::milliseconds pause) {
    { bus.read(r, dst) }    -> std::convertible_to<bool>;
    { bus.write(r, value) } -> std::convertible_to<bool>;
    bus.delay(pause);
};

template <RegisterBus Bus>
class Device {
public:
    // Єдиний шлях створення: без справного калібрування пристрою не існує.
    [[nodiscard]] static std::expected<Device, Error>
    open(Bus& bus, const Config& cfg = {}) noexcept
    {
        std::uint8_t id_value{};
        if (!bus.read(reg::id, std::span{&id_value, 1})) {
            return std::unexpected{Error::bus};
        }
        if (id_value != chip_id) {
            return std::unexpected{Error::wrong_chip};
        }

        if (!bus.write(reg::reset, reset_key)) {
            return std::unexpected{Error::bus};
        }
        bus.delay(std::chrono::milliseconds{3}); // старт після скидання

        // Поки im_update = 1, тіньові регістри ще заповнюються з OTP —
        // прочитане в цей момент калібрування буде наполовину старим.
        if (auto rc = wait_status(bus, status_im_update, 20); !rc) {
            return std::unexpected{rc.error()};
        }

        std::array<std::uint8_t, calibration_bytes> raw{};
        if (!bus.read(reg::calib_start, raw)) {
            return std::unexpected{Error::bus};
        }
        auto calib = parse_calibration(std::span<const std::uint8_t, calibration_bytes>{raw});
        if (!calib) {
            return std::unexpected{calib.error()};
        }

        // config пишемо, поки датчик у сні: у normal запис ігнорується.
        const auto conf = static_cast<std::uint8_t>(
            (static_cast<unsigned>(cfg.standby) << 5) |
            (static_cast<unsigned>(cfg.filter) << 2));
        if (!bus.write(reg::config, conf)) {
            return std::unexpected{Error::bus};
        }

        const auto ctrl = static_cast<std::uint8_t>(
            (static_cast<unsigned>(cfg.temperature) << 5) |
            (static_cast<unsigned>(cfg.pressure) << 2));
        if (!bus.write(reg::ctrl_meas,
                       static_cast<std::uint8_t>(ctrl | static_cast<unsigned>(cfg.mode)))) {
            return std::unexpected{Error::bus};
        }

        return Device{bus, cfg, ctrl, *calib};
    }

    [[nodiscard]] std::expected<Measurement, Error> read() noexcept
    {
        if (cfg_.mode == Mode::forced) {
            // Forced: кожен цикл запускається окремо, далі чип сам засинає.
            const auto ctrl = static_cast<std::uint8_t>(
                ctrl_base_ | static_cast<unsigned>(Mode::forced));
            if (!bus_->write(reg::ctrl_meas, ctrl)) {
                return std::unexpected{Error::bus};
            }
        }
        bus_->delay(measurement_time(cfg_));

        // Кадр беремо лише коли АЦП стоїть і тіньові регістри не
        // переписуються: інакше зловимо суміш двох сусідніх вимірювань.
        if (auto rc = wait_status(*bus_, status_measuring | status_im_update, 32); !rc) {
            return std::unexpected{rc.error()};
        }

        std::array<std::uint8_t, frame_bytes> frame{};
        if (!bus_->read(reg::data_start, frame)) {
            return std::unexpected{Error::bus};
        }

        return unpack_frame(std::span<const std::uint8_t, frame_bytes>{frame})
            .and_then([this](RawSample sample) { return comp_.apply(sample); });
    }

    [[nodiscard]] const Calibration& calibration() const noexcept {
        return comp_.calibration();
    }

private:
    Device(Bus& bus, const Config& cfg, std::uint8_t ctrl_base,
           const Calibration& calib) noexcept
        : bus_{&bus}, cfg_{cfg}, ctrl_base_{ctrl_base}, comp_{calib} {}

    // Чекає, поки задані біти статусу впадуть у нуль.
    static std::expected<void, Error>
    wait_status(Bus& bus, std::uint8_t mask, int attempts) noexcept
    {
        for (int i = 0; i < attempts; ++i) {
            std::uint8_t value{};
            if (!bus.read(reg::status, std::span{&value, 1})) {
                return std::unexpected{Error::bus};
            }
            if ((value & mask) == 0) {
                return {};
            }
            bus.delay(std::chrono::milliseconds{2});
        }
        return std::unexpected{Error::timeout};
    }

    Bus*         bus_{};
    Config       cfg_{};
    std::uint8_t ctrl_base_{};
    Compensator  comp_;
};

} // namespace bmp280
