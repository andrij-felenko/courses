namespace fault::diag {

inline void enable_diagnostics() noexcept {
    // 1. Увімкнути роздільні обробники винятків у SHCSR
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk |
                  SCB_SHCSR_BUSFAULTENA_Msk |
                  SCB_SHCSR_USGFAULTENA_Msk;

    // 2. Увімкнути пастки помилок ділення на нуль і невирівняного доступу
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk |
                SCB_CCR_UNALIGN_TRP_Msk;

    #ifdef DEBUG
    // 3. Вимкнути буферизацію запису шини для точної локалізації BusFault
    SCB->ACTLR |= SCB_ACTLR_DISDEFWBUF_Msk;
    #endif
}

} // namespace fault::diag
