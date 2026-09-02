#include <algorithm>
#include <array>
#include <cstdint>

#include "mcu/registers.hpp"
#include "mcu/startup.hpp"
#include "mcu/uart.hpp"

/* Три змінні, кожна у своїй секції: перша несе початкове значення у
   Flash, дві інші в прошивці не займають жодного байта. */
int target_voltage = 3300;                        /* .data */
int current_reading = 0;                          /* .bss  */
std::array<std::uint8_t, 16384> dma_buffer{};     /* .bss: 16 КБ нулів */

extern "C" int main()
{
    /* Перевіряємо, що стартовий код справді відпрацював. Якби .data не
       скопіювали з Flash, тут лежало б увімкнене сміття SRAM. */
    if (target_voltage != 3300) {
        mcu::trap();
    }
    if (std::ranges::any_of(dma_buffer, [](std::uint8_t byte) { return byte != 0; })) {
        mcu::trap(); /* .bss не занулено */
    }

    /* Об'єкт зроблено за першим зверненням — порядок гарантований */
    mcu::console().write("startup: sections ready\n");

    /* А цей уже існував до першого рядка main(): його конструктор
       відпрацював під час обходу .init_array. */
    mcu::g_console_uart.write("startup: global ctor done\n");

    if (mcu::core_clock_hz < 168'000'000U) {
        mcu::console().write("clock: PLL failed, running on HSI\n");
    }

    /* Далі була б прикладна логіка; поки що — сон до переривання */
    for (;;) {
        current_reading = target_voltage;
        mcu::wait_for_interrupt();
    }
}
