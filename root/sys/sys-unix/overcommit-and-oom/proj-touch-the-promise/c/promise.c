/* promise.c — лабораторія overcommit: обіцянка, дотик, стіна.
   Збірка:  cc -O2 -std=gnu11 -o promise promise.c
   Запуск:  ./promise <режим> [опції]

   режими   reserve   узяти обіцянку й спинитися
            touch     торкатися шматками з паузою
            wall      торкатися без пауз — до кінця

   опції    --size G      розмір обіцянки, ГіБ      (типово 8)
            --step M      крок торкання, МіБ        (типово 256)
            --pause MS    пауза між кроками, мс     (типово 0)
            --noreserve   mmap із MAP_NORESERVE замість malloc
            --calloc      calloc замість malloc
            --read        читати замість писати
            --release     після кожного кроку віддавати щойно взяте
            --limit-as G  RLIMIT_AS перед обіцянкою, ГіБ
            --adj N       записати N у /proc/self/oom_score_adj          */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/resource.h>

#define MIB (1024UL * 1024)
#define GIB (1024UL * MIB)

static size_t pgsz;               /* справжній розмір сторінки цієї машини */

/* Значення рядка «Ключ:  ЧИСЛО kB» у /proc-файлі; -1, якщо ключа нема. */
static long field_kb(const char *path, const char *key)
{
    FILE *f = fopen(path, "re");           /* 'e' — O_CLOEXEC, розширення glibc */
    if (!f) return -1;
    const size_t klen = strlen(key);
    char line[256];
    long val = -1;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, key, klen) && line[klen] == ':') {
            val = strtol(line + klen + 1, NULL, 10);   /* пробіли strtol з'їсть сам */
            break;
        }
    fclose(f);
    return val;
}
