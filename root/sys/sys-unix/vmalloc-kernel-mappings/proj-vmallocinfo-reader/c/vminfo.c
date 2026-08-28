/* vminfo.c — хто тримає область vmalloc.
 *   cc -O2 -Wall -Wextra -std=c11 -o vminfo vminfo.c
 *   sudo ./vminfo               # читає /proc/vmallocinfo
 *   sudo ./vminfo знімок.txt    # розбирає збережену копію
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXA  (1 << 17)          /* ділянок: з великим запасом */
#define MAXO  4096               /* різних викликачів */
#define WHO   96                 /* довжина ключа «функція [модуль]» */
#define TOPN  ((size_t)10)
#define MIB   1048576.0
#define GIB   1073741824.0

enum { K_AREA, K_MAPRAM, K_UNPURGED };

struct area {
    unsigned long start, end;    /* адреси; під kptr_restrict обидві нулі */
    unsigned long span;          /* слід у байтах — окреме поле, не %pK */
    unsigned long pages;         /* кадрів під даними; 0 — кадрів немає */
    int kind, ioremap;
    char who[WHO];
};

struct owner { char who[WHO]; unsigned long span, mem, n; };

static struct area  A[MAXA];
static struct owner O[MAXO];
static size_t na, no;

/* «tg3_open+0x1c4/0x9f0» + «[tg3]» → «tg3_open [tg3]».
   Зміщення прибираємо навмисно: із ним кожна точка виклику стала б
   окремим власником і жоден рядок не набрав би ваги. */
static void make_key(char *dst, const char *sym, const char *mod)
{
    char base[WHO];
    size_t k = 0;

    if (!sym) sym = "(невідомо)";
    while (sym[k] && sym[k] != '+' && k + 1 < sizeof base) {
        base[k] = sym[k];
        k++;
    }
    base[k] = '\0';
    if (mod) snprintf(dst, WHO, "%s %s", base, mod);
    else     snprintf(dst, WHO, "%s", base);
}

static int is_flag(const char *t)
{
    static const char *f[] = { "vmalloc", "vmap", "user",
                               "vpages", "dma-coherent", NULL };
    int i;

    for (i = 0; f[i]; i++)
        if (!strcmp(t, f[i])) return 1;
    return 0;
}

static void take_line(char *ln)
{
    struct area a;
    char *t, *sym = NULL, *mod = NULL;
    int used = 0;

    memset(&a, 0, sizeof a);
    /* спільний початок усіх трьох форм рядка: «0x…-0x… <байтів>» */
    if (sscanf(ln, "0x%lx-0x%lx %lu%n", &a.start, &a.end, &a.span, &used) != 3)
        return;

    t = strtok(ln + used, " \t\n");
    if (t && !strcmp(t, "unpurged")) {            /* «unpurged vm_area» */
        a.kind = K_UNPURGED;
        snprintf(a.who, WHO, "(звільнене, ще не вичищене)");
    } else if (t && !strcmp(t, "vm_map_ram")) {   /* без викликача */
        a.kind = K_MAPRAM;
        snprintf(a.who, WHO, "(vm_map_ram)");
    } else {
        a.kind = K_AREA;
        for (; t; t = strtok(NULL, " \t\n")) {
            if      (!strncmp(t, "pages=", 6)) a.pages = strtoul(t + 6, NULL, 10);
            else if (strchr(t, '='))           continue;  /* phys=…, N0=… */
            else if (t[0] == '[')              mod = t;   /* [модуль] */
            else if (!strcmp(t, "ioremap"))    a.ioremap = 1;
            else if (is_flag(t))               continue;
            else if (!sym)                     sym = t;   /* перше незнайоме */
        }
        make_key(a.who, sym, mod);
    }
    if (na < MAXA) A[na++] = a;
}

static struct owner *owner_of(const char *who)
{
    size_t i;

    for (i = 0; i < no; i++)
        if (!strcmp(O[i].who, who)) return &O[i];
    if (no + 1 < MAXO) {
        snprintf(O[no].who, WHO, "%s", who);
        return &O[no++];
    }
    snprintf(O[MAXO - 1].who, WHO, "(решта)");    /* кошик на переповнення */
    return &O[MAXO - 1];
}

