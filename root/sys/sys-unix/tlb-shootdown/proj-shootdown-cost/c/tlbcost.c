/* tlbcost.c — ціна одного розсилання скидань TLB, зміряна зсередини.
 * збірка:  cc -O2 -pthread -o tlbcost tlbcost.c
 * запуск:  ./tlbcost cores [пауза_нс]   — розгортка по ядрах-власниках
 *          ./tlbcost pages [пауза_нс]   — розгортка по сторінках у діапазоні
 */
#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>

#define PAGE        4096UL
#define HOLD_PAGES  1024    /* робоча множина власника: 4 МіБ — щоб повне
                               скидання справді коштувало йому прогріву */
#define WARMUP      3000
#define ITERS       20000
#define MAX_CPU     512

static uint64_t gap_ns = 50000;   /* пауза між пробами: не насичувати цілі */

static void die(const char *w) { perror(w); exit(1); }

static uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
}

static void spin(uint64_t ns)          /* саме крутитися, а не спати: сон
                                          вертає ядро холодним і з планувальником
                                          у сліді */
{
    uint64_t until = now_ns() + ns;
    while (now_ns() < until) { }
}

static void pin(int cpu)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof set, &set) != 0) die("sched_setaffinity");
}

/* по одному логічному процесору на фізичне ядро: у thread_siblings_list
   першим стоїть представник ядра, решта — його брати по гіперпотоку */
static int list_cores(int *out)
{
    int n = 0;
    for (int cpu = 0; cpu < MAX_CPU; cpu++) {
        char path[128], buf[256];
        snprintf(path, sizeof path,
                 "/sys/devices/system/cpu/cpu%d/topology/thread_siblings_list", cpu);
        FILE *f = fopen(path, "r");
        if (!f) continue;
        char *got = fgets(buf, sizeof buf, f);
        fclose(f);
        if (got && atoi(buf) == cpu) out[n++] = cpu;
    }
    return n;
}

/* рядок «TLB:» з /proc/interrupts — скільки розсилань ПРИЙНЯЛИ всі ядра разом */
static unsigned long long tlb_received(void)
{
    FILE *f = fopen("/proc/interrupts", "r");
    if (!f) return 0;
    char line[16384];
    unsigned long long sum = 0;
    while (fgets(line, sizeof line, f)) {
        char *p = line + strspn(line, " \t");
        if (strncmp(p, "TLB:", 4) != 0) continue;
        for (char *t = strtok(p + 4, " \t\n"); t; t = strtok(NULL, " \t\n")) {
            if (*t < '0' || *t > '9') break;    /* далі пішов словесний опис */
            sum += strtoull(t, NULL, 10);
        }
        break;
    }
    fclose(f);
    return sum;
}

