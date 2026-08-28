/* dcopy.c — копіювання файлу прямим вводом-виводом із заданою глибиною черги.
   Ключ -B вимикає O_DIRECT: буферизований шлях тим самим двигуном.

   вжиток: ./dcopy [-d глибина] [-b блок,КіБ] [-B] джерело ціль            */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <liburing.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define MAXQD 256

enum { OP_READ = 0, OP_WRITE = 1 };

struct slot {
    unsigned char *buf;
    off_t  off;              /* зміщення порції у файлі                    */
    size_t len;              /* довжина порції, вже округлена до блоку     */
    size_t done;             /* скільки байтів порції вже перенесено       */
};

static size_t up(size_t v, size_t a) { return (v + a - 1) / a * a; }

static double now(void)
{
    struct timespec t;

    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

/* ── Вирівнювання: питаємо ядро (див. вище) ────────────────────────────────── */

struct align { size_t mem, off; };

static struct align dio_align(int fd)
{
    struct align a = { 4096, 4096 };
    struct statx stx;

    if (statx(fd, "", AT_EMPTY_PATH, STATX_DIOALIGN, &stx) == 0
        && (stx.stx_mask & STATX_DIOALIGN) && stx.stx_dio_mem_align) {
        a.mem = stx.stx_dio_mem_align;
        a.off = stx.stx_dio_offset_align;
    }
    return a;
}

/* ── Скільки байтів файлу зараз лежить у кеші сторінок ─────────────────────── */
/* mmap сам нічого не читає, а mincore каже, які сторінки відображення вже
   резидентні. Ядро віддає правду лише тому, хто МІГ БИ відкрити цей файл на
   запис; решті воно заповнює вектор одиницями — латка бічного каналу з Linux
   5.0. Свої файли міряти можна, чужі — ні.                                  */

static long long cached(const char *path)
{
    size_t page = (size_t)sysconf(_SC_PAGESIZE), n, i;
    long long sum = 0;
    unsigned char *vec;
    struct stat st;
    void *m;
    int fd = open(path, O_RDONLY);

    if (fd < 0) return -1;
    if (fstat(fd, &st) || st.st_size <= 0) { close(fd); return -1; }
    m = mmap(NULL, (size_t)st.st_size, PROT_READ, MAP_SHARED, fd, 0);
    close(fd);                       /* відображення само тримає файл живим */
    if (m == MAP_FAILED) return -1;

    n = ((size_t)st.st_size + page - 1) / page;
    vec = malloc(n);
    if (vec && mincore(m, (size_t)st.st_size, vec) == 0)
        for (i = 0; i < n; i++)
            sum += (vec[i] & 1) ? (long long)page : 0;
    else
        sum = -1;
    free(vec);
    munmap(m, (size_t)st.st_size);
    return sum;
}

/* ── Двигун: qd порцій у польоті, кожна проходить читання → запис ──────────── */

static int pump(struct io_uring *ring, int in, int out, off_t size,
                size_t blk, size_t offal, struct slot *s, int qd)
{
    int freelist[MAXQD], nfree = 0, inflight = 0, i;
    struct io_uring_sqe *sqe;
    struct io_uring_cqe *cqe;
    off_t next = 0;

    for (i = qd - 1; i >= 0; i--)
        freelist[nfree++] = i;

    while (next < size || inflight) {
        while (nfree && next < size) {          /* набиваємо чергу читаннями */
            size_t want;

            i = freelist[--nfree];
            want = (size - next) < (off_t)blk ? (size_t)(size - next) : blk;
            s[i].off  = next;
            s[i].len  = up(want, offal);        /* хвіст округлюємо вгору    */
            s[i].done = 0;
            if (s[i].len > want)                /* і зануляємо доповнення    */
                memset(s[i].buf + want, 0, s[i].len - want);

            sqe = io_uring_get_sqe(ring);       /* кільце вдвічі більше за qd,
                                                   тож NULL тут неможливий  */
            io_uring_prep_read(sqe, in, s[i].buf, (unsigned)s[i].len, s[i].off);
            io_uring_sqe_set_data(sqe, (void *)(uintptr_t)((unsigned)i << 1 | OP_READ));
            next += (off_t)want;
            inflight++;
        }
        if (io_uring_submit(ring) < 0) { perror("io_uring_submit"); return -1; }

        if (io_uring_wait_cqe(ring, &cqe) < 0) { perror("io_uring_wait_cqe"); return -1; }
        do {                                    /* чекаємо на одне, забираємо всі готові */
            uintptr_t d = (uintptr_t)io_uring_cqe_get_data(cqe);
            int op = (int)(d & 1), res = cqe->res;

            i = (int)(d >> 1);
            io_uring_cqe_seen(ring, cqe);
            if (res < 0) {
                errno = -res;                   /* io_uring кладе −errno у res */
                perror(op == OP_READ ? "read" : "write");
                return -1;
            }
            s[i].done += (size_t)res;

            /* Коротка відповідь буває двічі. На кінці файлу читання поверне
               менше, ніж просили, — це не помилка, решту буфера ми занулили
               заздалегідь. Посеред файлу вона теж можлива; тоді доподаємо
               залишок тим самим оператором. Результат прямого обміну кратний
               блоку, тож зміщення лишається законним; коли ядро вимагає для
               пам'яті більшого вирівнювання, ніж для зміщень, залишок треба
               спершу пересунути на початок буфера.                          */
            if (op == OP_READ && s[i].off + (off_t)s[i].done >= size)
                s[i].done = s[i].len;

            if (s[i].done < s[i].len) {
                size_t rest = s[i].len - s[i].done;
                off_t  at   = s[i].off + (off_t)s[i].done;

                sqe = io_uring_get_sqe(ring);
                if (op == OP_READ)
                    io_uring_prep_read(sqe, in, s[i].buf + s[i].done, (unsigned)rest, at);
                else
                    io_uring_prep_write(sqe, out, s[i].buf + s[i].done, (unsigned)rest, at);
                io_uring_sqe_set_data(sqe, (void *)(uintptr_t)((unsigned)i << 1 | (unsigned)op));
            } else if (op == OP_READ) {         /* прочитали — пишемо тим самим буфером */
                s[i].done = 0;
                sqe = io_uring_get_sqe(ring);
                io_uring_prep_write(sqe, out, s[i].buf, (unsigned)s[i].len, s[i].off);
                io_uring_sqe_set_data(sqe, (void *)(uintptr_t)((unsigned)i << 1 | OP_WRITE));
            } else {                            /* порція закрита — слот вільний */
                freelist[nfree++] = i;
                inflight--;
            }
        } while (io_uring_peek_cqe(ring, &cqe) == 0);
    }
    return 0;
}

int main(int argc, char **argv)
{
    size_t blk = 1u << 20, bufal;
    int qd = 32, direct = 1, opt, in, out, i;
    struct io_uring ring;
    struct slot s[MAXQD];
    struct align a, b;
    struct stat st;
    double t0, t1;
    off_t size;

    while ((opt = getopt(argc, argv, "d:b:B")) != -1)
        switch (opt) {
        case 'd': qd = atoi(optarg); break;
        case 'b': blk = (size_t)atoi(optarg) << 10; break;
        case 'B': direct = 0; break;
        default:  return 2;
        }
    if (qd < 1 || qd > MAXQD || optind + 2 > argc) {
        fprintf(stderr, "вжиток: dcopy [-d глибина] [-b блок,КіБ] [-B] джерело ціль\n");
        return 2;
    }

    /* Саме тут ловиться EINVAL від файлових систем, які прямого шляху не мають. */
    in = open(argv[optind], O_RDONLY | (direct ? O_DIRECT : 0));
    if (in < 0) { perror(argv[optind]); return 1; }
    out = open(argv[optind + 1], O_WRONLY | O_CREAT | O_TRUNC | (direct ? O_DIRECT : 0), 0644);
    if (out < 0) { perror(argv[optind + 1]); return 1; }
    if (fstat(in, &st)) { perror("fstat"); return 1; }
    size = st.st_size;

    a = dio_align(in);
    b = dio_align(out);
    if (b.mem > a.mem) a.mem = b.mem;
    if (b.off > a.off) a.off = b.off;
    blk = up(blk, a.off);
    bufal = a.mem > a.off ? a.mem : a.off;

    /* Місце під ціль беремо одним рухом: інакше кожен запис, що продовжує
       файл, тягне за собою зміну розміру, тобто роботу з метаданими.       */
    if (fallocate(out, 0, 0, size) && errno != EOPNOTSUPP)
        perror("fallocate (не критично)");

    for (i = 0; i < qd; i++)
        if (posix_memalign((void **)&s[i].buf, bufal, blk)) {
            fprintf(stderr, "posix_memalign: немає пам'яті\n");
            return 1;
        }
    if (io_uring_queue_init((unsigned)qd * 2, &ring, 0) < 0) {
        perror("io_uring_queue_init");
        return 1;
    }

    printf("вирівнювання: пам'ять %zu, зміщення %zu; блок %zu КіБ; глибина %d; %s\n",
           a.mem, a.off, blk >> 10, qd, direct ? "O_DIRECT" : "буферизовано");

    t0 = now();
    if (pump(&ring, in, out, size, blk, a.off, s, qd))
        return 1;
    if (ftruncate(out, size)) perror("ftruncate");   /* зрізаємо доповнення хвоста */
    if (fdatasync(out))       perror("fdatasync");   /* прапорець довговічності не дає */
    t1 = now();

    printf("%.2f с, %.0f МБ/с\n", t1 - t0, (double)size / 1e6 / (t1 - t0));
    printf("у кеші після: джерело %lld МіБ, ціль %lld МіБ\n",
           cached(argv[optind]) >> 20, cached(argv[optind + 1]) >> 20);

    io_uring_queue_exit(&ring);
    close(in);
    close(out);
    return 0;
}
