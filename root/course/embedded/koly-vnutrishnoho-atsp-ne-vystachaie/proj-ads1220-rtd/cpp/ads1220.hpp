#pragma once

// ADS1220 у режимі 3-провідного PT100: два узгоджені струми збудження,
// логометрична опора на еталонному резисторі, одиничні перетворення
// й готовність результату за апаратним перериванням DRDY.

#include <cstdint>
#include <expected>
#include <string_view>

#include "spi_device.hpp"

namespace rtd {

enum class AdcError {
    Bus,               // обмін по SPI не відбувся
    ConfigMismatch,    // регістри прочиталися не такими, як записані
    Timeout,           // DRDY не впав за відведений час
    SensorOutOfRange   // код упертий у шкалу: обрив або замикання датчика
};

[[nodiscard]] std::string_view describe(AdcError error) noexcept;

class Ads1220 {
public:
    Ads1220(SpiDevice& bus, float refOhms, float gain) noexcept
        : bus_{&bus}, refOhms_{refOhms}, gain_{gain} {}

    // Скидає мікросхему, записує робочу конфігурацію й перечитує її назад.
    [[nodiscard]] std::expected<void, AdcError> init() noexcept;

    // Міряє власне зміщення нуля тракту на закорочених усередині входах.
    [[nodiscard]] std::expected<void, AdcError> calibrateOffset() noexcept;

    // Одне перетворення: повертає логометрично порахований опір датчика, Ом.
    [[nodiscard]] std::expected<float, AdcError> readResistance() noexcept;

    // Викликається з обробника спаду DRDY.
    void onDataReady() noexcept { dataReady_ = true; }

private:
    [[nodiscard]] std::expected<std::int32_t, AdcError> convertOnce() noexcept;
    [[nodiscard]] std::expected<void, AdcError> writeInputRegister(std::uint8_t value) noexcept;

    SpiDevice*    bus_;
    float         refOhms_;
    float         gain_;
    std::int32_t  offsetCode_{0};
    volatile bool dataReady_{false};
};

}  // namespace rtd
