extern uint32_t _siccmram;
extern uint32_t _sccmram;
extern uint32_t _eccmram;

void copy_ccmram_section_c(void) {
    uint32_t *src = &_siccmram;
    uint32_t *dst = &_sccmram;

    while (dst < &_eccmram) {
        *dst++ = *src++;
    }
}