static char *fresh_area(size_t pages)
{
    size_t len = pages * PAGE;
    char *a = mmap(NULL, len, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (a == MAP_FAILED) die("mmap");
    madvise(a, len, MADV_NOHUGEPAGE);   /* інакше прозорі великі сторінки
                                           зліплять тисячу записів у два */
    for (size_t off = 0; off < len; off += PAGE) a[off] = 1;   /* збої — тут */
    return a;
}

/* ── власники простору ──────────────────────────────────────────────────── */

struct holder {
    pthread_t        th;
    int              cpu;
    char            *area;
    _Atomic uint64_t rounds;
};

static _Atomic int stop_flag;

static void *holder_main(void *arg)
{
    struct holder *h = arg;
    pin(h->cpu);
    uint64_t r = 0;
    while (!atomic_load_explicit(&stop_flag, memory_order_relaxed)) {
        /* обхід власної робочої множини: тримає простір завантаженим на цьому
           ядрі й наповнює його TLB тисячею справжніх перекладів */
        for (size_t off = 0; off < HOLD_PAGES * PAGE; off += PAGE)
            h->area[off]++;
        atomic_store_explicit(&h->rounds, ++r, memory_order_relaxed);
    }
    return NULL;
}

static int grow_holders(struct holder *hs, int have, int want, const int *cores)
{
    while (have < want) {
        hs[have].cpu  = cores[have + 1];    /* cores[0] лишається ініціаторові */
        hs[have].area = fresh_area(HOLD_PAGES);
        if (pthread_create(&hs[have].th, NULL, holder_main, &hs[have]) != 0)
            die("pthread_create");
        have++;
    }
    return have;
}

/* ── проба: одне звуження прав на K сторінках ───────────────────────────── */

static char  *probe;
static size_t probe_len;

static uint64_t one_probe(void)
{
    uint64_t t0 = now_ns();
    if (mprotect(probe, probe_len, PROT_READ) != 0) die("mprotect ro");
    uint64_t t1 = now_ns();
    /* розширення прав назад: ядро одразу повертає біт запису в записи
       й нічого не розсилає — тож наступна проба знову матиме що стирати */
    if (mprotect(probe, probe_len, PROT_READ | PROT_WRITE) != 0) die("mprotect rw");
    return t1 - t0;
}

static int cmp_u64(const void *a, const void *b)
{
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

struct result { double p50, p99, mean, ipi, hold; };

static struct result measure(struct holder *hs, int nh)
{
    static uint64_t t[ITERS];
    struct result r;
    uint64_t rounds0 = 0, rounds1 = 0;

    for (int i = 0; i < WARMUP; i++) { one_probe(); spin(gap_ns); }

    unsigned long long ipi0 = tlb_received();      /* читання /proc — до вікна */
    for (int i = 0; i < nh; i++) rounds0 += atomic_load(&hs[i].rounds);
    uint64_t wall0 = now_ns();

    for (int i = 0; i < ITERS; i++) { t[i] = one_probe(); spin(gap_ns); }

    uint64_t wall1 = now_ns();
    for (int i = 0; i < nh; i++) rounds1 += atomic_load(&hs[i].rounds);
    unsigned long long ipi1 = tlb_received();

    double sum = 0;
    for (int i = 0; i < ITERS; i++) sum += (double)t[i];
    qsort(t, ITERS, sizeof t[0], cmp_u64);

    r.p50  = t[ITERS / 2]        / 1000.0;
    r.p99  = t[ITERS * 99 / 100] / 1000.0;
    r.mean = sum / ITERS / 1000.0;
    r.ipi  = (double)(ipi1 - ipi0) / ITERS;
    r.hold = nh ? (double)(rounds1 - rounds0) * 1e9 / (wall1 - wall0) / nh : 0.0;
    return r;
}

static double idle_rate(struct holder *hs, int nh)   /* вільний хід власників */
{
    uint64_t r0 = 0, r1 = 0;
    struct timespec nap = { 0, 200000000L };
    for (int i = 0; i < nh; i++) r0 += atomic_load(&hs[i].rounds);
    uint64_t w0 = now_ns();
    nanosleep(&nap, NULL);
    uint64_t w1 = now_ns();
    for (int i = 0; i < nh; i++) r1 += atomic_load(&hs[i].rounds);
    return (double)(r1 - r0) * 1e9 / (w1 - w0) / nh;
}

int main(int argc, char **argv)
{
    const char *sweep = argc > 1 ? argv[1] : "cores";
    static int cores[MAX_CPU];
    static struct holder hs[MAX_CPU];
    int ncore = list_cores(cores), nh = 0;

    if (argc > 2) gap_ns = strtoull(argv[2], NULL, 10);
    if (ncore < 2) { fputs("треба щонайменше два ядра\n", stderr); return 1; }
    pin(cores[0]);                   /* ініціатор сидить окремо від власників */

    if (strcmp(sweep, "cores") == 0) {
        probe_len = 8 * PAGE;        /* завідомо нижче порога в 33 сторінки */
        probe = fresh_area(8);
        puts("власників    p50    p99  серед.  IPI/оп  кіл/с власника");
        for (int want = 0; ; ) {
            nh = grow_holders(hs, nh, want, cores);
            struct result r = measure(hs, nh);
            printf("%9d %6.2f %6.2f %7.2f %7.2f %15.0f\n",
                   nh, r.p50, r.p99, r.mean, r.ipi, r.hold);
            if (want == ncore - 1) break;
            want = want ? want * 2 : 1;
            if (want > ncore - 1) want = ncore - 1;
        }
    } else {
        static const int ks[] = { 1, 4, 8, 16, 24, 32, 33, 34, 40, 48, 64, 0 };
        nh = grow_holders(hs, 0, ncore - 1 < 8 ? ncore - 1 : 8, cores);
        printf("власників: %d, вільний хід: %.0f кіл/с\n", nh, idle_rate(hs, nh));
        puts("сторінок    p50    p99  IPI/оп  кіл/с власника");
        for (int i = 0; ks[i]; i++) {
            if (probe) munmap(probe, probe_len);
            probe_len = (size_t)ks[i] * PAGE;
            probe = fresh_area((size_t)ks[i]);
            struct result r = measure(hs, nh);
            printf("%8d %6.2f %6.2f %7.2f %15.0f\n",
                   ks[i], r.p50, r.p99, r.ipi, r.hold);
        }
    }

    atomic_store(&stop_flag, 1);
    for (int i = 0; i < nh; i++) pthread_join(hs[i].th, NULL);
    return 0;
}
