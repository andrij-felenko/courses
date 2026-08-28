/* mmapbench.c — той самий файл трьома шляхами. Разом із часом друкує
   сторінкові збої, бо саме вони пояснюють час.

   Вжиток: ./mmapbench [ключі] <режим> [файл]                            */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <setjmp.h>
#include <signal.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#ifndef MADV_POPULATE_READ
#define MADV_POPULATE_READ 22        /* Linux 5.14; хай збереться й на старих заголовках */
#endif

static size_t PAGE;
static volatile uint64_t sink;       /* щоб оптимізатор не викинув усе читання */

/* ── Вимір: час і лічильники збоїв беремо однією парою «до/після» ─────────── */

struct probe { struct timespec t; long minflt, majflt; };

static void probe_take(struct probe *p)
{
    struct rusage r;

    clock_gettime(CLOCK_MONOTONIC, &p->t);   /* годинник першим: getrusage коштує
                                                кількасот наносекунд, і хай вони
                                                краще лягають усередину проміжку */
    getrusage(RUSAGE_SELF, &r);
    p->minflt = r.ru_minflt;
    p->majflt = r.ru_majflt;
}

static double ms_between(struct timespec a, struct timespec b)
{
    /* Віднімаємо ЦІЛІ поля: tv_sec монотонного годинника — це мільйони секунд
       від старту системи, і наносекунди в такому double просто потонули б. */
    return (double)(b.tv_sec - a.tv_sec) * 1e3
         + (double)(b.tv_nsec - a.tv_nsec) / 1e6;
}

static void head(void)
{
    printf("  %-24s %9s %11s %11s\n", "етап", "мс", "minflt", "majflt");
}

static void row(const char *what, const struct probe *a, const struct probe *b)
{
    printf("  %-24s %9.1f %11ld %11ld\n", what, ms_between(a->t, b->t),
           b->minflt - a->minflt, b->majflt - a->majflt);
}

/* Сума 64-бітними словами. memcpy тут не копіювання, а спосіб прочитати слово
   без порушення правил доступу до пам'яті: з -O2 з нього виходить рівно одна
   інструкція завантаження. */
static uint64_t sum_words(const unsigned char *p, size_t n)
{
    uint64_t s = 0, w;
    size_t i = 0;

    for (; i + sizeof w <= n; i += sizeof w) {
        memcpy(&w, p + i, sizeof w);
        s += w;
    }
    for (; i < n; i++)
        s += p[i];
    return s;
}

/* ── Набір сторінок для розрідженого режиму ───────────────────────────────── */

/* xorshift64* — щоб набір сторінок і порядок звертань були ТІ САМІ в кожному
   режимі: інакше порівнюємо не шляхи до байта, а два різні маршрути. */
static uint64_t rng = 20260803;

static uint64_t rnd(void)
{
    rng ^= rng >> 12;
    rng ^= rng << 25;
    rng ^= rng >> 27;
    return rng * 2685821657736338717ULL;
}

/* nsample РІЗНИХ сторінок, рівномірно розкиданих по файлу, у випадковому порядку. */
static size_t *make_sample(size_t npages, size_t nsample)
{
    size_t *s = malloc(nsample * sizeof *s), stride = npages / nsample, i;

    if (!s || stride == 0) {
        fprintf(stderr, "замалий файл для набору в %zu сторінок\n", nsample);
        exit(1);
    }
    for (i = 0; i < nsample; i++)
        s[i] = i * stride + rnd() % stride;
    for (i = nsample - 1; i > 0; i--) {          /* тасування Фішера—Йетса */
        size_t j = rnd() % (i + 1), t = s[i];
        s[i] = s[j];
        s[j] = t;
    }
    return s;
}

/* Викинути сторінки ЦЬОГО файлу з кешу: чесніше й безпечніше за drop_caches —
   не чіпає решту системи й не потребує прав. На сторінки, які хтось тримає
   відображеними, не подіє, тож кличемо ДО mmap. */
static void chill(int fd)
{
    int rc = posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);

    if (rc)
        fprintf(stderr, "увага: fadvise(DONTNEED) → %s\n", strerror(rc));
}

/* ── Режим 1: read() наскрізь ─────────────────────────────────────────────── */

static void seq_read(int fd, size_t size, size_t bufsz, int cold)
{
    unsigned char *buf = malloc(bufsz);
    struct probe a, b;
    uint64_t s = 0;

    if (!buf) { perror("malloc"); exit(1); }
    memset(buf, 0, bufsz);              /* прогрів буфера: його власні збої — не наша тема */
    if (cold)
        chill(fd);
    if (lseek(fd, 0, SEEK_SET) < 0) { perror("lseek"); exit(1); }

    head();
    probe_take(&a);
    for (;;) {
        ssize_t n = read(fd, buf, bufsz);
        if (n < 0) {
            if (errno == EINTR) continue;   /* сигнал міг урвати виклик */
            perror("read");
            exit(1);
        }
        if (n == 0)
            break;
        s += sum_words(buf, (size_t)n);
    }
    probe_take(&b);
    sink = s;

    row("read + сума", &a, &b);
    printf("  %-24s %9.1f МБ/с\n", "пропускна здатність",
           (double)size / 1e6 / (ms_between(a.t, b.t) / 1e3));
    free(buf);
}

