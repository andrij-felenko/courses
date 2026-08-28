/* inodesum.c — облік місця в дереві за тотожністю inode.
 *
 *   cc -Wall -Wextra -O2 -o inodesum inodesum.c
 *
 * POSIX.1-2008 (openat/fstatat/fdopendir). Одиниця st_blocks — 512 Б: це
 * правда для Linux, POSIX її не фіксує.
 */
#define _POSIX_C_SOURCE 200809L

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define BLOCK_UNIT   512      /* одиниця st_blocks у Linux */
#define SPARSE_TOP   5        /* скільки найдірявіших файлів показати */

/* Локальні ФС переривань зазвичай не віддають, а от FUSE і мережеві —
 * цілком. Повторюємо самі: перерваний виклик не є помилкою. */
static int fstatat_retry(int dfd, const char *name, struct stat *st, int flags)
{
    int r;
    do { r = fstatat(dfd, name, st, flags); } while (r != 0 && errno == EINTR);
    return r;
}

static int openat_retry(int dfd, const char *name, int flags)
{
    int fd;
    do { fd = openat(dfd, name, flags); } while (fd < 0 && errno == EINTR);
    return fd;
}

/* ── шлях, який росте ────────────────────────────────────────────────── */

struct pathbuf { char *s; size_t len, cap; };

static int path_reserve(struct pathbuf *p, size_t need)
{
    if (need <= p->cap) return 1;
    size_t cap = p->cap ? p->cap : 256;
    while (cap < need) cap *= 2;
    char *s = realloc(p->s, cap);
    if (s == NULL) return 0;
    p->s = s; p->cap = cap;
    return 1;
}

static int path_set(struct pathbuf *p, const char *s)
{
    size_t n = strlen(s);
    if (!path_reserve(p, n + 1)) return 0;
    memcpy(p->s, s, n + 1);
    p->len = n;
    return 1;
}

/* Дописує "/ім'я". Викликач запам'ятовує p->len ДО виклику і відновлює
 * його після — це і є вихід із підкаталогу. */
static int path_push(struct pathbuf *p, const char *name)
{
    size_t n = strlen(name);
    if (!path_reserve(p, p->len + 1 + n + 1)) return 0;
    if (p->len > 0 && p->s[p->len - 1] != '/')
        p->s[p->len++] = '/';
    memcpy(p->s + p->len, name, n + 1);
    p->len += n;
    return 1;
}

/* ── список імен одного каталогу ─────────────────────────────────────── */

struct namelist { char **v; size_t n, cap; };

static int names_push(struct namelist *l, const char *name)
{
    if (l->n == l->cap) {
        size_t cap = l->cap ? l->cap * 2 : 64;
        char **v = realloc(l->v, cap * sizeof *v);
        if (v == NULL) return 0;
        l->v = v; l->cap = cap;
    }
    char *copy = strdup(name);
    if (copy == NULL) return 0;
    l->v[l->n++] = copy;
    return 1;
}

static void names_free(struct namelist *l)
{
    for (size_t i = 0; i < l->n; i++) free(l->v[i]);
    free(l->v);
    memset(l, 0, sizeof *l);
}

static int cmp_name(const void *a, const void *b)
{
    return strcmp(*(char *const *)a, *(char *const *)b);
}
