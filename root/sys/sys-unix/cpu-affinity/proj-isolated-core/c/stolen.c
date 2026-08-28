/* stolen.c — лічильник украденого часу.
 * Тісний цикл читає монотонний годинник. Кожна різниця, більша за вартість
 * самого читання, означає, що ядро в цей час належало не нам.
 *
 *   gcc -O2 -Wall -o stolen stolen.c
 *   ./stolen <ядро> <секунд>
 */
#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <sys/mman.h>

#define BUCKETS 32                      /* лог₂-кошики: 1 нс … ≈2 с */

static inline uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
}

/* статична: у циклі не має бути ні malloc, ні звертання до нової сторінки */
static unsigned long long hist[BUCKETS];

int main(int argc, char **argv)
{
    int cpu       = (argc > 1) ? atoi(argv[1]) : 0;
    unsigned secs = (argc > 2) ? (unsigned)atoi(argv[2]) : 10;

    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof(set), &set) != 0) {
        fprintf(stderr, "sched_setaffinity(%d): %s\n", cpu, strerror(errno));
        return 1;
    }

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0)
        fprintf(stderr, "mlockall: %s — числа будуть брудніші\n", strerror(errno));

    /* розігрів: без нього найдовшою паузою щоразу виявляється власний старт */
    for (uint64_t warm = now_ns() + 50000000ull; now_ns() < warm; )
        ;

    uint64_t worst = 0;
    uint64_t deadline = now_ns() + (uint64_t)secs * 1000000000ull;
    uint64_t prev = now_ns();
    unsigned long long samples = 0;

    for (;;) {
        uint64_t t = now_ns();
        uint64_t d = t - prev;
        prev = t;

        int b = 0;                          /* кошик = позиція старшого біта */
        while (b < BUCKETS - 1 && (d >> b) != 0)
            b++;
        hist[b]++;
        samples++;

        if (d > worst)
            worst = d;
        if (t >= deadline)
            break;
    }

    /* медіанний кошик — типовий інтервал, тобто вартість самого приладу */
    unsigned long long acc = 0;
    int med = 0;
    for (int b = 0; b < BUCKETS; b++) {
        acc += hist[b];
        if (acc >= samples / 2) { med = b; break; }
    }

    printf("ядро %d (наприкінці %d), зразків %llu за %u с\n",
           cpu, sched_getcpu(), samples, secs);
    printf("типовий інтервал: %llu–%llu нс\n",
           med ? 1ull << (med - 1) : 0ull, 1ull << med);

    /* межі — теж степені двійки, інакше кошик не збігся б з порогом;
       вирівнювання — пробілами в самому рядку, бо %-8s рахує байти,
       а кирилична літера їх займає два */
    static const struct { const char *name; int from; } marks[] = {
        { "  1 мкс", 11 }, { "  8 мкс", 14 },
        { "128 мкс", 18 }, { "  1 мс ", 21 },
    };
    for (unsigned m = 0; m < sizeof(marks) / sizeof(marks[0]); m++) {
        unsigned long long over = 0;
        for (int b = marks[m].from; b < BUCKETS; b++)
            over += hist[b];
        printf("пауз від %s: %llu\n", marks[m].name, over);
    }
    printf("найдовша пауза: %.1f мкс\n", worst / 1000.0);

    puts("розподіл (нижня межа кошика):");
    for (int b = 0; b < BUCKETS; b++)
        if (hist[b])
            printf("  %12llu нс : %llu\n",
                   b ? 1ull << (b - 1) : 0ull, hist[b]);
    return 0;
}
