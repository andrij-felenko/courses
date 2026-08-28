void check_overflow_classic(int a, int b) noexcept {
    int is_overflow = 0;
    asm ("addl %2, %0\n\t"
         "seto %b1"
         : "+r" (a), "=q" (is_overflow)
         : "r" (b)
         : "cc");
    if (is_overflow) {
        /* Обробка помилки */
    }
}
