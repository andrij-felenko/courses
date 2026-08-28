/* init.c — PID 1 без жодної бібліотеки: самі системні виклики.
   Номери — з arch/x86/entry/syscalls/syscall_64.tbl (x86-64). */
#define SYS_write       1
#define SYS_mkdir      83
#define SYS_mount     165
#define SYS_reboot    169
#define SYS_exit_group 231

static long sys(long n, long a, long b, long c, long d, long e)
{
    long ret;
    register long r10 __asm__("r10") = d;
    register long r8  __asm__("r8")  = e;
    __asm__ volatile ("syscall"
                      : "=a"(ret)
                      : "a"(n), "D"(a), "S"(b), "d"(c), "r"(r10), "r"(r8)
                      : "rcx", "r11", "memory");
    return ret;
}

static unsigned long slen(const char *s)
{
    unsigned long n = 0;
    while (s[n]) n++;
    return n;
}

static void say(const char *s)
{
    sys(SYS_write, 1, (long)s, (long)slen(s), 0, 0);
}

void _start(void)
{
    say("\n=== вітання від PID 1 ===\n");

    sys(SYS_mkdir, (long)"/proc", 0755, 0, 0, 0);
    if (sys(SYS_mount, (long)"proc", (long)"/proc", (long)"proc", 0, 0) == 0)
        say("/proc змонтовано\n");
    else
        say("/proc змонтувати не вдалося\n");

    say("вимикаюся\n");
    /* magic1 = 0xfee1dead, magic2 = 672274793 (0x28121969 — 28.12.1969) */
    sys(SYS_reboot, 0xfee1dead, 672274793, 0x4321FEDC, 0, 0);

    /* сюди не доходимо; але мовчки повертатися з _start не можна — нікуди */
    sys(SYS_exit_group, 1, 0, 0, 0, 0);
    for (;;) ;
}
