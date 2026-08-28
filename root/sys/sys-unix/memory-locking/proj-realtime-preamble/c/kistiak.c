#define _GNU_SOURCE
#include <sys/mman.h>
#include <sys/resource.h>
#include <malloc.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

static void die(const char *what) { perror(what); exit(1); }

/* Скільки байтів прибив саме цей процес: рядок VmLck, у кілобайтах. */
static long vmlck_kib(void)
{
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return -1;
    char line[256];
    long kib = -1;
    while (fgets(line, sizeof line, f))
        if (sscanf(line, "VmLck: %ld kB", &kib) == 1) break;
    fclose(f);
    return kib;
}

static void lock_everything(void)
{
    if (mlockall(MCL_CURRENT | MCL_FUTURE) == 0)
        return;

    int err = errno;                  /* getrlimit нижче має право його затерти */
    struct rlimit rl = { 0, 0 };
    getrlimit(RLIMIT_MEMLOCK, &rl);

    if (err == ENOMEM)
        fprintf(stderr, "mlockall: уперлися в межу прибитої пам'яті; "
                        "м'яка %llu Б, жорстка %llu Б, уже прибито %ld КіБ\n",
                (unsigned long long) rl.rlim_cur,
                (unsigned long long) rl.rlim_max, vmlck_kib());
    else if (err == EPERM)
        fprintf(stderr, "mlockall: межа нульова, а CAP_IPC_LOCK немає\n");

    errno = err;
    die("mlockall");
}

#define STACK_WARM (64 * 1024)        /* із запасом на найглибший ланцюг викликів */

static void warm_stack(void)
{
    unsigned char buf[STACK_WARM];
    memset(buf, 0, sizeof buf);       /* саме ЗАПИС — чому, див. пастки нижче */
    __asm__ __volatile__("" :: "r"(buf) : "memory");   /* щоб memset не викинули */
}

static void warm_heap(size_t bytes)
{
    if (!mallopt(M_TRIM_THRESHOLD, -1)   /* free() більше не зсуває верх купи вниз */
     || !mallopt(M_MMAP_MAX, 0)          /* великі шматки теж із купи, не окремим mmap */
     || !mallopt(M_ARENA_MAX, 1)) {      /* усі потоки — через одну, розігріту купу */
        fprintf(stderr, "mallopt: розподільник не прийняв налаштування\n");
        exit(1);
    }

    size_t page = (size_t) sysconf(_SC_PAGESIZE);
    unsigned char *p = malloc(bytes);
    if (!p) die("malloc");
    for (size_t i = 0; i < bytes; i += page)
        p[i] = 1;                        /* по одному запису на сторінку */
    free(p);                             /* пам'ять лишається за процесом */
}

static void preamble(size_t working_set)
{
    lock_everything();
    warm_stack();
    warm_heap(working_set);
    fprintf(stderr, "готово: прибито %ld КіБ\n", vmlck_kib());
}
