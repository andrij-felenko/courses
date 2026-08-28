#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/prctl.h>

#ifndef PR_SET_MEMORY_MERGE
#define PR_SET_MEMORY_MERGE 67
#define PR_GET_MEMORY_MERGE 68
#endif

int main(void)
{
    const size_t len = 64u << 20;   /* 64 МіБ */

    /* Анонімна приватна ділянка — єдиний тип, який KSM бере. */
    void *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); return 1; }
    memset(p, 0xA5, len);           /* однаковий вміст у всіх сторінках */

    /* Дозвіл на цю ділянку. Нуль НЕ означає «взято в роботу». */
    if (madvise(p, len, MADV_MERGEABLE) != 0) { perror("madvise"); return 1; }

    /* Або дозвіл на весь процес одразу (ядро 6.4+), зі спадкуванням. */
    if (prctl(PR_SET_MEMORY_MERGE, 1, 0, 0, 0) != 0)
        perror("prctl");            /* не смертельно: старе ядро або без CONFIG_KSM */

    printf("pid=%d addr=%p\n", getpid(), p);
    pause();                        /* тримаємо пам'ять, щоб було що сканувати */
    return 0;
}
