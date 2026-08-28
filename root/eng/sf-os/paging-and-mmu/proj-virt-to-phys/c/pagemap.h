/* pagemap.h — читання /proc/self/pagemap. Включати ПЕРШИМ:
   макроси нижче мусять з'явитися раніше за будь-який системний заголовок. */
#ifndef PAGEMAP_H
#define PAGEMAP_H

#define _GNU_SOURCE               /* fork, MAP_ANONYMOUS, pread */
#define _FILE_OFFSET_BITS 64      /* 64-бітний off_t і на 32-бітній машині */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

#define PM_PRESENT    (1ULL << 63)
#define PM_SWAP       (1ULL << 62)
#define PM_FILE       (1ULL << 61)
#define PM_UFFD_WP    (1ULL << 57)
#define PM_EXCLUSIVE  (1ULL << 56)
#define PM_SOFT_DIRTY (1ULL << 55)
#define PM_PFN_MASK   ((1ULL << 55) - 1)

static inline long pm_page_size(void)
{
    static long ps;
    if (ps == 0) {
        ps = sysconf(_SC_PAGESIZE);      /* НЕ 4096: гранула буває й 16, і 64 КіБ */
        if (ps <= 0) { perror("sysconf(_SC_PAGESIZE)"); exit(1); }
    }
    return ps;
}

static inline int pm_open(void)
{
    int fd = open("/proc/self/pagemap", O_RDONLY);
    if (fd < 0) { perror("open /proc/self/pagemap"); exit(1); }
    return fd;
}

/* 0 — слово прочитано; -1 — адреса вища за межу простору (коротке читання) */
static inline int pm_read(int fd, const void *addr, uint64_t *word)
{
    uint64_t ps  = (uint64_t)pm_page_size();
    uint64_t vpn = (uint64_t)(uintptr_t)addr / ps;
    ssize_t  n   = pread(fd, word, sizeof *word, (off_t)(vpn * 8));

    if (n == (ssize_t)sizeof *word) return 0;
    if (n < 0) { perror("pread pagemap"); exit(1); }
    return -1;
}

static inline void pm_print(const char *what, const void *addr, uint64_t w)
{
    uint64_t ps = (uint64_t)pm_page_size();
    unsigned long long va = (unsigned long long)(uintptr_t)addr;

    printf("%s — va=0x%012llx  ", what, va);

    if (w & PM_PRESENT) {
        uint64_t pfn = w & PM_PFN_MASK;
        if (pfn != 0)
            printf("кадр=0x%llx  фіз=0x%012llx",
                   (unsigned long long)pfn,
                   (unsigned long long)(pfn * ps + va % ps));
        else
            printf("кадр прихований (немає CAP_SYS_ADMIN)");

        printf("  %s%s", (w & PM_EXCLUSIVE) ? "власна" : "СПІЛЬНА",
                         (w & PM_FILE)      ? ", файлова" : "");
    } else if (w & PM_SWAP) {
        printf("у підкачці: область %llu, слот 0x%llx",
               (unsigned long long)(w & 0x1f),
               (unsigned long long)((w >> 5) & ((1ULL << 50) - 1)));
    } else {
        printf("кадру немає — сторінки ще не торкалися");
    }
    putchar('\n');
}

#endif
