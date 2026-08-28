/* nolibc.c — програма без бібліотеки: своя точка входу, свій вихід */

#define SYS_write       1
#define SYS_exit_group  231

static long syscall3(long n, long a1, long a2, long a3)
{
    long ret;
    __asm__ volatile ("syscall"
        : "=a" (ret)
        : "a" (n), "D" (a1), "S" (a2), "d" (a3)
        : "rcx", "r11", "memory");
    return ret;
}

/* strlen теж нема кому надати */
static unsigned long slen(const char *s)
{
    const char *p = s;
    while (*p) p++;
    return (unsigned long)(p - s);
}

static void put(const char *s)
{
    syscall3(SYS_write, 1, (long)s, (long)slen(s));
}

/* ані printf, ані snprintf: десяткове число теж наша робота */
static void put_ulong(unsigned long v)
{
    char buf[21];                       /* 20 цифр максимум плюс перевід рядка */
    char *p = buf + sizeof buf;
    *--p = '\n';
    if (v == 0) *--p = '0';
    while (v) { *--p = (char)('0' + v % 10); v /= 10; }
    syscall3(SYS_write, 1, (long)p, (long)(buf + sizeof buf - p));
}

/* Сюди _start передає вершину стека такою, якою її лишило ядро */
void c_start(long *sp)
{
    long argc   = sp[0];
    char **argv = (char **)(sp + 1);
    char **envp = argv + argc + 1;      /* одразу за NULL-завершувачем argv */

    put("аргументів: ");
    put_ulong((unsigned long)argc);
    for (long i = 0; i < argc; i++) {
        put("  ");
        put(argv[i]);
        put("\n");
    }
    put("перша змінна оточення: ");
    put(envp[0] ? envp[0] : "(немає)");
    put("\n");

    syscall3(SYS_exit_group, 0, 0, 0);
    __builtin_unreachable();            /* повертатися нікуди */
}

__asm__(
    ".globl _start           \n"
    "_start:                 \n"
    "    xor  %ebp, %ebp     \n"   /* найзовнішній кадр: розкрутка стека спиниться тут */
    "    mov  %rsp, %rdi     \n"   /* перший аргумент c_start — сам покажчик стека */
    "    and  $-16, %rsp     \n"   /* угода про виклик вимагає вирівняного стека */
    "    call c_start        \n"
);
