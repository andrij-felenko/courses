static long raw_syscall4(long n, long a1, long a2, long a3, long a4)
{
    long ret;
    register long r10 __asm__("r10") = a4;
    __asm__ volatile ("syscall"
        : "=a" (ret)
        : "a" (n), "D" (a1), "S" (a2), "d" (a3), "r" (r10)
        : "rcx", "r11", "memory");
    return ret;
}
