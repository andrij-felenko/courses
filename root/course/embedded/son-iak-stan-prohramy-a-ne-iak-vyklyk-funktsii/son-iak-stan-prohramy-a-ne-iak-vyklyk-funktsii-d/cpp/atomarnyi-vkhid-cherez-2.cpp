/* Атомарний захищений вхід у сон ядра Cortex-M (C++20) */
namespace emb {

void atomicSleepEnter(const EventQueue& queue) noexcept {
    // 1. Блокуємо виклик ISR
    __asm volatile ("cpsid i" : : : "memory");

    // 2. Атомарна перевірка умов засинання
    if (queue.empty() && pm::PowerManager::instance().deepestAllowedMode() != pm::Mode::Active) {
        // SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
        __asm volatile ("dsb 0xF" ::: "memory");
        __asm volatile ("isb 0xF" ::: "memory");

        // 3. Апаратний сон ядра
        __asm volatile ("wfi");

        // SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
    }

    // 4. Дозвіл виконання накопичених обробників переривань
    __asm volatile ("cpsie i" : : : "memory");
}

} // namespace emb
