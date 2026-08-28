// lazyregion.cpp — ділянка анонімної пам'яті, вміст якої програма породжує
// сама у мить першого дотику до сторінки (версія C++20).

#define _GNU_SOURCE
#include <cerrno>
#include <fcntl.h>
#include <poll.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <atomic>
#include <chrono>
#include <iostream>
#include <memory>
#include <span>
#include <thread>
#include <vector>
#include <unistd.h>
#include <linux/userfaultfd.h>
#include <sys/eventfd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/syscall.h>

#ifndef UFFD_USER_MODE_ONLY
#define UFFD_USER_MODE_ONLY 1
#endif

namespace {

constexpr std::size_t REGION_PAGES = 65536ul;
constexpr std::size_t SWEEP_PAGES  = 4096ul;
constexpr std::size_t TOUCHES      = 200ul;
constexpr std::size_t STRIDE       = 307ul;

class UniqueFd {
    int fd_ = -1;
public:
    UniqueFd() = default;
    explicit UniqueFd(int fd) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) { reset(); fd_ = o.fd_; o.fd_ = -1; }
        return *this;
    }
    [[nodiscard]] int get() const { return fd_; }
    explicit operator bool() const { return fd_ >= 0; }
    void reset(int fd = -1) { if (fd_ >= 0) ::close(fd_); fd_ = fd; }
    int release() { int tmp = fd_; fd_ = -1; return tmp; }
};

void die(const char* what) {
    std::perror(what);
    std::exit(1);
}

std::size_t page_size = 0;
std::uint8_t* region  = nullptr;
std::size_t region_len = 0;
std::size_t batch_pages = 16;
UniqueFd uffd;
UniqueFd stopfd;

std::atomic<long> n_msgs{0};
std::atomic<long> n_placed{0};
std::atomic<long> n_exist{0};
std::atomic<long> ns_produce{0};
std::atomic<long> ns_copy{0};
volatile std::uint8_t sink = 0;

std::int64_t now_ns() {
    auto now = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<std::chrono::nanoseconds>(now.time_since_epoch()).count();
}

void produce(std::size_t index, std::span<std::uint8_t> dst) {
    std::uint64_t x = index * 0x9E3779B97F4A7C15ull + 0x243F6A8885A308D3ull;
    for (std::size_t off = 0; off < page_size; off += 8) {
        std::uint64_t z = (x += 0x9E3779B97F4A7C15ull);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
        z ^= z >> 31;
        std::memcpy(dst.data() + off, &z, 8);
    }
}

void serve(std::uintptr_t addr, std::uint8_t* buf) {
    std::uintptr_t start = addr & ~(page_size - 1);
    std::size_t index = (start - reinterpret_cast<std::uintptr_t>(region)) / page_size;

    std::size_t count = batch_pages;
    if (index + count > REGION_PAGES)
        count = REGION_PAGES - index;

    auto t0 = now_ns();
    for (std::size_t k = 0; k < count; ++k)
        produce(index + k, std::span<std::uint8_t>(buf + k * page_size, page_size));
    auto t1 = now_ns();

    std::size_t want = count * page_size;
    std::size_t done = 0;
    std::size_t skipped = 0;

    while (done < want) {
        ::uffdio_copy c{
            .dst  = start + done,
            .src  = reinterpret_cast<std::uintptr_t>(buf + done),
            .len  = want - done,
            .mode = 0,
        };
        if (::ioctl(uffd.get(), UFFDIO_COPY, &c) == 0)
            break;
        if (errno == EAGAIN && c.copy > 0) {
            done += static_cast<std::size_t>(c.copy);
            continue;
        }
        if (errno == EEXIST) {
            done += page_size;
            skipped++;
            continue;
        }
        die("UFFDIO_COPY");
    }
    auto t2 = now_ns();

    n_placed   += static_cast<long>(count - skipped);
    n_exist    += static_cast<long>(skipped);
    ns_produce += (t1 - t0);
    ns_copy    += (t2 - t1);
}

void watcher() {
    std::vector<std::uint8_t> buf(batch_pages * page_size);

    ::pollfd pfd[2] = {
        { .fd = uffd.get(),   .events = POLLIN, .revents = 0 },
        { .fd = stopfd.get(), .events = POLLIN, .revents = 0 },
    };

    for (;;) {
        if (::poll(pfd, 2, -1) < 0) {
            if (errno == EINTR) continue;
            die("poll");
        }
        if (pfd[1].revents & POLLIN)
            break;
        if (pfd[0].revents & POLLERR) {
            std::cerr << "uffd не придатний до poll\n";
            std::exit(1);
        }
        if (!(pfd[0].revents & POLLIN))
            continue;

        ::uffd_msg msg[16];
        ssize_t got = ::read(uffd.get(), msg, sizeof(msg));
        if (got < 0) {
            if (errno == EAGAIN || errno == EINTR) continue;
            die("read(uffd)");
        }
        for (std::size_t i = 0; i < static_cast<std::size_t>(got) / sizeof(msg[0]); ++i) {
            if (msg[i].event != UFFD_EVENT_PAGEFAULT)
                continue;
            n_msgs++;
            serve(static_cast<std::uintptr_t>(msg[i].arg.pagefault.address), buf.data());
        }
    }
}

int open_uffd() {
    int fd = static_cast<int>(::syscall(SYS_userfaultfd,
                              O_CLOEXEC | O_NONBLOCK | UFFD_USER_MODE_ONLY));
    if (fd >= 0 || errno != EINVAL)
        return fd;
    return static_cast<int>(::syscall(SYS_userfaultfd, O_CLOEXEC | O_NONBLOCK));
}

