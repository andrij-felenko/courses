// bsp/accelerometer.cpp — усе, що знає про мікросхему ADXL345.
// Номери регістрів і ціна молодшого розряду не виходять за межі цього
// файла: заголовок не має жодної згадки про них, тож заміна давача на
// LIS3DH не змусить перезбирати ані застосунок, ані тести бізнес-логіки.
#include "bsp/accelerometer.hpp"

#include "hal/clock.hpp"

#include <array>

namespace bsp {
namespace {

// Карта регістрів (datasheet ADXL345, Register Map).
constexpr std::uint8_t kRegDevId      = 0x00;
constexpr std::uint8_t kRegBwRate     = 0x2C;
constexpr std::uint8_t kRegPowerCtl   = 0x2D;
constexpr std::uint8_t kRegDataFormat = 0x31;
constexpr std::uint8_t kRegDataX0     = 0x32;
constexpr std::uint8_t kRegFifoCtl    = 0x38;

constexpr std::uint8_t kDevIdValue    = 0xE5;
constexpr std::uint8_t kRate100Hz     = 0x0A;
constexpr std::uint8_t kPowerMeasure  = 0x08;
constexpr std::uint8_t kPowerStandby  = 0x00;
constexpr std::uint8_t kFormatFullRes = 0x08;
constexpr std::uint8_t kFifoBypass    = 0x00;

// У режимі повної роздільності ціна розряду однакова для всіх діапазонів.
constexpr float kLsbPerG = 256.0F;

[[nodiscard]] std::int16_t le16(std::uint8_t low, std::uint8_t high) noexcept
{
    return static_cast<std::int16_t>(static_cast<std::uint16_t>(low) |
                                     static_cast<std::uint16_t>(high) << 8);
}

} // namespace

std::optional<Adxl345> Adxl345::create(hal::I2cDevice device, AccelRange range)
{
    const auto id = device.read_reg(kRegDevId);
    if (!id || *id != kDevIdValue) {
        // На адресі 0x53 залюбки сидить чужий давач. Дізнатися про це тут
        // дешевше, ніж розбирати польові дані, які тихо брешуть.
        return std::nullopt;
    }

    const auto format = static_cast<std::uint8_t>(
        kFormatFullRes | (static_cast<std::uint8_t>(range) & 0x03));

    const bool configured =
        device.write_reg(kRegPowerCtl, kPowerStandby) &&
        device.write_reg(kRegDataFormat, format) &&
        device.write_reg(kRegBwRate, kRate100Hz) &&
        device.write_reg(kRegFifoCtl, kFifoBypass) &&
        device.write_reg(kRegPowerCtl, kPowerMeasure);

    if (!configured) {
        return std::nullopt;
    }

    hal::delay(hal::Millis{20});  // перший вимір з'явиться не раніше
    return Adxl345{device, range};
}

std::expected<AccelSample, hal::I2cError> Adxl345::read()
{
    std::array<std::uint8_t, 6> raw{};
    if (auto res = device_.read_regs(kRegDataX0, raw); !res) {
        return std::unexpected{res.error()};
    }

    // ADXL345 віддає осі молодшим байтом уперед, у доповняльному коді.
    return AccelSample{
        .x_g = static_cast<float>(le16(raw[0], raw[1])) / kLsbPerG,
        .y_g = static_cast<float>(le16(raw[2], raw[3])) / kLsbPerG,
        .z_g = static_cast<float>(le16(raw[4], raw[5])) / kLsbPerG,
    };
}

void Adxl345::standby()
{
    // Результат навмисно ігноруємо: якщо шина вже мертва, приспати давач
    // однаково не вийде, а падати на цьому місці нема сенсу.
    static_cast<void>(device_.write_reg(kRegPowerCtl, kPowerStandby));
}

} // namespace bsp
