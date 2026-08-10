# ⚙️ Кільце на двох процесів: /dev/shm, атомарні індекси, eventfd

Дві програми, запущені окремо одна від одної, передають потік записів так, щоб жоден байт не проходив через ядро, а читач при цьому не крутив цикл, а спав. Нижче — повний робочий код цієї конструкції: один сегмент спільної пам'яті, два атомарні лічильники й один дескриптор на пробудження.

## Що будуємо

Виробник збирає телеметрію й раз на кілька мікросекунд викидає короткий запис змінної довжини. Споживач ці записи вичитує й складає на диск. Спільного предка немає: обидва запускаються самі по собі, тож успадкувати відображення нема від кого.

З цього тягнуться чотири вимоги, і кожна далі перетвориться на конкретний рядок коду. Записи різної довжини — отже, потрібне обрамлення. Гарячий шлях без системних викликів — отже, індекси живуть у самому сегменті. Читач, коли даних нема, мусить заснути — отже, поруч потрібен об'єкт ядра, на якому можна чекати. І переповнення не має ані блокувати виробника, ані псувати вже покладене.

## Розкладка сегмента

Тіло — суцільний масив байтів, у якому запис може лягти «через край»: почнеться в кінці й продовжиться на початку. Це звичайний [кільцевий буфер](book:algorithms/ring-buffer), у якого позиція перетворюється на зсув узяттям остачі від довжини. Ділення на гарячому шляху зайве, тож довжину тіла беремо **степенем двійки** — тоді остача це просто `pos & (RING_BYTES − 1)`, одна інструкція замість десятків тактів на цілочисельне ділення.

Індекси не скидаємо на нуль після обороту, а лишаємо рости й переповнюватися разом із 32-бітним типом. Виграш у тому, що зникає вічна двозначність кільця: коли індекси обрізані до довжини тіла, стан «повне» й стан «порожнє» дають однакову пару чисел, і їх доводиться розрізняти зайвим прапорцем. У вільних лічильниках такого нема — беззнакова різниця `head − tail` дає зайняте місце правильно навіть у момент, коли `head` уже перескочив через нуль, а `tail` ще ні.

![Позиція перетворюється на зсув маскою; запис через край копіюють двома шматками](/reference/unix-linux/signals-ipc/posix-shared-memory/img/ring-wrap.svg)

*Зайнято = head − tail, і жодних окремих прапорців «повне/порожнє».*

Далі — розміщення самих лічильників. `head` рухає тільки виробник, `tail` тільки споживач, але читає кожен обидва. Якщо оголосити їх поруч, вони потраплять в одну кеш-лінію, і два ядра почнуть відбирати цю лінію одне в одного на кожному записі, хоч торкаються різних змінних. Це [хибне спільне використання кеш-лінії](book:programming/false-sharing), і коштує воно десятки наносекунд там, де мали б бути одиниці. Тому кожен лічильник отримує `_Alignas(64)` — власну лінію цілком.

Усередині сегмента немає жодного вказівника: `mmap` кладе той самий об'єкт у двох процесах за різними адресами, тож адреса, записана одним, у другого не означає нічого. Тому все, що зберігається в заголовку, — це числа-зсуви від початку відображення.

## Порядок, а не лише вміст

Ядро гарантує, що обидва процеси бачать одні байти. Воно нічого не гарантує про **порядок**, у якому вони з'являються, — цим відає процесор і компілятор.

