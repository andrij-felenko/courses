/* shmring.c — кільце виробник–споживач на одному сегменті /dev/shm.
   gcc -O2 -o shmring shmring.c        (glibc < 2.34 потребує ще -lrt) */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/eventfd.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

#define SHM_NAME   "/telemetry.ring"
#define SOCK_NAME  "telemetry.ring"     /* абстрактний простір імен AF_UNIX */
#define RING_MAGIC 0x31474e52u          /* версія розкладки: міняється разом зі struct */
#define RING_BYTES (1u << 20)           /* СТЕПІНЬ ДВІЙКИ — інакше маска бреше */
#define RING_MASK  (RING_BYTES - 1u)
#define MAX_MSG    (1u << 16)

struct ring {
    uint32_t magic;                          /* пишеться до появи другого боку */
    uint32_t bytes;
    _Alignas(64) _Atomic uint32_t head;      /* рухає ЛИШЕ виробник */
    _Alignas(64) _Atomic uint32_t tail;      /* рухає ЛИШЕ споживач */
    _Alignas(64) _Atomic uint32_t need_wake;
    _Alignas(64) unsigned char data[RING_BYTES];
};

static void die(const char *what) { perror(what); exit(1); }

/* Зсув беремо маскою; якщо шматок не влазить до кінця тіла — копіюємо двічі.
   memcpy із нульовою довжиною законний, тож окремої гілки «не через край» нема. */
static void put(struct ring *r, uint32_t pos, const void *src, uint32_t n)
{
    uint32_t off = pos & RING_MASK;
    uint32_t first = RING_BYTES - off < n ? RING_BYTES - off : n;
    memcpy(r->data + off, src, first);
    memcpy(r->data, (const unsigned char *)src + first, n - first);
}

static void get(const struct ring *r, uint32_t pos, void *dst, uint32_t n)
{
    uint32_t off = pos & RING_MASK;
    uint32_t first = RING_BYTES - off < n ? RING_BYTES - off : n;
    memcpy(dst, r->data + off, first);
    memcpy((unsigned char *)dst + first, r->data, n - first);
}

static int push(struct ring *r, const void *msg, uint32_t n)
{
    uint32_t head = atomic_load_explicit(&r->head, memory_order_relaxed); /* наш власний */
    uint32_t tail = atomic_load_explicit(&r->tail, memory_order_acquire); /* чужий */
    if (RING_BYTES - (head - tail) < n + 4) return -1;   /* не влазить */
    put(r, head, &n, 4);                                 /* обрамлення: довжина попереду */
    put(r, head + 4, msg, n);
    atomic_store_explicit(&r->head, head + 4 + n, memory_order_release);  /* публікація */
    return 0;
}

/* >= 0 — довжина запису, -1 порожньо, -2 сегмент зіпсовано. */
static int pop(struct ring *r, void *dst, uint32_t cap)
{
    uint32_t tail = atomic_load_explicit(&r->tail, memory_order_relaxed);
    uint32_t head = atomic_load_explicit(&r->head, memory_order_acquire);
    if (head == tail) return -1;

    uint32_t n;
    get(r, tail, &n, 4);                 /* спершу ДО СЕБЕ, потім перевіряти */
    if (n > cap) return -2;              /* саме в цьому порядку: інакше n + 4 переповниться */
    if (head - tail < n + 4) return -2;
    get(r, tail + 4, dst, n);
    atomic_store_explicit(&r->tail, tail + 4 + n, memory_order_release);
    return (int)n;
}

static void addr_of(struct sockaddr_un *a, socklen_t *len)
{
    memset(a, 0, sizeof *a);
    a->sun_family = AF_UNIX;
    memcpy(a->sun_path + 1, SOCK_NAME, sizeof SOCK_NAME - 1);  /* перший байт NUL */
    *len = offsetof(struct sockaddr_un, sun_path) + 1 + sizeof SOCK_NAME - 1;
}

static int send_fd(int s, int fd)
{
    char b = 0;
    struct iovec io = { .iov_base = &b, .iov_len = 1 };
    union { char raw[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } u;
    memset(&u, 0, sizeof u);
    struct msghdr m = { .msg_iov = &io, .msg_iovlen = 1,
                        .msg_control = u.raw, .msg_controllen = sizeof u.raw };
    struct cmsghdr *c = CMSG_FIRSTHDR(&m);
    c->cmsg_level = SOL_SOCKET;
    c->cmsg_type = SCM_RIGHTS;
    c->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(c), &fd, sizeof fd);
    return sendmsg(s, &m, 0) == 1 ? 0 : -1;
}

