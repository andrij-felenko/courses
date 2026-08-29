#include "mpu6050.hpp"

#include <array>
#include <util/delay.h>

namespace gimbal {
namespace {

// Карта регістрів MPU-6050
constexpr std::uint8_t kRegSmplrtDiv   = 0x19;
constexpr std::uint8_t kRegConfig      = 0x1A;
constexpr std::uint8_t kRegGyroConfig  = 0x1B;
constexpr std::uint8_t kRegAccelConfig = 0x1C;
constexpr std::uint8_t kRegAccelXoutH  = 0x3B;
constexpr std::uint8_t kRegPwrMgmt1    = 0x6B;
constexpr std::uint8_t kRegWhoAmI      = 0x75;

constexpr std::uint8_t kWhoAmIValue = 0x68;

// ±500 °/с → 65.5 LSB на °/с; ±2 g → 16384 LSB на g.
constexpr float kGyroLsbPerDps = 65.5f;
constexpr float kAccelLsbPerG  = 16384.0f;

// Давач віддає старший байт першим.
[[nodiscard]] constexpr std::int16_t be16(std::uint8_t hi, std::uint8_t lo) noexcept {
    return static_cast<std::int16_t>((static_cast<std::uint16_t>(hi) << 8) | lo);
}

}  // namespace

Result<void, TwiError> Mpu6050::begin() noexcept {
    std::array<std::uint8_t, 1> who{};

    if (auto r = bus_.read_registers(kAddress, kRegWhoAmI, who); !r) {
        return r;
    }
    if (who[0] != kWhoAmIValue) {
        // Відповів хтось інший: або переплутана адреса, або на шині
        // висить чужа мікросхема. Йти далі немає сенсу.
        return Result<void, TwiError>::fail(TwiError::BusState);
    }

    // Вихід зі сну, такт від осцилятора гіроскопа X — він стабільніший
    // за внутрішній RC-генератор давача.
    if (auto r = bus_.write_register(kAddress, kRegPwrMgmt1, 0x01); !r) return r;
    _delay_ms(50);

    // DLPF 44 Гц: половина смуги нашого такту 200 Гц. Ширша смуга
    // притягла б у контур вібрацію мотора.
    if (auto r = bus_.write_register(kAddress, kRegConfig, 0x03); !r) return r;

    // З увімкненим DLPF внутрішня частота 1 кГц; дільник 4 дає 200 Гц —
    // рівно наш такт, тож кожне читання приносить свіжу вибірку.
    if (auto r = bus_.write_register(kAddress, kRegSmplrtDiv, 0x04); !r) return r;

    // ±500 °/с — рукою стенд розгойдують до ~300 °/с, запас є.
    if (auto r = bus_.write_register(kAddress, kRegGyroConfig, 0x08); !r) return r;

    // ±2 g — найточніший діапазон, нахил міряємо в спокої.
    if (auto r = bus_.write_register(kAddress, kRegAccelConfig, 0x00); !r) return r;

    return Result<void, TwiError>::ok();
}

Result<ImuSample, TwiError> Mpu6050::read() noexcept {
    using R = Result<ImuSample, TwiError>;

    // 0x3B…0x48: ax, ay, az, температура, gx, gy, gz.
    std::array<std::uint8_t, 14> raw{};

    if (auto r = bus_.read_registers(kAddress, kRegAccelXoutH, raw); !r) {
        return R::fail(r.error());
    }

    ImuSample s;
    s.accel_y_g  = static_cast<float>(be16(raw[2], raw[3])) / kAccelLsbPerG;
    s.accel_z_g  = static_cast<float>(be16(raw[4], raw[5])) / kAccelLsbPerG;
    s.gyro_x_dps = static_cast<float>(be16(raw[8], raw[9])) / kGyroLsbPerDps;

    return R::ok(s);
}

}  // namespace gimbal
