#pragma once

#include <optional>

#include "hal.hpp"

namespace board {

/* Розширювач MCP23017: порт A — входи (кінцевики, кнопки), порт B — вісім
   виходів реле. Саме такий розподіл описано в бюджеті плати реєстратора. */
class Mcp23017 {
public:
    static constexpr std::uint8_t kBaseAddress = 0x20;

    struct Config {
        std::uint8_t address{kBaseAddress};
        std::uint8_t inputs{};      /* IODIRA: 1 = вхід */
        std::uint8_t pullups{};     /* GPPUA: внутрішні 100 кОм */
        std::uint8_t inverted{};    /* IPOLA: замикання на землю читати як 1 */
        std::uint8_t interrupts{};  /* GPINTENA: які входи будять лінію INT */
    };

    struct Event {
        std::uint8_t address{};   /* який чип монтажного «АБО» озвався */
        std::uint8_t flags{};     /* INTF: піни, що викликали подію */
        std::uint8_t captured{};  /* INTCAP: зліпок входів на мить перепаду */
    };

    Mcp23017(I2cBus& bus, const Config& config) : bus_(bus), cfg_(config) {}

    Result<void> begin();
    Result<void> setRelays(std::uint8_t mask);
    Result<void> setRelay(std::uint8_t index, bool on);
    [[nodiscard]] Result<std::uint8_t> inputs();

    /* Порожній optional означає «спільну лінію тримав не цей чип». */
    [[nodiscard]] Result<std::optional<Event>> takeEvent();

    [[nodiscard]] std::uint8_t address() const noexcept { return cfg_.address; }

private:
    I2cBus& bus_;
    Config cfg_;
    std::uint8_t relayShadow_{0};
};

/* Кілька розширювачів, чиї виходи INT з відкритим стоком зведені монтажним
   «АБО» на єдиний вхід переривання мікроконтролера. */
class ExpanderBank {
public:
    ExpanderBank(std::span<Mcp23017> chips, GpioPort& gpio,
                 std::uint8_t intPin) noexcept
        : chips_(chips), gpio_(gpio), intPin_(intPin) {}

    [[nodiscard]] bool pending() const { return !gpio_.read(intPin_); }

    /* Обходить чипи, доки спільна лінія не підніметься. Повертає кількість
       складених у out подій. */
    Result<std::size_t> service(std::span<Mcp23017::Event> out);

private:
    static constexpr unsigned kMaxPasses = 4;

    std::span<Mcp23017> chips_;
    GpioPort& gpio_;
    std::uint8_t intPin_;
};

}  // namespace board
