extern "C" int _write(int file, char *ptr, int len) {
    static_cast<void>(file);
    for (int i = 0; i < len; ++i) {
        // Запис у порт 0 модуля ITM
        if (DEBUG_REGS->DEMCR & DEMCR_TRCENA) {
            auto* const itm_port0 = reinterpret_cast<volatile uint32_t*>(0xE0000000);
            auto* const itm_ter   = reinterpret_cast<volatile uint32_t*>(0xE0000E00);
            if (*itm_ter & 1u) {
                while (!(*itm_port0 & 1u)) {}
                *reinterpret_cast<volatile uint8_t*>(itm_port0) = static_cast<uint8_t>(ptr[i]);
            }
        }
    }
    return len;
}
