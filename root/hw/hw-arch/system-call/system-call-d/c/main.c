/* Один перетин межі на x86-64: номер у rax, три аргументи в rdi/rsi/rdx.
   Команда syscall затирає rcx і r11 — попереджаємо про це компілятор. */
static long raw_syscall3(long n, long a1, long a2, long a3) {
    long ret;
    __asm__ volatile ("syscall"
                      : "=a" (ret)
                      : "a" (n), "D" (a1), "S" (a2), "d" (a3)
                      : "rcx", "r11", "memory");
    return ret;
}

#define SYS_write 1

/* Те, що робить обгортка libc: розкласти одне число на результат і помилку. */
long my_write(int fd, const void *buf, unsigned long len, int *err) {
    long r = raw_syscall3(SYS_write, fd, (long)buf, (long)len);
    if (r < 0 && r >= -4095) {   /* увесь цей діапазон — коди помилок */
        *err = (int)(-r);        /* саме тут народжується errno */
        return -1;
    }
    *err = 0;
    return r;                    /* скільки байтів справді записано */
}