/* ── Режим 2: mmap наскрізь ───────────────────────────────────────────────── */

static void seq_mmap(int fd, size_t size, int populate, int advice, int cold)
{
    struct probe a, b, c, d;
    unsigned char *p;
    long faults;

    if (cold)
        chill(fd);

    head();
    probe_take(&a);
    p = mmap(NULL, size, PROT_READ,
             MAP_PRIVATE | (populate ? MAP_POPULATE : 0), fd, 0);
    if (p == MAP_FAILED) { perror("mmap"); exit(1); }
    if (advice && madvise(p, size, advice))
        fprintf(stderr, "увага: madvise → %s\n", strerror(errno));
    probe_take(&b);

    sink = sum_words(p, size);
    probe_take(&c);

    if (munmap(p, size))
        perror("munmap");
    probe_take(&d);

    row("mmap + підготовка", &a, &b);
    row("прохід і сума", &b, &c);
    row("munmap", &c, &d);
    printf("  %-24s %9.1f\n", "разом", ms_between(a.t, d.t));

    faults = (c.minflt - a.minflt) + (c.majflt - a.majflt);
    if (faults > 0)
        printf("  %-24s %9.2f\n", "сторінок на один збій",
               (double)(size / PAGE) / (double)faults);
}

/* ── Режим 3: розріджений доступ, той самий набір сторінок двома шляхами ───── */

static void rand_mode(int fd, size_t size, int use_mmap, size_t nsample,
                      size_t naccess, size_t rbytes, int cold)
{
    size_t *sample = make_sample(size / PAGE, nsample), k;
    unsigned char *buf = NULL, *p = NULL;
    struct probe a, b, c, d, acc0, acc1;
    uint64_t s = 0, w;

    if (rbytes > PAGE)
        rbytes = PAGE;
    if (cold)
        chill(fd);
    head();

    if (use_mmap) {
        probe_take(&a);
        p = mmap(NULL, size, PROT_READ, MAP_PRIVATE, fd, 0);
        if (p == MAP_FAILED) { perror("mmap"); exit(1); }
        probe_take(&b);
        for (k = 0; k < naccess; k++) {
            memcpy(&w, p + sample[rnd() % nsample] * PAGE + 64, sizeof w);
            s += w;
        }
        probe_take(&c);
        if (munmap(p, size))
            perror("munmap");
        probe_take(&d);
        row("mmap", &a, &b);
        row("звертання", &b, &c);
        row("munmap", &c, &d);
        acc0 = b; acc1 = c;
    } else {
        buf = malloc(PAGE);
        if (!buf) { perror("malloc"); exit(1); }
        memset(buf, 0, PAGE);
        probe_take(&a);
        for (k = 0; k < naccess; k++) {
            off_t off = (off_t)sample[rnd() % nsample] * (off_t)PAGE + 64;
            if (pread(fd, buf, rbytes, off) < (ssize_t)sizeof w) {
                perror("pread");
                exit(1);
            }
            memcpy(&w, buf, sizeof w);
            s += w;
        }
        probe_take(&b);
        row("pread", &a, &b);
        acc0 = a; acc1 = b;
    }
    sink = s;
    printf("  %-24s %9.3f мкс\n", "на одне звертання",
           ms_between(acc0.t, acc1.t) * 1e3 / (double)naccess);
    free(buf);
    free(sample);
}

/* ── Режим 4: файл обрізали під ногами ────────────────────────────────────── */

static sigjmp_buf bus_jump;
static void *volatile bus_addr;

static void on_sigbus(int sig, siginfo_t *si, void *uc)
{
    (void)sig; (void)uc;
    bus_addr = si->si_addr;        /* адреса, на якій усе спинилося */
    siglongjmp(bus_jump, 1);       /* повертатися в перервану інструкцію нікуди */
}

