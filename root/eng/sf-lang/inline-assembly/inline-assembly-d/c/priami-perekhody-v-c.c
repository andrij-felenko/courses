/* Звичайний підхід: генерація проміжного прапорця */
void check_overflow_classic(int a, int b) {
    int is_overflow;
    __asm__ ("addl %2, %0\n\t"
             "seto %b1"
             : "+r" (a), "=q" (is_overflow)
             : "r" (b)
             : "cc");
    if (is_overflow) {
        /* Обробка помилки */
    }
}
