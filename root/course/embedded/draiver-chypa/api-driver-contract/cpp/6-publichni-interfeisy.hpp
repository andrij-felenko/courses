// C++20: Типізований контракт класу драйвера датчика
#pragma once

#include <cstdint>
#include <span>
#include <expected>
#include <concepts>

namespace embedded::drivers {

struct Vector3D {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};
};

template <typename T>
concept BusTransport = requires(T t, std::uint8_t reg, std::span<std::uint8_t> rx, std::span<const std::uint8_t> tx) {
    { t.read(reg, rx) } -> std::same_as<Status>;
    { t.write(reg, tx) } -> std::same_as<Status>;
    { t.delay_ms(std::uint32_t{}) } -> std::same_as<void>;
};

template <BusTransport Transport>
class ChipSensor {
public:
    explicit constexpr ChipSensor(Transport transport, std::uint8_t i2c_address = 0x19) noexcept
        : transport_(transport), address_(i2c_address) {}

    [[nodiscard]] Status init() noexcept;
    [[nodiscard]] Status setRange(std::uint8_t range_g) noexcept;
    [[nodiscard]] std::expected<Vector3D, Status> readAccelerationSi() noexcept;
    [[nodiscard]] Status softReset() noexcept;

    [[nodiscard]] constexpr bool isInitialized() const noexcept {
        return is_initialized_;
    }

private:
    Transport transport_;
    std::uint8_t address_{0x19};
    std::uint8_t shadow_ctrl_reg_{0x00};
    float scale_factor_{1.0F};
    bool is_initialized_{false};
};

} // namespace embedded::drivers
