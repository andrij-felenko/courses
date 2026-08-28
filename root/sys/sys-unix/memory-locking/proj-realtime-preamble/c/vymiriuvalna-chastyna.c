#include <stdint.h>
#include <time.h>
#include <fcntl.h>

static inline uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t) ts.tv_sec * 1000000000ull + ts.tv_nsec;
}

static volatile unsigned char sink;

static void probe(const unsigned char *area, size_t bytes, unsigned long hist[64])
{
    size_t page = (size_t) sysconf(_SC_PAGESIZE);
    for (size_t off = 0; off < bytes; off += page) {
        uint64_t t0 = now_ns();
        sink = area[off];
        uint64_t dt = now_ns() - t0;
        unsigned k = 0;
        while (dt >>= 1) k++;
        hist[k]++;
    }
}

static void report(const char *tag, const unsigned long hist[64])
{
    int hi = 63;
    while (hi > 0 && hist[hi] == 0) hi--;
    printf("%s — найгірше звертання у смузі %llu нс\n", tag, 1ull << hi);
    for (int k = 0; k <= hi; k++)
        if (hist[k])
            printf("  %10llu нс  %lu\n", 1ull << k, hist[k]);
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "вжиток: %s <файл> [--locked]\n", argv[0]); return 2; }
    int locked = (argc > 2 && strcmp(argv[2], "--locked") == 0);
    size_t bytes = 256u << 20;

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) die("open");
    unsigned char *area = mmap(NULL, bytes, PROT_READ, MAP_PRIVATE, fd, 0);
    if (area == MAP_FAILED) die("mmap");

    if (locked)
        preamble(64u << 20);        /* mlockall накриє і щойно відображений файл */

    static unsigned long hist[64];
    probe(area, bytes, hist);       /* холостий прохід: сторінки мають бути населені */
    memset(hist, 0, sizeof hist);
    probe(area, bytes, hist);       /* власне замір */
    report(locked ? "прибито" : "як є", hist);
    return 0;
}
