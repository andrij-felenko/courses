/* abi-probe.c — три різні «ні» від ядра на тому самому виклику.
   Збірка: cc -O2 -o abi-probe abi-probe.c                     */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <linux/openat2.h>      /* struct open_how, RESOLVE_* — з ядра 5.6 */

#ifndef __NR_openat2
#define __NR_openat2 437        /* однаковий на всіх архітектурах */
#endif

/* Повертає 0 або -errno. Відкриваємо поточний каталог: він є завжди. */
static long probe(const void *how, size_t size)
{
        long r = syscall(__NR_openat2, AT_FDCWD, ".", how, size);
        if (r >= 0) {
                close((int)r);
                return 0;
        }
        return -errno;
}

static void report(const char *what, long e)
{
        const char *why;

        switch (-e) {
        case 0:      why = "працює";                                      break;
        case ENOSYS: why = "такого виклику в цьому ядрі немає";           break;
        case EPERM:  why = "виклик є, але його зрізав фільтр";            break;
        case EINVAL: why = "виклик є, а цього біта прапорців — немає";    break;
        case E2BIG:  why = "структура довша за відому ядру, хвіст не нульовий"; break;
        default:     why = strerror((int)-e);                             break;
        }
        printf("%s — %s\n", what, why);
}

int main(void)
{
        struct open_how how;
        struct {
                struct open_how how;
                unsigned long long tail;   /* «поле з майбутнього» */
        } ext;

        /* 1. Чи є взагалі виклик. Нулі в структурі обов'язкові. */
        memset(&how, 0, sizeof how);
        how.flags = O_RDONLY;
        report("базовий виклик", probe(&how, sizeof how));

        /* 2. Чи вміє це ядро конкретну властивість. */
        memset(&how, 0, sizeof how);
        how.flags = O_RDONLY;
        how.resolve = RESOLVE_IN_ROOT;
        report("прапорець RESOLVE_IN_ROOT", probe(&how, sizeof how));

        /* 3. Невідомий біт: ядро зобов'язане відмовити, а не проковтнути. */
        memset(&how, 0, sizeof how);
        how.flags = O_RDONLY;
        how.resolve = 1ULL << 40;
        report("вигаданий біт", probe(&how, sizeof how));

        /* 4. Структура довша за відому ядру, і хвіст не нульовий. */
        memset(&ext, 0, sizeof ext);
        ext.how.flags = O_RDONLY;
        ext.tail = 1;
        report("поле з майбутнього", probe(&ext, sizeof ext));

        return 0;
}
