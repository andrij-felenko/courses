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
#include <stdexcept>
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

[[noreturn]] void fail(const char *what)          // збій системного виклику: є errno
{ throw std::system_error(errno, std::system_category(), what); }

[[noreturn]] void bad(const char *what)           // зіпсований вміст сегмента: errno ні до чого
{ throw std::runtime_error(what); }

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
        if (n > out.size()) bad("довжина запису поза межами буфера");
        if (h - t < n + 4) bad("довжина запису не сходиться з head");
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
        bad("допоміжне повідомлення без дескриптора");
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
        bad("сегмент коротший за розкладку");    // інакше SIGBUS при доторку
    Mapping r{ shm };
    if (r->magic != kMagic || r->bytes != kBytes) bad("чужа версія розкладки");

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
