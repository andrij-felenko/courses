// Цикл «прокинувся — виміряв — заснув» на STM32L4.
//
// Уся послідовність присипляння схована за одним сторожем: створення
// SleepScope готує плату, вихід з блоку її повертає. Через це в головному
// циклі видно лише роботу, а не порядок гасіння вузлів.
#include <array>
#include <chrono>
#include <span>
#include <string_view>

#include "bus_quiesce.hpp"
#include "mcu.hpp"
#include "pin_isolation.hpp"
#include "sensor_rail.hpp"
#include "sleep_scope.hpp"
#include "status.hpp"
#include "wakeup.hpp"

namespace {

using namespace std::chrono_literals;
using namespace lowpower;

constexpr auto kSleepDuration = 10s;

const mcu::Pin kRailGate{mcu::gpiob(), 12};   // затвор силового ключа
const mcu::Pin kWakeButton{mcu::gpioa(), 0};  // вхід пробудження EXTI0

// Виводи, які НЕ можна кидати в аналоговий режим.
//
// PA0 — кнопка й вхід пробудження. Аналоговий режим від'єднує тригер Шмітта,
//       і плата перестає бачити фронт: зовні це мертвий виріб, який оживає
//       лише зняттям живлення.
// PB12 — затвор ключа. Мусить лишатися виходом і тримати одиницю весь сон:
//       відпустиш у Hi-Z — затвор підтягнеться витоком, ключ привідкриється,
//       і датчики почнуть живитися посеред «глибокого сну».
const std::array kKeepAwake{kWakeButton, kRailGate};

// ------------------------------ журнал -----------------------------------

// Після сну модуль UART лишається вимкненим, а вивід PA2 — аналоговим.
// Тому кожен запис починається з питання, чи є чим писати.
void log_ready()
{
    auto& uart = mcu::usart2();
    if ((uart.cr1 & mcu::bits::kUsartUe) == 0U) {
        mcu::Pin{mcu::gpioa(), 2}.alternate(7);  // PA2 = USART2_TX
        uart.cr1 = mcu::bits::kUsartUe | mcu::bits::kUsartTe;
    }
}

void log(std::string_view text)
{
    log_ready();
    auto& uart = mcu::usart2();
    for (const char c : text) {
        while ((uart.isr & mcu::bits::kUsartIsrTxe) == 0U) {}
        uart.tdr = static_cast<mcu::u32>(static_cast<unsigned char>(c));
    }
}

void log(std::int32_t value)
{
    std::array<char, 12> buf{};
    auto pos = buf.size();
    auto magnitude = static_cast<std::uint32_t>(value < 0 ? -value : value);

    do {
        buf[--pos] = static_cast<char>('0' + magnitude % 10U);
        magnitude /= 10U;
    } while (magnitude != 0U);

    if (value < 0) { buf[--pos] = '-'; }
    log(std::string_view{buf.data() + pos, buf.size() - pos});
}

// -------------------------- початкова розкладка --------------------------

void board_init()
{
    auto& rcc = mcu::rcc();
    mcu::set_bits(rcc.ahb2enr, mcu::bits::kRccGpioAEn | mcu::bits::kRccGpioBEn |
                               mcu::bits::kRccGpioCEn);
    mcu::set_bits(rcc.apb1enr1, mcu::bits::kRccUsart2En | mcu::bits::kRccI2c1En |
                                mcu::bits::kRccPwrEn);
    mcu::set_bits(rcc.apb2enr, mcu::bits::kRccSpi1En);

    // Силовий ключ: спершу рівень, потім режим виходу. Навпаки — і затвор на
    // мить дістане старий вміст засувки, а ключ моргне.
    kRailGate.write(true);  // закритий
    kRailGate.mode(mcu::Mode::Output);

    // UART журналу: PA2 — TX, PA3 — RX.
    mcu::Pin{mcu::gpioa(), 2}.alternate(7);
    mcu::Pin{mcu::gpioa(), 3}.alternate(7);
    mcu::usart2().brr = mcu::kCpuHz / 115200U;  // 4 МГц / 115200 = 35, похибка ~2%
    mcu::usart2().cr1 = mcu::bits::kUsartUe | mcu::bits::kUsartTe;

    // I2C1: PB8 — SCL, PB9 — SDA, обидва з відкритим стоком. Підтяжки
    // зовнішні, на шині датчиків, і зникають разом із нею.
    for (const auto& pin : {mcu::Pin{mcu::gpiob(), 8}, mcu::Pin{mcu::gpiob(), 9}}) {
        pin.open_drain(true);
        pin.alternate(4);
    }
    mcu::i2c1().timingr = 0x0042'0F13U;  // 100 кГц від 4 МГц
    mcu::i2c1().cr1 = mcu::bits::kI2cPe;

    // SPI1 на PA5/PA6/PA7 — зовнішня флеш-пам'ять журналу. У цьому прикладі
    // вона не читається, але вона є на платі, і її шину теж треба зупиняти:
    // обірваний кадр SPI лишає ведений із піднятим CS.
    for (unsigned n : {5U, 6U, 7U}) {
        mcu::Pin{mcu::gpioa(), n}.alternate(5);
    }
    mcu::spi1().cr1 = 0U;
}

} // namespace

int main()
{
    board_init();
    wakeup::init();

    SensorRail rail{kRailGate};
    PinIsolator pins{std::span<const mcu::Pin>{kKeepAwake}};

    log("\r\nстарт\r\n");

    for (;;) {
        if (auto powered = rail.power_up(); !powered) {
            log("живлення датчиків: ");
            log(describe(powered.error()));
            log("\r\n");

            // Шина могла лишитися заклиненою після зриву транзакції —
            // пробуємо розклинити її дев'ятьма тактами.
            if (auto recovered = recover_i2c_bus(); !recovered) {
                log("i2c не розклинилася\r\n");
            }
        } else if (auto temperature = rail.read_temperature_raw(); temperature) {
            log("t_raw=");
            log(*temperature);
            log("\r\n");
        } else {
            log("вимір: ");
            log(describe(temperature.error()));
            log("\r\n");
        }

        if (auto slept = deep_sleep_for(rail, pins, kSleepDuration); !slept) {
            log("сон: ");
            log(describe(slept.error()));
            log("\r\n");
        }

        const auto reason = wakeup::last_reason();
        log("прокинулися: ");
        log(reason ? describe(*reason) : std::string_view{"невідомо"});
        log("\r\n");
    }
}
