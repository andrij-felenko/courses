#include <stddef.h>

static long sys_write(int fd, const void *buf, size_t n)
{
    long ret;
    __asm__ volatile (
        "syscall"
        : "=a"(ret)                                  /* результат — з rax */
        : "a"(1L), "D"((long)fd), "S"(buf), "d"(n)   /* номер, далі rdi, rsi, rdx */
        : "rcx", "r11", "memory");                   /* їх затирає сама інструкція */
    return ret;
}
