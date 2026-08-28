extern uint8_t __stack_bottom, __stack_top;   /* межі зі скрипта компонувальника */
#define PAINT 0xAAu

void stack_paint(void) {                       /* раз на старті, до глибоких викликів */
    for (uint8_t *p = &__stack_bottom; p < &__stack_top; ++p)
        *p = PAINT;
}

uint32_t stack_headroom(void) {                /* скільки байтів стек НЕ зачепив */
    uint8_t *p = &__stack_bottom;
    while (p < &__stack_top && *p == PAINT) ++p;
    return (uint32_t)(p - &__stack_bottom);    /* запас від дна до піку */
}
