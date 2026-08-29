// board.hpp — план виводів плати на час сну.
//
// План — constexpr-таблиця: компілятор сам ловить вивід, описаний двічі,
// а все, чого в таблиці немає, за замовчуванням їде в аналоговий режим.
// «Забути налаштувати ніжку» тут неможливо конструктивно.
#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <span>
#include <string_view>

#include "soc.hpp"

namespace board {

enum class SleepRole : std::uint8_t {
    Analog,    // цифровий буфер від'єднати: наскрізного струму немає
    ParkLow,   // притиснути до 0 В ДО розмикання ключа — анти-фантом
    KeepHigh,  // лишається виходом у стані 1 (затвор ключа)
    Wakeup,    // зміщений зовнішнім резистором вивід пробудження
    Sense      // вимірювальний вхід, вмикається на мікросекунди
};

struct PinSpec {
    const soc::GpioPort* port;
    std::uint8_t number;
    SleepRole role;
    std::string_view note;
};

inline constexpr std::array<PinSpec, 15> kPlan{{
    {&soc::portA,  0, SleepRole::Wakeup,  "PA0  WKUP1, кнопка, зовнішні 470 кОм"},
    {&soc::portA,  2, SleepRole::ParkLow, "PA2  USART2_TX до мосту USB-UART"},
    {&soc::portA,  3, SleepRole::Analog,  "PA3  USART2_RX"},
    {&soc::portA,  4, SleepRole::ParkLow, "PA4  SPI1_CS Flash (активний нуль)"},
    {&soc::portA,  5, SleepRole::ParkLow, "PA5  SPI1_SCK"},
    {&soc::portA,  6, SleepRole::Analog,  "PA6  SPI1_MISO"},
    {&soc::portA,  7, SleepRole::ParkLow, "PA7  SPI1_MOSI"},
    {&soc::portA, 13, SleepRole::Analog,  "PA13 SWDIO"},
    {&soc::portA, 14, SleepRole::Analog,  "PA14 SWCLK"},
    {&soc::portB,  1, SleepRole::Sense,   "PB1  дільник 1:2 з шини 3V3_SW"},
    {&soc::portB,  3, SleepRole::Analog,  "PB3  SWO"},
    {&soc::portB,  6, SleepRole::ParkLow, "PB6  I2C1_SCL, підтяжки з 3V3_SW"},
    {&soc::portB,  7, SleepRole::ParkLow, "PB7  I2C1_SDA"},
    {&soc::portB, 12, SleepRole::KeepHigh,"PB12 затвор ключа (1 = знеструмлено)"},
    {&soc::portC, 13, SleepRole::ParkLow, "PC13 світлодіод"},
}};

consteval bool planHasNoDuplicates() noexcept
{
    for (std::size_t i = 0; i < kPlan.size(); ++i) {
        for (std::size_t j = i + 1; j < kPlan.size(); ++j) {
            if (kPlan[i].port == kPlan[j].port && kPlan[i].number == kPlan[j].number) {
                return false;
            }
        }
    }
    return true;
}
static_assert(planHasNoDuplicates(), "один вивід описано в плані двічі");

[[nodiscard]] constexpr SleepRole roleOf(const soc::GpioPort& port, std::uint8_t pin) noexcept
{
    for (const PinSpec& spec : kPlan) {
        if (spec.port == &port && spec.number == pin) {
            return spec.role;
        }
    }
    return SleepRole::Analog; // не згаданий = невживаний
}

[[nodiscard]] constexpr std::span<const PinSpec> plan() noexcept
{
    return std::span<const PinSpec>{kPlan};
}

// Виводи, що лишилися цифровими входами без підтяжки: саме вони ловлять
// наводку на VDD/2 і відкривають обидва транзистори вхідного буфера.
struct FloatingPins {
    soc::Word inPortA{};
    soc::Word inPortB{};
    soc::Word inPortC{};
    unsigned count{};

    [[nodiscard]] constexpr bool none() const noexcept { return count == 0U; }
};

inline constexpr std::uint8_t kRailGatePin = 12U;
inline constexpr std::uint8_t kSensePin = 1U;
inline constexpr std::uint8_t kLedPin = 13U;

void initClocks() noexcept;
void initPins() noexcept;
void delayFor(std::chrono::milliseconds duration) noexcept;
void led(bool on) noexcept;

void parkSwitchedDomain() noexcept;
void allPinsToAnalog() noexcept;
void applyStandbyPulls() noexcept;

[[nodiscard]] FloatingPins auditFloating() noexcept;

// Ключ комутованої шини. Живою шину лишає тільки паразитне живлення
// через ESD-діод — саме це й перевіряє railIsDischarged().
void railOn() noexcept;
void railOff() noexcept;
[[nodiscard]] bool railIsDischarged() noexcept;

// RAII: шина датчика гасне разом з областю видимості, і сигнальні лінії
// паркуються ПЕРЕД тим, як зникне напруга. Жодного «не забути вимкнути»
// в гілках виходу — тому й немає goto out.
class SensorRail {
public:
    SensorRail() noexcept { railOn(); }

    ~SensorRail() noexcept
    {
        parkSwitchedDomain();
        railOff();
    }

    SensorRail(const SensorRail&) = delete;
    SensorRail& operator=(const SensorRail&) = delete;
    SensorRail(SensorRail&&) = delete;
    SensorRail& operator=(SensorRail&&) = delete;
};

} // namespace board
