/* forklab.c — той самий кадр у кількох процесах і що з ним робить запис.
 *   cc -O2 -Wall -o forklab forklab.c && sudo ./forklab
 */
#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/wait.h>

#define PAGE 4096
#define KIDS 4

static uint64_t read_u64(const char *path, off_t off)
{
    uint64_t v = 0;
    int fd = open(path, O_RDONLY);
    if (fd < 0) return 0;
    if (pread(fd, &v, 8, off) != 8) v = 0;
    close(fd);
    return v;
}

static uint64_t pfn_of(const void *addr)
{
    uint64_t e = read_u64("/proc/self/pagemap", (off_t)((uintptr_t)addr / PAGE * 8));
    return (e & (1ULL << 63)) ? (e & ((1ULL << 55) - 1)) : 0;
}

static uint64_t mapcount_of(uint64_t pfn)
{
    return read_u64("/proc/kpagecount", (off_t)(pfn * 8));
}

int main(void)
{
    int go[2], hold[2];
    if (pipe(go) || pipe(hold)) return 1;

    char *p = mmap(NULL, PAGE, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) return 1;
    p[0] = 'A';                          /* збій запису — кадр щойно з'явився */

    uint64_t pfn = pfn_of(p);
    if (!pfn) { fprintf(stderr, "кадр 0: потрібен CAP_SYS_ADMIN\n"); return 1; }
    printf("кадр %#" PRIx64 ",  до fork      відображень: %" PRIu64 "\n",
           pfn, mapcount_of(pfn));
    fflush(stdout);                      /* щоб рядок не подвоївся в нащадках */

    for (int i = 0; i < KIDS; i++)
        if (fork() == 0) {
            char c;
            close(go[1]); close(hold[1]);
            read(go[0], &c, 1);          /* чекаємо дозволу писати */
            p[0] = (char)('a' + i);      /* копіювання при записі: власний кадр */
            read(hold[0], &c, 1);        /* тримаємося живими, доки батько міряє */
            _exit(0);
        }

    sleep(1);
    printf("             після fork    відображень: %" PRIu64 "\n", mapcount_of(pfn));

    write(go[1], "xxxx", KIDS);          /* хай усі напишуть у свою копію */
    sleep(1);
    printf("             після запису  відображень: %" PRIu64 "\n", mapcount_of(pfn));

    close(hold[1]);                      /* відпускаємо нащадків */
    while (wait(NULL) > 0) ;
    return 0;
}