static int by_span(const void *x, const void *y)  /* власники — за спаданням */
{
    const struct owner *a = x, *b = y;
    return (a->span < b->span) - (a->span > b->span);
}

static int by_start(const void *x, const void *y) /* ділянки — за адресою */
{
    const struct area *a = x, *b = y;
    return (a->start > b->start) - (a->start < b->start);
}

/* Довжина області — з /proc/meminfo: у самому vmallocinfo кінця не видно. */
static unsigned long vmalloc_total(void)
{
    unsigned long kb = 0;
    char ln[256];
    FILE *f = fopen("/proc/meminfo", "r");

    if (!f) return 0;
    while (fgets(ln, sizeof ln, f))
        if (sscanf(ln, "VmallocTotal: %lu kB", &kb) == 1) break;
    fclose(f);
    return kb * 1024UL;
}

int main(int argc, char **argv)
{
    const char *path = argc > 1 ? argv[1] : "/proc/vmallocinfo";
    unsigned long span = 0, mem = 0, io = 0, unp = 0;
    unsigned long region, lo, hi, gap = 0, gap_at = 0, tail = 0;
    size_t i, masked = 0, foreign = 0;
    char ln[512];
    FILE *f = fopen(path, "r");

    if (!f) { perror(path); return 1; }
    while (fgets(ln, sizeof ln, f)) take_line(ln);
    fclose(f);
    if (!na) { fprintf(stderr, "%s: жодного рядка ділянки\n", path); return 1; }

    for (i = 0; i < na; i++) {
        struct owner *o = owner_of(A[i].who);
        unsigned long m = A[i].pages * 4096UL;

        o->span += A[i].span;  o->mem += m;  o->n++;
        span += A[i].span;     mem += m;
        if (A[i].ioremap)            io  += A[i].span;
        if (A[i].kind == K_UNPURGED) unp += A[i].span;
        if (A[i].start == 0)         masked++;
    }

    printf("%s: %zu ділянок, %zu різних викликачів\n\n", path, na, no);
    printf("   адресний слід    пам'ять під ним  ділянок  хто просив\n");
    qsort(O, no, sizeof *O, by_span);
    for (i = 0; i < no && i < TOPN; i++)
        printf("%12.1f МіБ %14.1f МіБ %8lu  %s\n",
               O[i].span / MIB, O[i].mem / MIB, O[i].n, O[i].who);

    printf("\nразом слід %.1f МіБ, під ним кадрів на %.1f МіБ\n"
           "  ioremap (регістри пристроїв, кадрів немає)  %.1f МіБ\n"
           "  звільнене, ще не вичищене                   %.1f МіБ\n",
           span / MIB, mem / MIB, io / MIB, unp / MIB);

    if (masked) {
        printf("\nадреси затерто (kptr_restrict) — проміжки не порахувати\n");
        return 0;
    }

    /* Проміжки — лише серед ділянок самої області. Модулі й інші діапазони
       живуть за терабайти звідси: відстань до них не дірка, а чужі адреси. */
    region = vmalloc_total();
    qsort(A, na, sizeof *A, by_start);
    lo = A[0].start;
    hi = A[0].end;
    for (i = 1; i < na; i++) {
        if (region && A[i].start - lo >= region) { foreign++; continue; }
        if (A[i].start > hi && A[i].start - hi > gap) {
            gap = A[i].start - hi;
            gap_at = hi;
        }
        if (A[i].end > hi) hi = A[i].end;
    }
    if (region && lo + region > hi) tail = lo + region - hi;

    printf("\nобласть за VmallocTotal: %.1f ГіБ\n"
           "поза нею (модулі та інші діапазони): %zu ділянок\n"
           "найбільша дірка між сусідами: %.1f МіБ, від 0x%lx\n"
           "вільний хвіст до кінця області: %.1f ГіБ\n",
           region / GIB, foreign, gap / MIB, gap_at, tail / GIB);
    return 0;
}