static void sigbus_demo(void)
{
    struct sigaction sa;
    volatile unsigned char *v;     /* volatile: інакше компілятор ПЕРЕВИКОРИСТАЄ
                                      значення, прочитане перед обрізанням,
                                      і другого звертання просто не буде */
    unsigned char *p;
    int fd = open("./mmapbench.tmp", O_RDWR | O_CREAT | O_TRUNC, 0600);

    if (fd < 0) { perror("open"); exit(1); }
    unlink("./mmapbench.tmp");                   /* ім'я вже не потрібне, inode живий */
    if (ftruncate(fd, (off_t)PAGE * 4)) { perror("ftruncate"); exit(1); }

    p = mmap(NULL, PAGE * 4, PROT_READ, MAP_PRIVATE, fd, 0);
    if (p == MAP_FAILED) { perror("mmap"); exit(1); }
    v = p;

    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_sigbus;
    sa.sa_flags = SA_SIGINFO;                    /* без цього не буде si_addr */
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGBUS, &sa, NULL)) { perror("sigaction"); exit(1); }

    printf("  файл на 4 сторінки, відображення на 4 сторінки\n");
    printf("  сторінка 3, байт 0 = %u\n", (unsigned)v[PAGE * 3]);

    if (ftruncate(fd, (off_t)PAGE)) { perror("ftruncate"); exit(1); }
    printf("  файл обрізано до 1 сторінки; відображення лишилось на 4\n");

    if (sigsetjmp(bus_jump, 1) == 0) {           /* 1 — відновити й маску сигналів */
        printf("  сторінка 3, байт 0 = %u\n", (unsigned)v[PAGE * 3]);
        printf("  збою не сталося — несподівано\n");
    } else {
        printf("  SIGBUS на адресі %p — сторінка %ld відображення\n",
               (void *)bus_addr,
               (long)(((unsigned char *)bus_addr - p) / (ptrdiff_t)PAGE));
    }

    munmap(p, PAGE * 4);
    close(fd);
}

/* ── Розбір рядка запуску ─────────────────────────────────────────────────── */

static void usage(void)
{
    fprintf(stderr,
        "вжиток: mmapbench [ключі] <режим> [файл]\n"
        "режими: seq-read | seq-mmap | rand-pread | rand-mmap | sigbus\n"
        "  -n N  сторінок у розрідженому наборі  (типово 8192)\n"
        "  -k N  скільки зробити звертань        (типово 131072)\n"
        "  -b N  буфер read(), КіБ               (типово 1024)\n"
        "  -B N  байтів на одне pread()          (типово 8)\n"
        "  -s N  зерно генератора\n"
        "  -p    MAP_POPULATE\n"
        "  -w    madvise(MADV_WILLNEED)\n"
        "  -P    madvise(MADV_POPULATE_READ)     (Linux 5.14+)\n"
        "  -c    викинути сторінки файлу з кешу перед виміром\n");
    exit(2);
}

int main(int argc, char **argv)
{
    size_t nsample = 8192, naccess = 131072, bufkib = 1024, rbytes = 8;
    int populate = 0, advice = 0, cold = 0, opt;
    const char *mode, *path;
    struct stat st;
    int fd;

    PAGE = (size_t)sysconf(_SC_PAGESIZE);

    while ((opt = getopt(argc, argv, "n:k:b:B:s:pwPc")) != -1)
        switch (opt) {
        case 'n': nsample = strtoul(optarg, NULL, 10); break;
        case 'k': naccess = strtoul(optarg, NULL, 10); break;
        case 'b': bufkib  = strtoul(optarg, NULL, 10); break;
        case 'B': rbytes  = strtoul(optarg, NULL, 10); break;
        case 's': rng     = strtoull(optarg, NULL, 10); break;
        case 'p': populate = 1; break;
        case 'w': advice = MADV_WILLNEED; break;
        case 'P': advice = MADV_POPULATE_READ; break;
        case 'c': cold = 1; break;
        default: usage();
        }
    if (rng == 0) rng = 1;                       /* нуль зупинив би xorshift */
    if (rbytes < sizeof(uint64_t)) rbytes = sizeof(uint64_t);
    if (optind >= argc) usage();
    mode = argv[optind++];

    if (!strcmp(mode, "sigbus")) { sigbus_demo(); return 0; }

    if (optind >= argc) usage();
    path = argv[optind];
    fd = open(path, O_RDONLY);
    if (fd < 0) { perror(path); return 1; }
    if (fstat(fd, &st) || !S_ISREG(st.st_mode) || st.st_size <= 0) {
        fprintf(stderr, "%s: потрібен звичайний непорожній файл\n", path);
        return 1;
    }
    printf("файл %s: %.2f ГіБ, сторінок %zu по %zu Б\n", path,
           (double)st.st_size / (1024.0 * 1024 * 1024),
           (size_t)st.st_size / PAGE, PAGE);

    if (!strcmp(mode, "seq-read"))
        seq_read(fd, (size_t)st.st_size, bufkib << 10, cold);
    else if (!strcmp(mode, "seq-mmap"))
        seq_mmap(fd, (size_t)st.st_size, populate, advice, cold);
    else if (!strcmp(mode, "rand-pread"))
        rand_mode(fd, (size_t)st.st_size, 0, nsample, naccess, rbytes, cold);
    else if (!strcmp(mode, "rand-mmap"))
        rand_mode(fd, (size_t)st.st_size, 1, nsample, naccess, rbytes, cold);
    else
        usage();

    close(fd);
    return 0;
}
