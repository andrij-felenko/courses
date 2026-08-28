/* linkcount-audit.c — мініатюра четвертого проходу e2fsck.
 *
 * Обходить піддерево, рахує, скільки записів каталогів указують
 * на кожен номер inode, і звіряє пораховане з полем st_nlink.
 *
 *   cc -O2 -Wall -Wextra -o linkcount-audit linkcount-audit.c
 */
#define _GNU_SOURCE
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

struct rec {
    ino_t    ino;    /* 0 — комірка вільна: inode з номером 0 не буває */
    uint64_t seen;   /* скільки записів каталогів указали сюди */
    nlink_t  nlink;  /* що каже поле в самому inode */
    mode_t   mode;   /* тип: каталог чи ні */
    int      known;  /* чи знято stat хоч раз */
};

static struct rec *tab;
static size_t cap;   /* завжди степінь двійки */
static size_t used;

/* Номери inode йдуть майже поспіль, тож молодші біти самі по собі
   лягли б у сусідні комірки й дали довгі ланцюги проб. Перемішувач
   splitmix64 розкидає їх по всій таблиці. */
static uint64_t mix64(uint64_t x)
{
    x ^= x >> 33;  x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33;  x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33;
    return x;
}

static struct rec *slot_of(struct rec *t, size_t c, ino_t ino)
{
    size_t i = (size_t)(mix64((uint64_t)ino) & (uint64_t)(c - 1));
    while (t[i].ino != 0 && t[i].ino != ino)
        i = (i + 1) & (c - 1);
    return &t[i];
}

static void grow(void)
{
    size_t ncap = cap ? cap * 2 : 4096;
    struct rec *nt = calloc(ncap, sizeof *nt);
    if (!nt) { perror("calloc"); exit(8); }
    for (size_t i = 0; i < cap; i++)
        if (tab[i].ino != 0)
            *slot_of(nt, ncap, tab[i].ino) = tab[i];
    free(tab);
    tab = nt;
    cap = ncap;
}

static struct rec *find(ino_t ino)
{
    if (ino == 0) return NULL;
    if (used * 10 >= cap * 7) grow();     /* тримаємо заповнення нижче 70 % */
    struct rec *r = slot_of(tab, cap, ino);
    if (r->ino == 0) { r->ino = ino; used++; }
    return r;
}
