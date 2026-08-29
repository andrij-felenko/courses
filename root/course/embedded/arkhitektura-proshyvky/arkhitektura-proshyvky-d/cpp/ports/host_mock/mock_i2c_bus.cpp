// ports/host_mock/mock_i2c_bus.cpp — імітація шини та мікросхем.
// Драйвер не бачить різниці: він говорить у той самий hal::II2cBus, що й
// на живій платі. Калібрувальні коефіцієнти взято з реального примірника
// BME280, а сирі коди підібрано так, щоб формула дала близько 25 °C.
#include "app/config.hpp"
#include "ports/host_mock/host_mocks.hpp"

namespace port {
namespace {

constexpr std::uint8_t kBmeRegReset    = 0xE0;
constexpr std::uint8_t kBmeRegCtrlMeas = 0xF4;
constexpr std::uint8_t kBmeResetWord   = 0xB6;

} // namespace

void MockDevice::set_reg16(std::uint8_t reg, std::uint16_t value) noexcept
{
    regs_[reg]     = static_cast<std::uint8_t>(value & 0xFF);
    regs_[reg + 1] = static_cast<std::uint8_t>(value >> 8);
}

void MockDevice::inject_error(hal::I2cError error, unsigned count) noexcept
{
    inject_error_ = error;
    inject_left_  = count;
}

bool MockDevice::take_injected(hal::I2cError& out) noexcept
{
    if (inject_left_ == 0) {
        return false;
    }
    --inject_left_;
    out = inject_error_;
    return true;
}

std::uint8_t MockDevice::read_next() noexcept
{
    // Внутрішній лічильник адреси загортається на 256 — так само, як у
    // справжньої мікросхеми з однобайтовою адресою регістра.
    const std::uint8_t value = regs_[pointer_];
    pointer_ = static_cast<std::uint8_t>(pointer_ + 1);
    return value;
}

void MockDevice::write_reg(std::uint8_t reg, std::uint8_t value)
{
    regs_[reg] = value;
}

// --- BME280 ---

MockBme280::MockBme280() : MockDevice{config::kBme280Address}
{
    set_reg(0xD0, 0x60);   // ідентифікатор саме BME280
    set_reg(0xF3, 0x00);   // перетворення не триває

    set_reg16(0x88, 28000);                                       // dig_T1
    set_reg16(0x8A, static_cast<std::uint16_t>(26500));           // dig_T2
    set_reg16(0x8C, static_cast<std::uint16_t>(50));              // dig_T3

    set_reg16(0x8E, 36477);                                       // dig_P1
    set_reg16(0x90, static_cast<std::uint16_t>(-10685));          // dig_P2
    set_reg16(0x92, 3024);                                        // dig_P3
    set_reg16(0x94, 2855);                                        // dig_P4
    set_reg16(0x96, 140);                                         // dig_P5
    set_reg16(0x98, static_cast<std::uint16_t>(-7));              // dig_P6
    set_reg16(0x9A, 15500);                                       // dig_P7
    set_reg16(0x9C, static_cast<std::uint16_t>(-14600));          // dig_P8
    set_reg16(0x9E, 6000);                                        // dig_P9

    set_reg(0xA1, 75);                                            // dig_H1
    set_reg16(0xE1, 350);                                         // dig_H2
    set_reg(0xE3, 0);                                             // dig_H3
    // dig_H4 = 302, dig_H5 = 50 — дванадцятибітні зі спільним байтом 0xE5.
    set_reg(0xE4, static_cast<std::uint8_t>(302 >> 4));
    set_reg(0xE5, static_cast<std::uint8_t>(((50 & 0x0F) << 4) | (302 & 0x0F)));
    set_reg(0xE6, static_cast<std::uint8_t>(50 >> 4));
    set_reg(0xE7, 30);                                            // dig_H6

    set_raw(527144, 415148, 32000);
}

void MockBme280::set_raw(std::uint32_t adc_t, std::uint32_t adc_p, std::uint16_t adc_h)
{
    // Регістри 0xF7…0xFE: тиск, температура, вологість — старшим байтом
    // уперед, тиск і температура по двадцять розрядів.
    set_reg(0xF7, static_cast<std::uint8_t>((adc_p >> 12) & 0xFF));
    set_reg(0xF8, static_cast<std::uint8_t>((adc_p >> 4) & 0xFF));
    set_reg(0xF9, static_cast<std::uint8_t>((adc_p << 4) & 0xF0));
    set_reg(0xFA, static_cast<std::uint8_t>((adc_t >> 12) & 0xFF));
    set_reg(0xFB, static_cast<std::uint8_t>((adc_t >> 4) & 0xFF));
    set_reg(0xFC, static_cast<std::uint8_t>((adc_t << 4) & 0xF0));
    set_reg(0xFD, static_cast<std::uint8_t>(adc_h >> 8));
    set_reg(0xFE, static_cast<std::uint8_t>(adc_h & 0xFF));
}

void MockBme280::write_reg(std::uint8_t reg, std::uint8_t value)
{
    MockDevice::write_reg(reg, value);

    if (reg == kBmeRegReset && value == kBmeResetWord) {
        // Скидання обнуляє конфігураційні регістри, а калібрування й сирі
        // дані лишає — так само робить справжня мікросхема.
        MockDevice::write_reg(0xF2, 0);
        MockDevice::write_reg(0xF4, 0);
        MockDevice::write_reg(0xF5, 0);
    }
    if (reg == kBmeRegCtrlMeas && (value & 0x03) == 0x01) {
        // Режим forced: імітація відпрацьовує вимір миттєво, тож прапорець
        // «міряю» навіть не встигає піднятися.
        MockDevice::write_reg(0xF3, 0);
        MockDevice::write_reg(0xF4, static_cast<std::uint8_t>(value & 0xFC));
    }
}

// --- ADXL345 ---

MockAdxl345::MockAdxl345() : MockDevice{config::kAdxl345Address}
{
    set_reg(0x00, 0xE5);      // DEVID
    set_axes(0, 0, 256);      // спокій: 1 g по осі Z
}

void MockAdxl345::set_axes(std::int16_t x, std::int16_t y, std::int16_t z)
{
    set_reg16(0x32, static_cast<std::uint16_t>(x));
    set_reg16(0x34, static_cast<std::uint16_t>(y));
    set_reg16(0x36, static_cast<std::uint16_t>(z));
}

// --- Шина ---

std::expected<MockDevice*, hal::I2cError> MockI2cBus::select(std::uint8_t address)
{
    MockDevice* device = nullptr;
    if (address == env_.address()) {
        device = &env_;
    } else if (address == accel_.address()) {
        device = &accel_;
    }

    if (device == nullptr || !device->present()) {
        // Порожня колодка на платі відповідає так само: мовчанням.
        return std::unexpected{hal::I2cError::Nack};
    }

    hal::I2cError injected{};
    if (device->take_injected(injected)) {
        return std::unexpected{injected};
    }

    ++transactions_;
    return device;
}

std::expected<void, hal::I2cError>
MockI2cBus::write(std::uint8_t address, std::span<const std::uint8_t> data)
{
    const auto device = select(address);
    if (!device) {
        return std::unexpected{device.error()};
    }
    if (data.empty()) {
        return {};   // опитування присутності
    }

    (*device)->select(data[0]);
    for (std::size_t i = 1; i < data.size(); ++i) {
        (*device)->write_reg(static_cast<std::uint8_t>(data[0] + i - 1), data[i]);
    }
    return {};
}

std::expected<void, hal::I2cError>
MockI2cBus::read(std::uint8_t address, std::span<std::uint8_t> data)
{
    const auto device = select(address);
    if (!device) {
        return std::unexpected{device.error()};
    }
    if (data.empty()) {
        return std::unexpected{hal::I2cError::BadArgs};
    }

    for (std::uint8_t& byte : data) {
        byte = (*device)->read_next();
    }
    return {};
}

} // namespace port
