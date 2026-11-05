// Точна затримка на обчислену кількість тактів у SRAM.
// Секція .ramfunc усуває затримки вибірки інструкцій із Flash-пам'яті.
__attribute__((noinline, section(".ramfunc")))
void delay_exact_cycles(uint32_t cycles) {
    if (cycles <= 6) {
        return;
    }
    // Віднімання накладних витрат на виклик функції та перевірку умов
    cycles -= 6;

    uint32_t iterations = cycles / 3;
    uint32_t remainder = cycles % 3;

    // Асемблерний цикл: subs (1 такт) + bne (2 такти) = 3 такти на ітерацію
    __asm__ volatile (
        "1: \n\t"
        "subs %[cnt], %[cnt], #1 \n\t"
        "bne 1b \n\t"
        : [cnt] "+r" (iterations)
        :
        : "cc"
    );

    // Добирання залишкових тактів одиночними інструкціями NOP
    if (remainder == 1) {
        __asm__ volatile ("nop");
    } else if (remainder == 2) {
        __asm__ volatile ("nop\n\tnop");
    }
}
