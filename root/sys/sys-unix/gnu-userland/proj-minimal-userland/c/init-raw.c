/* init-raw.c — жодної бібліотеки, самі системні виклики.
   gcc -static -nostdlib -nostartfiles -Os -o init init-raw.c */

static long sys(long n, long a, long b, long c, long d, long e)
{
    register long r10 __asm__("r10") = d;
    register long r8  __asm__("r8")  = e;
    long ret;
    __asm__ volatile ("syscall"
                      : "=a"(ret)
                      : "a"(n), "D"(a), "S"(b), "d"(c), "r"(r10), "r"(r8)
                      : "rcx", "r11", "memory");
    return ret;
}

#define SYS_write   1
#define SYS_pause  34
#define SYS_mount 165

void _start(void)
{
    static const char msg[] = "init: без libc, самі системні виклики\n";

    sys(SYS_mount, (long)"proc", (long)"/proc", (long)"proc", 0, 0);
    sys(SYS_write, 1, (long)msg, sizeof msg - 1, 0, 0);

    for (;;)
        sys(SYS_pause, 0, 0, 0, 0, 0);
}
