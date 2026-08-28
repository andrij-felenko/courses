/* two-doors.c — той самий write двома входами, повз бібліотеку C */
#include <stdio.h>

static char msg_int80[]   = "door: int 0x80\n";
static char msg_syscall[] = "door: syscall\n";

/* Домовленість i386: номер у EAX, аргументи в EBX, ECX, EDX. */
static long write_int80(int fd, const void *buf, unsigned long len)
{
    long ret;
    __asm__ volatile ("int $0x80"
                      : "=a" (ret)
                      : "a" (4),        /* write у 32-бітній таблиці */
                        "b" (fd), "c" (buf), "d" (len)
                      : "memory");
    return ret;
}

#ifdef __x86_64__
/* Домовленість x86-64: номер у RAX, аргументи в RDI, RSI, RDX. */
static long write_syscall(int fd, const void *buf, unsigned long len)
{
    long ret;
    __asm__ volatile ("syscall"
                      : "=a" (ret)
                      : "a" (1),        /* write у 64-бітній таблиці */
                        "D" (fd), "S" (buf), "d" (len)
                      : "rcx", "r11", "memory");
    return ret;
}
#endif

int main(void)
{
    long r1 = write_int80(1, msg_int80, sizeof msg_int80 - 1);
    fprintf(stderr, "int 0x80 -> %ld\n", r1);

#ifdef __x86_64__
    long r2 = write_syscall(1, msg_syscall, sizeof msg_syscall - 1);
    fprintf(stderr, "syscall  -> %ld\n", r2);
#endif
    return 0;
}
