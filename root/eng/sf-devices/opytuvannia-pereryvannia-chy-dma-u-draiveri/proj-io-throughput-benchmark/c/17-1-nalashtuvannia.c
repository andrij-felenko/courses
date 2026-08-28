int _write(int file, char *ptr, int len) {
    (void)file;
    for (int i = 0; i < len; ++i) {
        // Запис у порт 0 модуля ITM
        if (CORE_DEBUG_BLOCK->DEMCR & DEMCR_TRCENA_BIT) {
            volatile uint32_t *ITM_PORT0 = (volatile uint32_t *)0xE0000000;
            volatile uint32_t *ITM_TER   = (volatile uint32_t *)0xE0000E00;
            if (*ITM_TER & 1u) {
                while (!(*ITM_PORT0 & 1u)) {}
                *((volatile uint8_t *)ITM_PORT0) = (uint8_t)ptr[i];
            }
        }
    }
    return len;
}
