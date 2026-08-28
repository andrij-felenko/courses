// iolat.cpp — затримка дрібних читань під фоновою заливкою запису (C++20)
//   збірка: g++ -O2 -std=c++20 iolat.cpp -o iolat -lpthread
//   запуск: ./iolat <файл-для-читання> <файл-для-запису> <секунд>
#include <fcntl.h>
#include <math.h>
#include <sys/stat.h>
#include <unistd.h>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <memory>
#include <random>
#include <thread>
#include <vector>

constexpr uint32_t READ_BLK = 4096u;
constexpr uint32_t WRITE_BLK = 1u << 20;
constexpr uint64_t WRITE_FILE = 4ull << 30;
constexpr uint64_t WARMUP_NS = 2000000000ull;
constexpr uint32_t MAX_SAMPLES = 4000000u;

struct ScopedFd {
    int fd{-1};
    ScopedFd() = default;
    explicit ScopedFd(int f) : fd(f) {}
    ~ScopedFd() { if (fd >= 0) ::close(fd); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd(o.fd) { o.fd = -1; }
    ScopedFd& operator=(ScopedFd&& o) noexcept {
        if (this != &o) {
            if (fd >= 0) ::close(fd);
            fd = o.fd;
            o.fd = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const { return fd; }
    [[nodiscard]] bool valid() const { return fd >= 0; }
};

static std::atomic<bool> stop_flag{false};
static std::atomic<uint64_t> written_bytes{0};

static uint64_t now_ns() {
    auto t = std::chrono::steady_clock::now().time_since_epoch();
    return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(t).count());
}

static size_t dio_align(int fd) {
#ifdef STATX_DIOALIGN
    struct statx st{};
    if (statx(fd, "", AT_EMPTY_PATH, STATX_DIOALIGN, &st) == 0 &&
        (st.stx_mask & STATX_DIOALIGN) && st.stx_dio_offset_align) {
        size_t a = st.stx_dio_offset_align;
        if (st.stx_dio_mem_align > a) a = st.stx_dio_mem_align;
        return a;
    }
#endif
    return 4096;
}

static void flooder_worker(const std::string& path) {
    ScopedFd fd(::open(path.c_str(), O_WRONLY | O_CREAT, 0644));
    if (!fd.valid()) {
        std::perror("open write");
        return;
    }
    std::vector<char> buf(WRITE_BLK, static_cast<char>(0xA5));
    uint64_t off = 0;
    while (!stop_flag.load(std::memory_order_relaxed)) {
        ssize_t n = ::pwrite(fd.get(), buf.data(), WRITE_BLK, static_cast<off_t>(off));
        if (n <= 0) break;
        written_bytes.fetch_add(static_cast<uint64_t>(n), std::memory_order_relaxed);
        off = (off + static_cast<uint64_t>(n)) % WRITE_FILE;
        if (off != 0 && off % (64ull << 20) == 0) {
            ::sync_file_range(fd.get(), static_cast<off_t>(off - (64ull << 20)),
                              64ll << 20, SYNC_FILE_RANGE_WRITE);
        }
    }
}

static double pct_us(const std::vector<uint64_t>& v, double p) {
    if (v.empty()) return 0.0;
    size_t i = static_cast<size_t>(std::ceil(p / 100.0 * static_cast<double>(v.size())));
    if (i < 1) i = 1;
    if (i > v.size()) i = v.size();
    return static_cast<double>(v[i - 1]) / 1000.0;
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "usage: " << argv[0] << " <read-file> <write-file> <seconds>\n";
        return 2;
    }
    unsigned secs = static_cast<unsigned>(std::strtoul(argv[3], nullptr, 10));

    ScopedFd rfd(::open(argv[1], O_RDONLY | O_DIRECT));
    if (!rfd.valid()) {
        std::perror("open read (O_DIRECT)");
        return 1;
    }
    off_t size = ::lseek(rfd.get(), 0, SEEK_END);
    size_t align = dio_align(rfd.get());
    size_t blk = READ_BLK < align ? align : READ_BLK;
    if (size < static_cast<off_t>(blk * 262144)) {
        std::cerr << "файл замалий: читання мають розбігтися по носію\n";
        return 1;
    }

    void* raw_buf = nullptr;
    if (::posix_memalign(&raw_buf, align, blk) != 0) {
        std::perror("posix_memalign");
        return 1;
    }
    std::unique_ptr<void, void(*)(void*)> buf_holder(raw_buf, ::free);

    std::vector<uint64_t> lat;
    lat.reserve(MAX_SAMPLES);

    uint64_t nblocks = static_cast<uint64_t>(size) / blk;
    std::mt19937_64 rng(now_ns());
    std::uniform_int_distribution<uint64_t> dist(0, nblocks - 1);

    std::string write_path = argv[2];
    std::thread flooder_thread(flooder_worker, write_path);

    uint64_t t0 = now_ns();
    uint64_t deadline = t0 + static_cast<uint64_t>(secs) * 1000000000ull;
    uint64_t warm = t0 + WARMUP_NS;
    uint64_t t_first = 0;

    for (;;) {
        uint64_t a = now_ns();
        if (a >= deadline || lat.size() == MAX_SAMPLES) break;
        off_t off = static_cast<off_t>(dist(rng) * blk);
        ssize_t r = ::pread(rfd.get(), raw_buf, blk, off);
        uint64_t b = now_ns();
        if (r != static_cast<ssize_t>(blk)) {
            std::perror("pread");
            break;
        }
        if (a >= warm) {
            if (!t_first) t_first = a;
            lat.push_back(b - a);
        }
    }
    uint64_t t_end = now_ns();

    stop_flag.store(true, std::memory_order_relaxed);
    if (flooder_thread.joinable()) {
        flooder_thread.join();
    }

    if (lat.size() < 1000) {
        std::cerr << "замало вимірів\n";
        return 1;
    }

    std::sort(lat.begin(), lat.end());
    double span = static_cast<double>(t_end - t_first) / 1e9;
    double written_mb = static_cast<double>(written_bytes.load()) / (1u << 20);
    double elapsed_s = static_cast<double>(t_end - t0) / 1e9;

    std::printf("%8.0f %8.0f %8.0f %8.0f %9.0f %8.1f\n",
                pct_us(lat, 50.0), pct_us(lat, 99.0), pct_us(lat, 99.9),
                static_cast<double>(lat.back()) / 1000.0,
                static_cast<double>(lat.size()) / span,
                written_mb / elapsed_s);
    return 0;
}
