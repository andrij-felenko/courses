/* Копіювання секції .ramfunc у C */
extern uint32_t _si_ramfunc; /* Початок у Flash */
extern uint32_t _sramfunc;    /* Початок у RAM */
extern uint32_t _eramfunc;    /* Кінець у RAM */

void copy_ramfunc_to_ram(void) {
    uint32_t *src = &_si_ramfunc;
    uint32_t *dst = &_sramfunc;
    while (dst < &_eramfunc) {
        *dst++ = *src++;
    }
    __DSB();
    __ISB();
}
