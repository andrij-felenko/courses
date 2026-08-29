// bsp/bme280.cpp — реалізація драйвера BME280.
// Формули компенсації взято з довідника Bosch (розділ «Compensation
// formulas»); вони цілочислові, і саме тому їх варто тримати в одному
// місці, а не розсипати по головному циклу, як це робив прототип.
#include "bsp/bme280.hpp"

#include "hal/clock.hpp"

#include <array>

namespace bsp {
namespace {

constexpr std::uint8_t kRegCalib00   = 0x88;  // dig_T1…dig_P9, 26 байтів
constexpr std::uint8_t kRegId        = 0xD0;
constexpr std::uint8_t kRegReset     = 0xE0;
constexpr std::uint8_t kRegCalib26   = 0xE1;  // dig_H2…dig_H6, 7 байтів
constexpr std::uint8_t kRegCtrlHum   = 0xF2;
constexpr std::uint8_t kRegStatus    = 0xF3;
constexpr std::uint8_t kRegCtrlMeas  = 0xF4;
constexpr std::uint8_t kRegConfig    = 0xF5;
constexpr std::uint8_t kRegPressMsb  = 0xF7;  // 8 байтів сирих даних поспіль

constexpr std::uint8_t kChipId          = 0x60;
constexpr std::uint8_t kResetWord       = 0xB6;
constexpr std::uint8_t kStatusMeasuring = 0x08;
constexpr std::uint8_t kOsrsHumX1       = 0x01;
constexpr std::uint8_t kCtrlMeasForced  = 0x25;  // osrs_t=1, osrs_p=1, forced
constexpr std::uint8_t kConfigFilterOff = 0x00;

constexpr hal::Millis kMeasureTimeout{20};
constexpr std::int32_t kAdcDisabled = 0x80000;  // канал вимкнено

[[nodiscard]] std::uint16_t u16(std::span<const std::uint8_t> b, std::size_t i) noexcept
{
    return static_cast<std::uint16_t>(static_cast<std::uint16_t>(b[i]) |
                                      static_cast<std::uint16_t>(b[i + 1]) << 8);
}

[[nodiscard]] std::int16_t s16(std::span<const std::uint8_t> b, std::size_t i) noexcept
{
    return static_cast<std::int16_t>(u16(b, i));
}

} // namespace

std::expected<Bme280::Calibration, hal::I2cError>
Bme280::read_calibration(const hal::I2cDevice& device)
{
    std::array<std::uint8_t, 26> block{};
    if (auto res = device.read_regs(kRegCalib00, block); !res) {
        return std::unexpected{res.error()};
    }

    std::array<std::uint8_t, 7> humidity{};
    if (auto res = device.read_regs(kRegCalib26, humidity); !res) {
        return std::unexpected{res.error()};
    }

    Calibration c{};
    c.t1 = u16(block, 0);
    c.t2 = s16(block, 2);
    c.t3 = s16(block, 4);
    c.p1 = u16(block, 6);
    c.p2 = s16(block, 8);
    c.p3 = s16(block, 10);
    c.p4 = s16(block, 12);
    c.p5 = s16(block, 14);
    c.p6 = s16(block, 16);
    c.p7 = s16(block, 18);
    c.p8 = s16(block, 20);
    c.p9 = s16(block, 22);
    c.h1 = block[25];

    c.h2 = s16(humidity, 0);
    c.h3 = humidity[2];
    // dig_H4 і dig_H5 — дванадцятибітні зі спільним байтом humidity[4].
    c.h4 = static_cast<std::int16_t>(static_cast<std::int16_t>(static_cast<std::int8_t>(humidity[3])) * 16 |
                                     static_cast<std::int16_t>(humidity[4] & 0x0F));
    c.h5 = static_cast<std::int16_t>(static_cast<std::int16_t>(static_cast<std::int8_t>(humidity[5])) * 16 |
                                     static_cast<std::int16_t>(humidity[4] >> 4));
    c.h6 = static_cast<std::int8_t>(humidity[6]);

    // Порожня калібрувальна таблиця дала б ділення на нуль у формулі тиску.
    if (c.t1 == 0 || c.p1 == 0) {
        return std::unexpected{hal::I2cError::BusError};
    }
    return c;
}

std::optional<Bme280> Bme280::create(hal::I2cDevice device)
{
    const auto id = device.read_reg(kRegId);
    if (!id || *id != kChipId) {
        // 0x58 — це BMP280 без вологості, 0x61 — BME680. Видавати їхні
        // покази за наші не можна: формули вологості інші.
        return std::nullopt;
    }

    if (!device.write_reg(kRegReset, kResetWord)) {
        return std::nullopt;
    }
    hal::delay(hal::Millis{5});  // копіювання калібрувальної таблиці з ПЗП

    const auto calib = read_calibration(device);
    if (!calib) {
        return std::nullopt;
    }

    // Регістр ctrl_hum набирає чинності лише після запису ctrl_meas —
    // саме тому порядок цих двох рядків міняти не можна.
    if (!device.write_reg(kRegCtrlHum, kOsrsHumX1) ||
        !device.write_reg(kRegConfig, kConfigFilterOff)) {
        return std::nullopt;
    }

    return Bme280{device, *calib};
}

std::expected<void, hal::I2cError> Bme280::wait_conversion()
{
    // Чекаємо за прапорцем, а не наосліп: інакше драйвер заклякне назавжди,
    // щойно давач відвалиться посеред виміру.
    const auto started = hal::now();
    for (;;) {
        const auto status = device_.read_reg(kRegStatus);
        if (!status) {
            return std::unexpected{status.error()};
        }
        if ((*status & kStatusMeasuring) == 0) {
            return {};
        }
        if (hal::elapsed_since(started) > kMeasureTimeout) {
            return std::unexpected{hal::I2cError::Timeout};
        }
        hal::delay(hal::Millis{1});
    }
}

std::expected<Environment, hal::I2cError> Bme280::measure()
{
    if (auto res = device_.write_reg(kRegCtrlMeas, kCtrlMeasForced); !res) {
        return std::unexpected{res.error()};
    }
    if (auto res = wait_conversion(); !res) {
        return std::unexpected{res.error()};
    }

    std::array<std::uint8_t, 8> raw{};
    if (auto res = device_.read_regs(kRegPressMsb, raw); !res) {
        return std::unexpected{res.error()};
    }

    // Тиск і температура — двадцятибітні, вологість — шістнадцятибітна.
    const auto adc_p = static_cast<std::int32_t>(
        static_cast<std::uint32_t>(raw[0]) << 12 |
        static_cast<std::uint32_t>(raw[1]) << 4 |
        static_cast<std::uint32_t>(raw[2]) >> 4);
    const auto adc_t = static_cast<std::int32_t>(
        static_cast<std::uint32_t>(raw[3]) << 12 |
        static_cast<std::uint32_t>(raw[4]) << 4 |
        static_cast<std::uint32_t>(raw[5]) >> 4);
    const auto adc_h = static_cast<std::int32_t>(
        static_cast<std::uint32_t>(raw[6]) << 8 | static_cast<std::uint32_t>(raw[7]));

    if (adc_t == kAdcDisabled) {
        return std::unexpected{hal::I2cError::BusError};
    }

    const std::int32_t  hundredths = compensate_temperature(adc_t);
    const std::uint32_t pressure   = compensate_pressure(adc_p);
    const std::uint32_t humidity   = compensate_humidity(adc_h);

    return Environment{
        .temperature_c = static_cast<float>(hundredths) / 100.0F,
        .humidity_rh   = static_cast<float>(humidity) / 1024.0F,
        .pressure_hpa  = static_cast<float>(pressure) / 25600.0F,  // Па/256 → гПа
    };
}

std::int32_t Bme280::compensate_temperature(std::int32_t adc_t)
{
    const std::int32_t var1 =
        (((adc_t >> 3) - (static_cast<std::int32_t>(calib_.t1) << 1)) *
         static_cast<std::int32_t>(calib_.t2)) >> 11;

    const std::int32_t d = (adc_t >> 4) - static_cast<std::int32_t>(calib_.t1);
    const std::int32_t var2 = (((d * d) >> 12) * static_cast<std::int32_t>(calib_.t3)) >> 14;

    t_fine_ = var1 + var2;
    return (t_fine_ * 5 + 128) >> 8;
}

std::uint32_t Bme280::compensate_pressure(std::int32_t adc_p) const
{
    std::int64_t var1 = static_cast<std::int64_t>(t_fine_) - 128000;
    std::int64_t var2 = var1 * var1 * static_cast<std::int64_t>(calib_.p6);
    var2 += (var1 * static_cast<std::int64_t>(calib_.p5)) << 17;
    var2 += static_cast<std::int64_t>(calib_.p4) << 35;
    var1 = ((var1 * var1 * static_cast<std::int64_t>(calib_.p3)) >> 8) +
           ((var1 * static_cast<std::int64_t>(calib_.p2)) << 12);
    var1 = (((static_cast<std::int64_t>(1) << 47) + var1) *
            static_cast<std::int64_t>(calib_.p1)) >> 33;

    if (var1 == 0) {
        return 0;  // окремо обумовлений у довіднику випадок
    }

    std::int64_t p = 1048576 - adc_p;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (static_cast<std::int64_t>(calib_.p9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (static_cast<std::int64_t>(calib_.p8) * p) >> 19;
    p = ((p + var1 + var2) >> 8) + (static_cast<std::int64_t>(calib_.p7) << 4);
    return static_cast<std::uint32_t>(p);
}

std::uint32_t Bme280::compensate_humidity(std::int32_t adc_h) const
{
    std::int32_t v = t_fine_ - 76800;

    v = (((((adc_h << 14) - (static_cast<std::int32_t>(calib_.h4) << 20) -
            (static_cast<std::int32_t>(calib_.h5) * v)) + 16384) >> 15) *
         (((((((v * static_cast<std::int32_t>(calib_.h6)) >> 10) *
              (((v * static_cast<std::int32_t>(calib_.h3)) >> 11) + 32768)) >> 10) +
            2097152) * static_cast<std::int32_t>(calib_.h2) + 8192) >> 14));

    v -= (((((v >> 15) * (v >> 15)) >> 7) * static_cast<std::int32_t>(calib_.h1)) >> 4);

    v = (v < 0) ? 0 : v;
    v = (v > 419430400) ? 419430400 : v;  // стеля 100 %RH
    return static_cast<std::uint32_t>(v >> 12);
}

} // namespace bsp
