#include <stddef.h>

static long raw_syscall3(long n, long a1, long a2, long a3)
{
    long ret;
    __asm__ volatile (
        "syscall"
        : "=a" (ret)                                   /* вихід — rax */
        : "a" (n), "D" (a1), "S" (a2), "d" (a3)        /* rax, rdi, rsi, rdx */
        : "rcx", "r11", "memory");                     /* що псує інструкція */
    return ret;
}
