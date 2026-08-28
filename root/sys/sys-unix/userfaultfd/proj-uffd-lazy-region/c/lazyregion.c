/* lazyregion.c — ділянка анонімної пам'яті, вміст якої програма породжує
   сама, у мить першого дотику до сторінки.

   Вжиток: ./lazyregion [сторінок у пакеті]                                 */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <linux/userfaultfd.h>
#include <sys/eventfd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/syscall.h>

#ifndef UFFD_USER_MODE_ONLY          /* заголовки старші за ядро 5.11 */
#define UFFD_USER_MODE_ONLY 1
#endif

#define die(what)  do { perror(what); exit(1); } while (0)

#define REGION_PAGES  65536ul        /* 256 МіБ при сторінці 4 КіБ         */
#define SWEEP_PAGES    4096ul        /* нижня частина — суцільний прохід   */
#define TOUCHES          200ul       /* розкиданих дотиків у верхній       */
#define STRIDE           307ul       /* крок — більший за типовий пакет    */

static size_t         page_size;
static unsigned char *region;
static size_t         region_len;
static unsigned long  batch_pages = 16;
static int            uffd   = -1;
static int            stopfd = -1;

static _Atomic long   n_msgs, n_placed, n_exist, ns_produce, ns_copy;
static volatile unsigned char sink;      /* щоб читання не викинув оптимізатор */

static int64_t now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (int64_t)t.tv_sec * 1000000000 + t.tv_nsec;
}

/* Вміст сторінки — детермінована функція її номера: те саме число завжди дає
   ті самі байти. У справжній програмі тут був би запит у мережу або
   розтиснення образу; для механізму це байдуже. */
static void produce(unsigned long index, unsigned char *dst)
{
    uint64_t x = index * 0x9E3779B97F4A7C15ull + 0x243F6A8885A308D3ull;
    for (size_t off = 0; off < page_size; off += 8) {
        uint64_t z = (x += 0x9E3779B97F4A7C15ull);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
        z ^= z >> 31;
        memcpy(dst + off, &z, 8);
    }
}

/* Обслужити один збій. buf лежить ПОЗА ділянкою: ядро читає його як звичайну
   пам'ять простору користувача. */
static void serve(unsigned long addr, unsigned char *buf)
{
    /* Адреса збою не зобов'язана бути початком сторінки — вирівнюємо самі. */
    unsigned long start = addr & ~(unsigned long)(page_size - 1);
    unsigned long index = (start - (unsigned long)region) / page_size;

    unsigned long count = batch_pages;
    if (index + count > REGION_PAGES)         /* не вилізти за ділянку */
        count = REGION_PAGES - index;

    int64_t t0 = now_ns();
    for (unsigned long k = 0; k < count; k++)
        produce(index + k, buf + k * page_size);
    int64_t t1 = now_ns();

    size_t want = (size_t)count * page_size, done = 0;
    unsigned long skipped = 0;

    while (done < want) {
        struct uffdio_copy c = {
            .dst  = start + done,
            .src  = (unsigned long)(buf + done),
            .len  = want - done,
            .mode = 0,
        };
        if (ioctl(uffd, UFFDIO_COPY, &c) == 0)
            break;                            /* усе покладено й розбуджено */
        if (errno == EAGAIN && c.copy > 0) {  /* лягла частина — доробляємо */
            done += (size_t)c.copy;
            continue;
        }
        if (errno == EEXIST) {                /* цю сторінку вже хтось поклав */
            done += page_size;
            skipped++;
            continue;
        }
        die("UFFDIO_COPY");
    }
    int64_t t2 = now_ns();

    n_placed   += (long)(count - skipped);
    n_exist    += (long)skipped;
    ns_produce += t1 - t0;
    ns_copy    += t2 - t1;
}

static void *watcher(void *arg)
{
    (void)arg;

    unsigned char *buf = malloc(batch_pages * page_size);
    if (!buf) die("malloc");

    struct pollfd pfd[2] = {
        { .fd = uffd,   .events = POLLIN, .revents = 0 },
        { .fd = stopfd, .events = POLLIN, .revents = 0 },
    };

    for (;;) {
        if (poll(pfd, 2, -1) < 0) {
            if (errno == EINTR) continue;
            die("poll");
        }
        if (pfd[1].revents & POLLIN)          /* «час додому» */
            break;
        if (pfd[0].revents & POLLERR) {       /* немає O_NONBLOCK або UFFDIO_API */
            fprintf(stderr, "uffd не придатний до poll\n");
            exit(1);
        }
        if (!(pfd[0].revents & POLLIN))
            continue;

        struct uffd_msg msg[16];              /* за один read — кілька подій */
        ssize_t got = read(uffd, msg, sizeof msg);
        if (got < 0) {
            if (errno == EAGAIN || errno == EINTR) continue;
            die("read(uffd)");
        }
        for (size_t i = 0; i < (size_t)got / sizeof msg[0]; i++) {
            if (msg[i].event != UFFD_EVENT_PAGEFAULT)
                continue;                     /* fork/remap/unmap ми не замовляли */
            n_msgs++;
            serve((unsigned long)msg[i].arg.pagefault.address, buf);
        }
    }
    free(buf);
    return NULL;
}

static int open_uffd(void)
{
    int fd = (int)syscall(SYS_userfaultfd,
                          O_CLOEXEC | O_NONBLOCK | UFFD_USER_MODE_ONLY);
    if (fd >= 0 || errno != EINVAL)
        return fd;
    return (int)syscall(SYS_userfaultfd, O_CLOEXEC | O_NONBLOCK);
}

