#include "provoke.hpp"

#include <array>
#include <cstdint>

#include "trace.hpp"
#include "stm32f4xx.h"

namespace provoke {
namespace {

// Скрізь volatile і noinline: без них оптимізатор бачить неозначену поведінку,
// викидає код — і стенд перестає падати там, де мусить.
volatile std::uint8_t g_packet[8] = {0xAAU, 0x01U, 0x02U, 0x03U, 0x04U, 0x05U, 0x06U, 0x07U};

[[gnu::noinline]] std::uint32_t recurse(std::uint32_t depth)
{
    // Саме сирий масив, а не std::array: у std::array немає volatile-перевантаження
    // operator[], а без volatile оптимізатор просто прибрав би кадр.
    volatile std::uint8_t frame_eater[256];

    frame_eater[0] = static_cast<std::uint8_t>(depth);
    // Додавання після виклику не дає компілятору перетворити це на цикл.
    return frame_eater[0] + recurse(depth + 1U);
}

constexpr std::array kCases{
    Case{'1', "запис за NULL", &null_write},
    Case{'2', "периферія без тактування", &unclocked_peripheral},
    Case{'3', "невирівняне читання", &unaligned_load},
    Case{'4', "переповнення стека", &stack_overflow},
    Case{'5', "виклик за парною адресою", &bad_function_pointer},
    Case{'6', "ділення на нуль", &divide_by_zero},
    Case{'7', "зависання під сторожем", &watchdog_hang},
};

} // namespace

void null_write()
{
    trace::out.line("provoke: запис за нульовою адресою");

    // На STM32 за адресою 0 лежить дзеркало Flash: читання пройде, запис — ні.
    auto* const null_pointer = reinterpret_cast<volatile std::uint32_t*>(0x0000'0000U);
    *null_pointer            = 0xDEAD'BEEFU;
    __DSB();
}

void unclocked_peripheral()
{
    trace::out.line("provoke: доступ до периферії без тактування");

    // USART3, а не USART2: другий канал нам ще потрібен для звіту.
    RCC->APB1ENR &= ~RCC_APB1ENR_USART3EN;
    __DSB();

    USART3->CR1 = USART_CR1_UE; // міст APB відповість HRESP = ERROR
    __DSB();
}

void unaligned_load()
{
    trace::out.line("provoke: невирівняне читання слова");

    // Класика: у кадрі протоколу байт заголовка, а далі 32-бітне поле.
    const auto address = reinterpret_cast<std::uintptr_t>(&g_packet[1]);
    const volatile std::uint32_t value = *reinterpret_cast<const std::uint32_t*>(address);

    static_cast<void>(value); // спрацює лише при CCR.UNALIGN_TRP = 1
}

void stack_overflow()
{
    trace::out.line("provoke: рекурсія до переповнення стека");

    const volatile std::uint32_t sink = recurse(0U);
    static_cast<void>(sink);
}

void bad_function_pointer()
{
    trace::out.line("provoke: виклик за парною адресою (втрачено біт Thumb)");

    // Парна адреса означала б режим ARM, якого в Cortex-M фізично немає.
    auto* const callback = reinterpret_cast<void (*)()>(static_cast<std::uintptr_t>(0x0800'1000U));
    callback();
}

void divide_by_zero()
{
    trace::out.line("provoke: цілочислове ділення на нуль");

    volatile std::int32_t numerator   = 42;
    volatile std::int32_t denominator = 0;
    const volatile std::int32_t quotient = numerator / denominator;

    static_cast<void>(quotient); // спрацює лише при CCR.DIV_0_TRP = 1
}

void watchdog_hang()
{
    trace::out.line("provoke: зависання без скидання IWDG");
    trace::out.flush();

    for (;;) {
        __NOP(); // сторож добере своє й смикне лінію скидання
    }
}

std::span<const Case> catalogue() noexcept
{
    return kCases;
}

bool run(char key)
{
    for (const Case& item : kCases) {
        if (item.key == key) {
            item.run();
            return true;
        }
    }
    return false;
}

} // namespace provoke