long rss_kib() {
    FILE* f = std::fopen("/proc/self/status", "r");
    if (!f) return -1;
    char line[256];
    long kb = -1;
    while (std::fgets(line, sizeof(line), f)) {
        if (std::sscanf(line, "VmRSS: %ld kB", &kb) == 1) break;
    }
    std::fclose(f);
    return kb;
}

} // namespace

int main(int argc, char** argv) {
    if (argc > 1) {
        batch_pages = std::strtoul(argv[1], nullptr, 10);
        if (batch_pages < 1 || batch_pages > 512) {
            std::cerr << "пакет — від 1 до 512 сторінок\n";
            return 1;
        }
    }
    page_size  = static_cast<std::size_t>(::sysconf(_SC_PAGESIZE));
    region_len = REGION_PAGES * page_size;

    uffd.reset(open_uffd());
    if (!uffd) {
        int e = errno;
        std::cerr << "userfaultfd: " << std::strerror(e) << "\n";
        if (e == EPERM)
            std::cerr << "потрібен доступ до /dev/userfaultfd, CAP_SYS_PTRACE "
                         "або vm.unprivileged_userfaultfd = 1\n";
        return 1;
    }

    ::uffdio_api api{ .api = UFFD_API, .features = 0 };
    if (::ioctl(uffd.get(), UFFDIO_API, &api) < 0) die("UFFDIO_API");

    void* ptr = ::mmap(nullptr, region_len, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) die("mmap");
    region = static_cast<std::uint8_t*>(ptr);

    ::uffdio_register reg{
        .range = { .start = reinterpret_cast<std::uintptr_t>(region), .len = region_len },
        .mode  = UFFDIO_REGISTER_MODE_MISSING,
    };
    if (::ioctl(uffd.get(), UFFDIO_REGISTER, &reg) < 0) die("UFFDIO_REGISTER");
    if (!(reg.ioctls & (1ull << _UFFDIO_COPY))) {
        std::cerr << "ядро не дає UFFDIO_COPY на цій ділянці\n";
        return 1;
    }

    stopfd.reset(::eventfd(0, EFD_CLOEXEC));
    if (!stopfd) die("eventfd");

    std::thread worker(watcher);

    // Дослід 1: розкидані дотики — кожен потрапляє у власний збій.
    long m0 = n_msgs.load();
    auto t0 = now_ns();
    for (std::size_t i = 0; i < TOUCHES; ++i)
        sink = region[(SWEEP_PAGES + i * STRIDE) * page_size];
    auto scattered_ns = now_ns() - t0;
    long scattered_msgs = n_msgs.load() - m0;

    // Дослід 2: суцільний прохід — пакет закриває збої наперед.
    m0 = n_msgs.load();
    t0 = now_ns();
    for (std::size_t p = 0; p < SWEEP_PAGES; ++p)
        sink = region[p * page_size];
    auto sweep_ns = now_ns() - t0;
    long sweep_msgs = n_msgs.load() - m0;

    // Перевірка: у ділянці справді наш вміст, а не тиша.
    std::vector<std::uint8_t> expect(page_size);
    for (std::size_t i = 0; i < TOUCHES; i += 8) {
        std::size_t index = SWEEP_PAGES + i * STRIDE;
        produce(index, expect);
        if (std::memcmp(region + index * page_size, expect.data(), page_size) != 0) {
            std::cerr << "сторінка " << index << " прийшла не та\n";
            return 1;
        }
    }

    // Завершення: сигналимо та чекаємо на потік.
    std::uint64_t one = 1;
    if (::write(stopfd.get(), &one, sizeof(one)) != static_cast<ssize_t>(sizeof(one)))
        die("write(stopfd)");
    worker.join();

    ::uffdio_range range{
        .start = reinterpret_cast<std::uintptr_t>(region), .len = region_len
    };
    if (::ioctl(uffd.get(), UFFDIO_UNREGISTER, &range) < 0) die("UFFDIO_UNREGISTER");

    long total = n_msgs.load();
    double round_us = (scattered_ns + sweep_ns) / 1000.0 / static_cast<double>(total);

    std::printf("ділянка           : %lu МіБ, %lu сторінок по %zu Б\n",
                static_cast<unsigned long>(region_len >> 20), REGION_PAGES, page_size);
    std::printf("пакет             : %lu сторінок\n\n", batch_pages);
    std::printf("розкидані дотики  : %lu → %ld збоїв, %.2f мс\n",
                TOUCHES, scattered_msgs, scattered_ns / 1e6);
    std::printf("суцільний прохід  : %lu сторінок → %ld збоїв, %.2f мс\n",
                SWEEP_PAGES, sweep_msgs, sweep_ns / 1e6);
    std::printf("покладено         : %ld сторінок, уже було %ld\n\n",
                n_placed.load(), n_exist.load());
    std::printf("на один збій      : %.1f мкс\n", round_us);
    std::printf("  вироблення      : %.1f мкс\n", static_cast<double>(ns_produce.load()) / 1000.0 / total);
    std::printf("  UFFDIO_COPY     : %.1f мкс\n", static_cast<double>(ns_copy.load()) / 1000.0 / total);
    std::printf("  решта           : %.1f мкс\n",
                round_us - static_cast<double>(ns_produce.load() + ns_copy.load()) / 1000.0 / total);
    std::printf("VmRSS             : %ld КіБ\n", rss_kib());

    ::munmap(region, region_len);
    return 0;
}