static long rss_kib(void)
{
    FILE *f = fopen("/proc/self/status", "r");
    char line[256];
    long kb = -1;
    if (!f) return -1;
    while (fgets(line, sizeof line, f))
        if (sscanf(line, "VmRSS: %ld kB", &kb) == 1) break;
    fclose(f);
    return kb;
}

int main(int argc, char **argv)
{
    if (argc > 1) {
        batch_pages = strtoul(argv[1], NULL, 10);
        if (batch_pages < 1 || batch_pages > 512) {
            fprintf(stderr, "пакет — від 1 до 512 сторінок\n");
            return 1;
        }
    }
    page_size  = (size_t)sysconf(_SC_PAGESIZE);
    region_len = REGION_PAGES * page_size;

    uffd = open_uffd();
    if (uffd < 0) {
        int e = errno;
        fprintf(stderr, "userfaultfd: %s\n", strerror(e));
        if (e == EPERM)
            fprintf(stderr, "потрібен доступ до /dev/userfaultfd, CAP_SYS_PTRACE "
                            "або vm.unprivileged_userfaultfd = 1\n");
        return 1;
    }

    struct uffdio_api api = { .api = UFFD_API, .features = 0 };
    if (ioctl(uffd, UFFDIO_API, &api) < 0) die("UFFDIO_API");

    region = mmap(NULL, region_len, PROT_READ | PROT_WRITE,
                  MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (region == MAP_FAILED) die("mmap");

    struct uffdio_register reg = {
        .range = { .start = (unsigned long)region, .len = region_len },
        .mode  = UFFDIO_REGISTER_MODE_MISSING,
    };
    if (ioctl(uffd, UFFDIO_REGISTER, &reg) < 0) die("UFFDIO_REGISTER");
    if (!(reg.ioctls & (1ull << _UFFDIO_COPY))) {
        fprintf(stderr, "ядро не дає UFFDIO_COPY на цій ділянці\n");
        return 1;
    }

    stopfd = eventfd(0, EFD_CLOEXEC);
    if (stopfd < 0) die("eventfd");

    pthread_t tid;
    int rc = pthread_create(&tid, NULL, watcher, NULL);
    if (rc) { errno = rc; die("pthread_create"); }

    /* Дослід 1: розкидані дотики — кожен потрапляє у власний збій. */
    long m0 = n_msgs;
    int64_t t0 = now_ns();
    for (unsigned long i = 0; i < TOUCHES; i++)
        sink = region[(SWEEP_PAGES + i * STRIDE) * page_size];
    int64_t scattered_ns = now_ns() - t0;
    long scattered_msgs = n_msgs - m0;

    /* Дослід 2: суцільний прохід — пакет закриває збої наперед. */
    m0 = n_msgs;
    t0 = now_ns();
    for (unsigned long p = 0; p < SWEEP_PAGES; p++)
        sink = region[p * page_size];
    int64_t sweep_ns = now_ns() - t0;
    long sweep_msgs = n_msgs - m0;

    /* Перевірка: у ділянці справді наш вміст, а не тиша. */
    unsigned char *expect = malloc(page_size);
    if (!expect) die("malloc");
    for (unsigned long i = 0; i < TOUCHES; i += 8) {
        unsigned long index = SWEEP_PAGES + i * STRIDE;
        produce(index, expect);
        if (memcmp(region + index * page_size, expect, page_size) != 0) {
            fprintf(stderr, "сторінка %lu прийшла не та\n", index);
            return 1;
        }
    }
    free(expect);

    /* Завершення. Порядок єдино можливий: спершу впевнитися, що ділянки
       більше ніхто не торкнеться, тоді спинити наглядача, аж тоді знімати
       реєстрацію. */
    uint64_t one = 1;
    if (write(stopfd, &one, sizeof one) != (ssize_t)sizeof one)
        die("write(stopfd)");
    pthread_join(tid, NULL);

    struct uffdio_range range = {
        .start = (unsigned long)region, .len = region_len
    };
    if (ioctl(uffd, UFFDIO_UNREGISTER, &range) < 0) die("UFFDIO_UNREGISTER");

    close(uffd);
    close(stopfd);

    long total = n_msgs;
    double round_us = (scattered_ns + sweep_ns) / 1000.0 / (double)total;

    printf("ділянка           : %lu МіБ, %lu сторінок по %zu Б\n",
           (unsigned long)(region_len >> 20), REGION_PAGES, page_size);
    printf("пакет             : %lu сторінок\n\n", batch_pages);
    printf("розкидані дотики  : %lu → %ld збоїв, %.2f мс\n",
           TOUCHES, scattered_msgs, scattered_ns / 1e6);
    printf("суцільний прохід  : %lu сторінок → %ld збоїв, %.2f мс\n",
           SWEEP_PAGES, sweep_msgs, sweep_ns / 1e6);
    printf("покладено         : %ld сторінок, уже було %ld\n\n",
           (long)n_placed, (long)n_exist);
    printf("на один збій      : %.1f мкс\n", round_us);
    printf("  вироблення      : %.1f мкс\n", (double)ns_produce / 1000.0 / total);
    printf("  UFFDIO_COPY     : %.1f мкс\n", (double)ns_copy / 1000.0 / total);
    printf("  решта           : %.1f мкс\n",
           round_us - ((double)ns_produce + ns_copy) / 1000.0 / total);
    printf("VmRSS             : %ld КіБ\n", rss_kib());

    munmap(region, region_len);
    return 0;
}
