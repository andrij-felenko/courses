/* НАДІЙНИЙ ВАРІАНТ на C++ з використанням інструкції DSB */
extern "C" void TIM2_IRQHandler() {
    if ((TIM2->SR & TIM_SR_UIF) != 0) {
        TIM2->SR = ~TIM_SR_UIF;
        
        // Бар'єр синхронізації даних гарантує завершення запису на шині
        __asm volatile ("dsb" ::: "memory");

        do_fast_action();
    }
}
