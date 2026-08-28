/* slabwatch.c — дослід із кешами ядра
   зібрати:  cc -O2 -Wall -Wextra -o slabwatch slabwatch.c -lm            */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/stat.h>

#define MAXC 1024

struct cache {
    char name[48];
    unsigned long active_objs, num_objs;
    unsigned long objsize, objperslab, pagesperslab;
    unsigned long active_slabs, num_slabs;
    unsigned long bytes;   /* усе, що під цим кешем                       */
    unsigned long tail;    /* хвости слабів — це не вживеться ніколи      */
    unsigned long idle;    /* нарізані, але порожні слоти                 */
};

static struct cache C[MAXC];
static int NC;
static unsigned long PAGE;

static double mib(unsigned long b) { return b / 1048576.0; }
static unsigned long sub(unsigned long a, unsigned long b) { return a > b ? a - b : 0; }

static int read_slabinfo(void)
{
    FILE *f = fopen("/proc/slabinfo", "r");
    if (!f) {
        fprintf(stderr, "/proc/slabinfo: %s (файл читає лише root)\n", strerror(errno));
        return -1;
    }
    char ln[512];
    NC = 0;
    while (fgets(ln, sizeof ln, f) && NC < MAXC) {
        struct cache c;
        memset(&c, 0, sizeof c);
        int n = sscanf(ln, "%47s %lu %lu %lu %lu %lu : tunables %*u %*u %*u"
                           " : slabdata %lu %lu",
                       c.name, &c.active_objs, &c.num_objs, &c.objsize,
                       &c.objperslab, &c.pagesperslab,
                       &c.active_slabs, &c.num_slabs);
        if (n != 8 || !c.objsize || !c.objperslab || !c.pagesperslab)
            continue;                    /* шапка й рядок із назвами полів */
        unsigned long slab = c.pagesperslab * PAGE;
        unsigned long used = c.objperslab * c.objsize;
        c.bytes = c.num_slabs * slab;
        c.tail  = c.num_slabs * sub(slab, used);
        c.idle  = sub(c.num_objs, c.active_objs) * c.objsize;
        C[NC++] = c;
    }
    fclose(f);
    return NC;
}

static unsigned long meminfo_kb(const char *key)     /* значення в кілобайтах */
{
    FILE *f = fopen("/proc/meminfo", "r");
    if (!f) return 0;
    char ln[256];
    size_t kl = strlen(key);
    unsigned long v = 0;
    while (fgets(ln, sizeof ln, f))
        if (!strncmp(ln, key, kl) && ln[kl] == ':') {
            v = strtoul(ln + kl + 1, NULL, 10);
            break;
        }
    fclose(f);
    return v;
}

static const struct cache *find_cache(const char *name)
{
    for (int i = 0; i < NC; i++)
        if (!strcmp(C[i].name, name)) return &C[i];
    return NULL;
}

/* один знімок стану названого кеша з підписом */
static struct cache snapshot(const char *tag, const char *cname)
{
    struct cache z;
    memset(&z, 0, sizeof z);
    if (read_slabinfo() < 0) exit(1);
    const struct cache *c = find_cache(cname);
    if (!c) {
        printf("%s: кеша «%s» у slabinfo немає (злився з іншим?)\n", tag, cname);
        return z;
    }
    z = *c;
    printf("%s: %s %lu об'єктів, %lu слабів (%.1f МіБ)"
           " | SReclaimable %.0f МіБ, Slab %.0f МіБ\n",
           tag, cname, z.active_objs, z.num_slabs,
           mib(z.num_slabs * z.pagesperslab * PAGE),
           meminfo_kb("SReclaimable") / 1024.0, meminfo_kb("Slab") / 1024.0);
    return z;
}
