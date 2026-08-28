#include <cstdint>

extern "C" void NMI_Handler()
{
    // Адреси регістрів RCC та TIM1
    auto& rcc_cir   = *reinterpret_cast<volatile std::uint32_t*>(0x4002380C);
    auto& tim1_bdtr = *reinterpret_cast<volatile std::uint32_t*>(0x40010044);

    // 1. Перевірка прапорця CSSF
    if (rcc_cir & (1UL << 7)) {
        // 2. Аварійне вимкнення силових виходів ШІМ
        tim1_bdtr &= ~(1UL << 15); // Очищення біта MOE (Main Output Enable)

        // 3. Очищення прапорця переривання CSS
        rcc_cir |= (1UL << 23); // Запис у CSSC

        // 4. Безпечна зупинка до скидання сторожовим таймером
        while (true) {
            asm volatile("nop");
        }
    }
}