Тому публікація запису розпадається на дві різні за природою дії: спершу дані копіюються в тіло звичайним `memcpy`, і лише потім новий `head` записується атомарно з семантикою випуску. Читач, побачивши цей `head` захопленням, дістає гарантію: усе, що виробник записав **до** випуску, для нього вже видиме. Без цієї пари він цілком міг би побачити свіжий індекс над ще не дописаним тілом ([упорядкування пам'яті](book:programming/memory-ordering-barriers)).

Приємний побічний наслідок: якщо виробник помре посеред копіювання, кільце лишиться цілим. Наполовину покладений запис ніхто не побачить, бо `head` так і не зрушив — читач просто не знає про його існування.

## Як розбудити того, хто спить

Спільна пам'ять німа: у ній нема на чому заснути. Потрібен об'єкт ядра — беремо [eventfd](book:unix-linux/eventfd-and-futex), лічильник із дескриптором: запис вісьмох байтів додає до нього, читання повертає накопичене й обнуляє, а на порожньому лічильнику читач блокується. У Linux він є з версії 2.6.22.

Тут вилазить те, про що зазвичай згадують надто пізно: **eventfd не має імені**. Сегмент пам'яті два чужі процеси знаходять за рядком у `/dev/shm`, а дескриптор так знайти не можна — його або успадковують через `fork`, або передають [сокетом домену Unix](book:unix-linux/unix-domain-sockets) допоміжним повідомленням `SCM_RIGHTS` (механіка розібрана окремо — [передати дескриптор](book:unix-linux/unix-domain-sockets/proj-pass-a-descriptor.md)). Рендеву-сокет у цій конструкції неминучий — і, з'явившись, окупає себе тричі: приносить дескриптор, задає момент «сегмент уже готовий» і своїм розривом повідомляє про смерть сусіда.

Будити на кожному записі не можна — це знищило б увесь сенс: `write` в eventfd коштує стільки ж, скільки запис у канал, і ми повернулися б до тисяч системних викликів на секунду. Тому в заголовку є прапорець `need_wake`: читач піднімає його **перед** тим, як заснути, а виробник смикає eventfd лише тоді, коли бачить прапорець піднятим. На повному кільці системних викликів не робиться взагалі.

![Читач оголошує намір заснути, перевіряє ще раз і лише тоді блокується](/reference/unix-linux/signals-ipc/posix-shared-memory/img/wake-handshake.svg)

*Прапорець піднімають до перевірки, а не після: інакше запис устигає прослизнути в проміжок.*

І саме тут звичного випуску-захоплення **не досить**. Читач пише прапорець і читає `head`; виробник пише `head` і читає прапорець — записи в різні комірки, які кожен бік мусить побачити раніше за своє читання. Буфер запису процесора має повне право затримати обидва записи, і тоді читач не побачить даних, виробник не побачить прапорця, і читач засне назавжди при повному кільці. Ліки — повний бар'єр (`atomic_thread_fence(memory_order_seq_cst)`) між записом і читанням на **обох** боках; напівбар'єрами тут не обійтися.

## Код

Одна програма у двох ролях: `./shmring r` — споживач (він же власник сегмента), `./shmring w` — виробник.

:::tabs

```c
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
```

```cpp
// shmring.cpp — те саме кільце: RAII на дескриптор і відображення, std::atomic на індекси.
// g++ -O2 -std=c++20 -o shmring shmring.cpp
#include <fcntl.h>
#include <sys/eventfd.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

#include <algorithm>
#include <atomic>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <format>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

namespace {

constexpr const char  *kShm   = "/telemetry.ring";
constexpr std::string_view kSock = "telemetry.ring";   // абстрактне ім'я AF_UNIX
constexpr std::uint32_t kMagic = 0x31474e52u;
constexpr std::uint32_t kBytes = 1u << 20;             // СТЕПІНЬ ДВІЙКИ
constexpr std::uint32_t kMask  = kBytes - 1u;
constexpr std::size_t   kLine  = 64;   // std::hardware_destructive_interference_size
constexpr std::uint32_t kMaxMsg = 1u << 16;

[[noreturn]] void fail(const char *what)
{ throw std::system_error(errno, std::system_category(), what); }

struct Ring {
    std::uint32_t magic;
    std::uint32_t bytes;
    alignas(kLine) std::atomic<std::uint32_t> head;       // рухає ЛИШЕ виробник
    alignas(kLine) std::atomic<std::uint32_t> tail;       // рухає ЛИШЕ споживач
    alignas(kLine) std::atomic<std::uint32_t> need_wake;
    alignas(kLine) std::byte data[kBytes];

    void copy_in(std::uint32_t pos, const void *src, std::uint32_t n) noexcept {
        const std::uint32_t off = pos & kMask;
        const std::uint32_t first = std::min(kBytes - off, n);
        std::memcpy(data + off, src, first);
        std::memcpy(data, static_cast<const std::byte *>(src) + first, n - first);
    }
    void copy_out(std::uint32_t pos, void *dst, std::uint32_t n) const noexcept {
        const std::uint32_t off = pos & kMask;
        const std::uint32_t first = std::min(kBytes - off, n);
        std::memcpy(dst, data + off, first);
        std::memcpy(static_cast<std::byte *>(dst) + first, data, n - first);
    }

    bool push(std::span<const std::byte> msg) noexcept {
        const auto n = static_cast<std::uint32_t>(msg.size());
        const std::uint32_t h = head.load(std::memory_order_relaxed);   // наш власний
        const std::uint32_t t = tail.load(std::memory_order_acquire);   // чужий
        if (kBytes - (h - t) < n + 4) return false;
        copy_in(h, &n, 4);
        copy_in(h + 4, msg.data(), n);
        head.store(h + 4 + n, std::memory_order_release);
        return true;
    }

    // порожнє std::optional — нема чого читати; виняток — сегмент зіпсовано
    std::optional<std::uint32_t> pop(std::span<std::byte> out) {
        const std::uint32_t t = tail.load(std::memory_order_relaxed);
        const std::uint32_t h = head.load(std::memory_order_acquire);
        if (h == t) return std::nullopt;
        std::uint32_t n;
        copy_out(t, &n, 4);                       // спершу ДО СЕБЕ, потім перевіряти
        if (n > out.size()) fail("довжина запису поза межами буфера");
        if (h - t < n + 4) fail("довжина запису не сходиться з head");
        copy_out(t + 4, out.data(), n);
        tail.store(t + 4 + n, std::memory_order_release);
        return n;
    }
};

// Без апаратної атомарності std::atomic ховає замок у таблиці ПРОЦЕСУ —
// у спільній пам'яті два процеси замикали б різні замки й не помітили б цього.
static_assert(std::atomic<std::uint32_t>::is_always_lock_free);

class Fd {
public:
    explicit Fd(int fd) : fd_(fd) { if (fd_ < 0) fail("fd"); }
    ~Fd() { if (fd_ >= 0) ::close(fd_); }
    Fd(Fd &&o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    Fd(const Fd &) = delete;
    Fd &operator=(const Fd &) = delete;
    int get() const noexcept { return fd_; }
private:
    int fd_;
};

class Mapping {                       // munmap за виходом з області видимості
public:
    explicit Mapping(const Fd &fd) {
        void *p = ::mmap(nullptr, sizeof(Ring), PROT_READ | PROT_WRITE,
                         MAP_SHARED, fd.get(), 0);
        if (p == MAP_FAILED) fail("mmap");
        ring_ = static_cast<Ring *>(p);
    }
    ~Mapping() { if (ring_) ::munmap(ring_, sizeof(Ring)); }
    Mapping(const Mapping &) = delete;
    Mapping &operator=(const Mapping &) = delete;
    Ring *operator->() const noexcept { return ring_; }
    Ring &operator*() const noexcept { return *ring_; }
private:
    Ring *ring_ = nullptr;
};

// Передача дескриптора — чистий syscall: обгортки в стандартній бібліотеці немає.
socklen_t addr_of(sockaddr_un &a)
{
    std::memset(&a, 0, sizeof a);
    a.sun_family = AF_UNIX;
    std::memcpy(a.sun_path + 1, kSock.data(), kSock.size());   // перший байт NUL
    return static_cast<socklen_t>(offsetof(sockaddr_un, sun_path) + 1 + kSock.size());
}

void send_fd(int s, int fd)
{
    char b = 0;
    iovec io{ &b, 1 };
    alignas(cmsghdr) char raw[CMSG_SPACE(sizeof(int))]{};
    msghdr m{};
    m.msg_iov = &io; m.msg_iovlen = 1;
    m.msg_control = raw; m.msg_controllen = sizeof raw;
    cmsghdr *c = CMSG_FIRSTHDR(&m);
    c->cmsg_level = SOL_SOCKET;
    c->cmsg_type = SCM_RIGHTS;
    c->cmsg_len = CMSG_LEN(sizeof(int));
    std::memcpy(CMSG_DATA(c), &fd, sizeof fd);
    if (::sendmsg(s, &m, 0) != 1) fail("sendmsg");
}

Fd recv_fd(int s)
{
    char b;
    iovec io{ &b, 1 };
    alignas(cmsghdr) char raw[CMSG_SPACE(sizeof(int))]{};
    msghdr m{};
    m.msg_iov = &io; m.msg_iovlen = 1;
    m.msg_control = raw; m.msg_controllen = sizeof raw;
    if (::recvmsg(s, &m, MSG_CMSG_CLOEXEC) != 1) fail("recvmsg");
    cmsghdr *c = CMSG_FIRSTHDR(&m);
    if (!c || c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS)
        fail("допоміжне повідомлення без дескриптора");
    int fd;
    std::memcpy(&fd, CMSG_DATA(c), sizeof fd);
    return Fd{ fd };
}

void consumer()
{
    // bind абстрактного імені — заразом і замок «лише один споживач».
    Fd srv{ ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0) };
    sockaddr_un a;
    const socklen_t alen = addr_of(a);
    if (::bind(srv.get(), reinterpret_cast<sockaddr *>(&a), alen) < 0) fail("bind");
    if (::listen(srv.get(), 4) < 0) fail("listen");

    ::shm_unlink(kShm);                       // уламок після падіння
    Fd shm{ ::shm_open(kShm, O_CREAT | O_EXCL | O_RDWR, 0600) };
    if (::ftruncate(shm.get(), sizeof(Ring)) < 0) fail("ftruncate");
    Mapping r{ shm };                         // ~Fd закриє дескриптор: його вже не треба

    r->bytes = kBytes;
    r->head.store(0, std::memory_order_relaxed);
    r->tail.store(0, std::memory_order_relaxed);
    r->need_wake.store(0, std::memory_order_relaxed);
    r->magic = kMagic;

    Fd efd{ ::eventfd(0, EFD_CLOEXEC) };
    Fd cli{ ::accept(srv.get(), nullptr, nullptr) };
    send_fd(cli.get(), efd.get());            // після цього сегмент точно готовий

    std::vector<std::byte> buf(kMaxMsg);
    for (;;) {
        if (auto n = r->pop(buf)) {
            std::fwrite(buf.data(), 1, *n, stdout);
            continue;
        }
        r->need_wake.store(1, std::memory_order_relaxed);
        std::atomic_thread_fence(std::memory_order_seq_cst);   // прапорець ПЕРЕД перечитуванням
        if (r->head.load(std::memory_order_relaxed) !=
            r->tail.load(std::memory_order_relaxed)) {
            r->need_wake.store(0, std::memory_order_relaxed);
            continue;
        }
        std::uint64_t ticket;
        if (::read(efd.get(), &ticket, sizeof ticket) != sizeof ticket) fail("read(efd)");
    }
}

void producer()
{
    Fd s{ ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0) };
    sockaddr_un a;
    const socklen_t alen = addr_of(a);
    if (::connect(s.get(), reinterpret_cast<sockaddr *>(&a), alen) < 0) fail("connect");
    Fd efd = recv_fd(s.get());

    Fd shm{ ::shm_open(kShm, O_RDWR, 0) };
    struct stat st{};
    if (::fstat(shm.get(), &st) < 0) fail("fstat");
    if (static_cast<std::size_t>(st.st_size) < sizeof(Ring))
        fail("сегмент коротший за розкладку");   // інакше SIGBUS при доторку
    Mapping r{ shm };
    if (r->magic != kMagic || r->bytes != kBytes) fail("чужа версія розкладки");

    unsigned long dropped = 0;
    for (unsigned long i = 0;; i++) {
        const std::string line = std::format("кадр {}\n", i);
        const std::span msg{ reinterpret_cast<const std::byte *>(line.data()), line.size() };
        if (!r->push(msg)) {                       // кільце повне
            if (++dropped % 10000 == 0)
                std::fprintf(stderr, "втрачено записів: %lu\n", dropped);
            continue;
        }
        std::atomic_thread_fence(std::memory_order_seq_cst);   // публікація ПЕРЕД прапорцем
        if (r->need_wake.load(std::memory_order_relaxed) &&
            r->need_wake.exchange(0, std::memory_order_relaxed)) {
            const std::uint64_t one = 1;
            if (::write(efd.get(), &one, sizeof one) != sizeof one) fail("write(efd)");
        }
    }
}

}  // namespace

int main(int argc, char **argv)
try {
    if (argc == 2 && argv[1][0] == 'r') { consumer(); return 0; }
    if (argc == 2 && argv[1][0] == 'w') { producer(); return 0; }
    std::fprintf(stderr, "уживання: %s r|w\n", argv[0]);
    return 2;
} catch (const std::exception &e) {
    std::fprintf(stderr, "%s\n", e.what());
    return 1;
}
```

:::

Версія на C++ відрізняється не синтаксисом, а тим, де живуть гарантії. Дескриптор і відображення закриваються деструктором, а не рядком, який легко забути. `std::span` носить довжину разом з даними, тож перевірка меж перестає бути справою уважності. І `static_assert` на `is_always_lock_free` ловить дуже підступну річ: коли апаратної атомарності для типу нема, [`std::atomic`](book:programming/std-atomic) підставляє замок із таблиці, що живе в адресному просторі **свого** процесу, — два процеси замикали б різні замки й нічого б не помітили.

## Ціна операції

На гарячому шляху немає ані системних викликів, ані динамічної пам'яті, ані ділень. Запис коштує один `memcpy` завдовжки із сам запис — час залежить від довжини запису й **не** залежить від того, скільки байтів уже лежить у кільці, — плюс два атомарні звертання й один повний бар'єр. Читання симетричне.

Витрати, які лишаються, — комунікаційні: кожен перехід `head` через кеш-лінію змушує лінію мандрувати між ядрами (десятки наносекунд), а повний бар'єр гальмує конвеєр процесора. Обидва зникають, коли працювати **пачками**: покласти сотню записів, а тоді один раз опублікувати `head` і один раз перевірити прапорець. У цьому коді бар'єр стоїть на кожному записі навмисно — так видно логіку; у бойовому виробнику він виноситься за цикл пачки.

## Пастки

**Довжина сегмента — не довжина відображення.** `mmap` радо відобразить більше, ніж об'єкт займає, і помилки не буде. Вона прийде пізніше й у найгіршому вигляді: доторк до сторінки за межею об'єкта дає `SIGBUS` посеред звичайного розіменування вказівника. Тому виробник перевіряє `fstat` **до** відображення, а не покладається на те, що творець усе зробив правильно.

**Зсув, а не вказівник.** У сегменті не можна зберігати ані вказівників, ані нічого, що тримає їх усередині: рядків, векторів, об'єктів із таблицею віртуальних методів. Обидві програми мусять однаково розуміти розмір і вирівнювання полів — саме тому в заголовку стоїть `magic` із версією розкладки, і міняти його треба разом зі структурою, інакше свіжий виробник мовчки писатиме за старою.

**Числу з чужого боку не можна вірити двічі.** У `pop` довжина спершу копіюється в локальну змінну й лише потім перевіряється: якби перевірка й використання читали спільну пам'ять окремо, сусід устиг би підмінити значення між ними, і копіювання вийшло б за буфер. Порядок перевірок теж не випадковий — спочатку `n > cap`, і лише тоді `n + 4`, бо на неперевіреному `n` саме додавання може переповнитися.

**Смерть учасника пам'ять не помічає.** Впав виробник — сегмент і його вміст лишаються, і наступний запуск підхопить чужий недописаний стан; тому споживач починає зі `shm_unlink` і створює сегмент із `O_EXCL`. Впав споживач — `tail` завмирає, кільце заповнюється, і виробник вічно губить записи, не маючи звідки дізнатися чому. Помітити це можна лише поза пам'яттю: рендеву-сокет при смерті сусіда дає розрив, і саме за ним варто стежити разом із рештою подій. Спільна пам'ять на такі питання не відповідає взагалі.

**Ім'я в `/dev/shm` — глобальний ресурс.** Два незалежні запуски однієї програми зіткнуться на ньому лобами. Коли учасники вже мають сокет, ім'я можна прибрати зовсім: `memfd_create` дає безіменний об'єкт у пам'яті, який передають тим самим `SCM_RIGHTS`, а «пломби» дозволяють ще й заборонити зміну розміру — і тоді перевірка `fstat` перестає бути перегонами ([memfd_create і пломби](book:unix-linux/memfd-create)).