static int recv_fd(int s)
{
    char b;
    struct iovec io = { .iov_base = &b, .iov_len = 1 };
    union { char raw[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } u;
    memset(&u, 0, sizeof u);
    struct msghdr m = { .msg_iov = &io, .msg_iovlen = 1,
                        .msg_control = u.raw, .msg_controllen = sizeof u.raw };
    if (recvmsg(s, &m, MSG_CMSG_CLOEXEC) != 1) return -1;
    struct cmsghdr *c = CMSG_FIRSTHDR(&m);
    if (!c || c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS) return -1;
    int fd;
    memcpy(&fd, CMSG_DATA(c), sizeof fd);
    return fd;
}

static int consumer(void)
{
    /* bind абстрактного імені — заразом і замок «лише один споживач»:
       живий сусід тримає ім'я, і другий примірник дістане EADDRINUSE. */
    int srv = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    struct sockaddr_un a; socklen_t alen;
    addr_of(&a, &alen);
    if (bind(srv, (struct sockaddr *)&a, alen) < 0) die("bind");
    if (listen(srv, 4) < 0) die("listen");

    shm_unlink(SHM_NAME);              /* уламок після падіння; O_EXCL нижче — страховка */
    int fd = shm_open(SHM_NAME, O_CREAT | O_EXCL | O_RDWR, 0600);
    if (fd < 0) die("shm_open");
    if (ftruncate(fd, sizeof(struct ring)) < 0) die("ftruncate");
    struct ring *r = mmap(NULL, sizeof *r, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (r == MAP_FAILED) die("mmap");
    close(fd);                          /* об'єкт тримає саме відображення */

    r->bytes = RING_BYTES;
    atomic_store_explicit(&r->head, 0, memory_order_relaxed);
    atomic_store_explicit(&r->tail, 0, memory_order_relaxed);
    atomic_store_explicit(&r->need_wake, 0, memory_order_relaxed);
    r->magic = RING_MAGIC;

    int efd = eventfd(0, EFD_CLOEXEC);
    if (efd < 0) die("eventfd");

    int cli = accept(srv, NULL, NULL);          /* виробник прийшов… */
    if (cli < 0) die("accept");
    if (send_fd(cli, efd) < 0) die("send_fd");  /* …і бачить уже готовий сегмент */

    unsigned char msg[MAX_MSG];
    for (;;) {
        int n = pop(r, msg, sizeof msg);
        if (n >= 0) { fwrite(msg, 1, (size_t)n, stdout); continue; }
        if (n == -2) { fprintf(stderr, "розкладку зіпсовано\n"); return 1; }

        atomic_store_explicit(&r->need_wake, 1, memory_order_relaxed);
        atomic_thread_fence(memory_order_seq_cst);   /* прапорець ПЕРЕД перечитуванням */
        if (atomic_load_explicit(&r->head, memory_order_relaxed) !=
            atomic_load_explicit(&r->tail, memory_order_relaxed)) {
            atomic_store_explicit(&r->need_wake, 0, memory_order_relaxed);
            continue;                                /* устигло приїхати — не спимо */
        }
        uint64_t ticket;
        if (read(efd, &ticket, sizeof ticket) != (ssize_t)sizeof ticket) die("read(efd)");
    }
}

static int producer(void)
{
    int s = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    struct sockaddr_un a; socklen_t alen;
    addr_of(&a, &alen);
    if (connect(s, (struct sockaddr *)&a, alen) < 0) die("connect");
    int efd = recv_fd(s);                    /* той самий об'єкт ядра, інше число */
    if (efd < 0) die("recv_fd");

    int fd = shm_open(SHM_NAME, O_RDWR, 0);
    if (fd < 0) die("shm_open");
    struct stat st;
    if (fstat(fd, &st) < 0) die("fstat");
    if ((size_t)st.st_size < sizeof(struct ring)) {   /* коротший об'єкт = SIGBUS при доторку */
        fprintf(stderr, "сегмент коротший за розкладку\n");
        return 1;
    }
    struct ring *r = mmap(NULL, sizeof *r, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (r == MAP_FAILED) die("mmap");
    close(fd);
    if (r->magic != RING_MAGIC || r->bytes != RING_BYTES) {
        fprintf(stderr, "чужа версія розкладки\n");
        return 1;
    }

    unsigned long dropped = 0;
    for (unsigned long i = 0;; i++) {
        char line[64];
        int n = snprintf(line, sizeof line, "кадр %lu\n", i);
        if (push(r, line, (uint32_t)n) < 0) {         /* кільце повне — губимо найновіше */
            if (++dropped % 10000 == 0)
                fprintf(stderr, "втрачено записів: %lu\n", dropped);
            continue;
        }
        atomic_thread_fence(memory_order_seq_cst);    /* публікація ПЕРЕД читанням прапорця */
        if (atomic_load_explicit(&r->need_wake, memory_order_relaxed) &&
            atomic_exchange_explicit(&r->need_wake, 0, memory_order_relaxed)) {
            uint64_t one = 1;
            if (write(efd, &one, sizeof one) != (ssize_t)sizeof one) die("write(efd)");
        }
    }
}

int main(int argc, char **argv)
{
    if (argc == 2 && argv[1][0] == 'r') return consumer();
    if (argc == 2 && argv[1][0] == 'w') return producer();
    fprintf(stderr, "уживання: %s r|w\n", argv[0]);
    return 2;
}
