#include "mcu/uart.hpp"

#include <cstdint>

#include "mcu/registers.hpp"
#include "mcu/startup.hpp"

namespace {

/* GPIOA (0x40020000) і USART1 (0x40011000) у STM32F4 */
using gpioa_moder   = mcu::reg32<0x40020000UL>;
using gpioa_ospeedr = mcu::reg32<0x40020008UL>;
using gpioa_afrh    = mcu::reg32<0x40020024UL>;
using usart1_sr     = mcu::reg32<0x40011000UL>;
using usart1_dr     = mcu::reg32<0x40011004UL>;
using usart1_brr    = mcu::reg32<0x40011008UL>;
using usart1_cr1    = mcu::reg32<0x4001100CUL>;

constexpr std::uint32_t gpioa_clock  = 1U << 0; /* RCC_AHB1ENR.GPIOAEN */
constexpr std::uint32_t usart1_clock = 1U << 4; /* RCC_APB2ENR.USART1EN */
constexpr std::uint32_t tx_pin = 9;             /* PA9 = USART1_TX */
constexpr std::uint32_t alt_func_usart1 = 7;    /* AF7 */
constexpr std::uint32_t cr1_te = 1U << 3;       /* передавач */
constexpr std::uint32_t cr1_ue = 1U << 13;      /* сам модуль */
constexpr std::uint32_t sr_txe = 1U << 7;       /* регістр даних вільний */

} // namespace

namespace mcu {

uart::uart(std::uint32_t baud_rate) noexcept : baud_{baud_rate}
{
    rcc::ahb1enr::set(gpioa_clock);
    rcc::apb2enr::set(usart1_clock);

    /* PA9 → режим альтернативної функції, і саме AF7 (USART1) */
    gpioa_moder::modify(0b11U << (tx_pin * 2), 0b10U << (tx_pin * 2));
    gpioa_ospeedr::set(0b10U << (tx_pin * 2)); /* швидкий фронт */
    gpioa_afrh::modify(0xFU << ((tx_pin - 8) * 4),
                       alt_func_usart1 << ((tx_pin - 8) * 4));

    /* USART1 висить на APB2 — там половина частоти ядра. Регістр BRR і
       є fck/baud у шістнадцятих частках такту, тож ділимо з округленням.
       Значення core_clock_hz бере той стан, у якому тактування лишив
       стартовий код: конструктор глобального об'єкта виконується вже
       після configure_clock(). */
    const std::uint32_t pclk2 = core_clock_hz / 2U;
    usart1_brr::write((pclk2 + baud_rate / 2U) / baud_rate);
    usart1_cr1::write(cr1_ue | cr1_te);
}

void uart::put(char symbol) const noexcept
{
    while (!usart1_sr::all_set(sr_txe)) {
        /* чекаємо, поки зсувний регістр забере попередній байт */
    }
    usart1_dr::write(static_cast<std::uint32_t>(static_cast<unsigned char>(symbol)));
}

void uart::write(std::string_view text) const noexcept
{
    for (const char symbol : text) {
        if (symbol == '\n') {
            put('\r'); /* термінали чекають пари CR+LF */
        }
        put(symbol);
    }
}

/* Ось той самий глобальний об'єкт із прози: покажчик на його конструктор
   компілятор кладе в .init_array, і стартовий код викличе його до
   main() — але в порядку, якого стандарт не визначає. */
uart g_console_uart{115200};

/* Ініціалізація за першим зверненням. Локальний static конструюється в
   мить першого виклику, тому порядок між файлами вже не має значення.
   Прошивку збирають із -fno-threadsafe-statics: на голому залізі до
   першого виклику ще немає ні планувальника, ні другого потоку, а
   інакше GCC потягнув би за собою __cxa_guard_acquire. */
uart& console() noexcept
{
    static uart instance{115200};
    return instance;
}

} // namespace mcu
