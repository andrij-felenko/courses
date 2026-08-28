#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>

namespace sys {

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd) : fd_(fd) {}
    ~ScopedFd() { if (fd_ != -1) ::close(fd_); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ != -1; }
};

struct SampleRecord {
    std::uint64_t ip;
    std::uint32_t pid;
    std::uint32_t tid;
    std::uint64_t time;
};

class PerfRingBuffer {
    ScopedFd fd_;
    void* mmap_base_{MAP_FAILED};
    std::size_t mmap_size_{0};
    std::size_t page_size_{0};
    std::size_t data_size_{0};

    static long perf_event_open_sys(struct perf_event_attr* attr, pid_t pid,
                                   int cpu, int group_fd, unsigned long flags) {
        return ::syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
    }

public:
    static std::expected<PerfRingBuffer, std::error_code> create(std::uint64_t sample_period, std::size_t data_pages = 8) {
        struct perf_event_attr pe{};
        pe.type = PERF_TYPE_HARDWARE;
        pe.size = sizeof(struct perf_event_attr);
        pe.config = PERF_COUNT_HW_CPU_CYCLES;
        pe.sample_period = sample_period;
        pe.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME;
        pe.disabled = 1;
        pe.exclude_kernel = 1;
        pe.exclude_hv = 1;

        int raw_fd = static_cast<int>(perf_event_open_sys(&pe, 0, -1, -1, 0));
        if (raw_fd == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ScopedFd fd(raw_fd);
        std::size_t psize = static_cast<std::size_t>(::sysconf(_SC_PAGESIZE));
        std::size_t total_size = psize * (1 + data_pages);

        void* base = ::mmap(nullptr, total_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd.get(), 0);
        if (base == MAP_FAILED) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return PerfRingBuffer(std::move(fd), base, total_size, psize, psize * data_pages);
    }

    PerfRingBuffer(ScopedFd fd, void* base, std::size_t total_size, std::size_t psize, std::size_t dsize)
        : fd_(std::move(fd)), mmap_base_(base), mmap_size_(total_size), page_size_(psize), data_size_(dsize) {}

    ~PerfRingBuffer() {
        if (mmap_base_ != MAP_FAILED) {
            ::munmap(mmap_base_, mmap_size_);
        }
    }

    PerfRingBuffer(const PerfRingBuffer&) = delete;
    PerfRingBuffer& operator=(const PerfRingBuffer&) = delete;
    PerfRingBuffer(PerfRingBuffer&&) noexcept = default;

    void start() {
        ::ioctl(fd_.get(), PERF_EVENT_IOC_RESET, 0);
        ::ioctl(fd_.get(), PERF_EVENT_IOC_ENABLE, 0);
    }

    void stop() {
        ::ioctl(fd_.get(), PERF_EVENT_IOC_DISABLE, 0);
    }

    [[nodiscard]] std::vector<SampleRecord> consume_samples() {
        std::vector<SampleRecord> records;
        auto* hdr = static_cast<struct perf_event_mmap_page*>(mmap_base_);
        auto* data_boundary = static_cast<const char*>(mmap_base_) + page_size_;

        std::uint64_t head = std::atomic_load_explicit(
            reinterpret_cast<const std::atomic<std::uint64_t>*>(&hdr->data_head),
            std::memory_order_acquire
        );
        std::uint64_t tail = hdr->data_tail;

        while (tail < head) {
            std::uint64_t offset = tail % data_size_;
            auto* phead = reinterpret_cast<const struct perf_event_header*>(data_boundary + offset);

            if (phead->size == 0) break;

            if (phead->type == PERF_RECORD_SAMPLE) {
                struct RawSample {
                    std::uint64_t ip;
                    std::uint32_t pid;
                    std::uint32_t tid;
                    std::uint64_t time;
                };
                const auto* raw = reinterpret_cast<const RawSample*>(
                    reinterpret_cast<const char*>(phead) + sizeof(struct perf_event_header)
                );
                records.push_back(SampleRecord{raw->ip, raw->pid, raw->tid, raw->time});
            }
            tail += phead->size;
        }

        std::atomic_store_explicit(
            reinterpret_cast<std::atomic<std::uint64_t>*>(&hdr->data_tail),
            tail, std::memory_order_release
        );
        return records;
    }
};

} // namespace sys

int main() {
    auto profiler_res = sys::PerfRingBuffer::create(100'000);
    if (!profiler_res) {
        std::cerr << "Помилка ініціалізації perf: " << profiler_res.error().message() << '\n';
        return 1;
    }

    auto profiler = std::move(*profiler_res);
    profiler.start();

    volatile std::uint64_t dummy{0};
    for (std::uint64_t i = 0; i < 50'000'000ULL; ++i) {
        dummy += i;
    }

    profiler.stop();

    auto samples = profiler.consume_samples();
    std::cout << "Отримано вибірок у C++: " << samples.size() << '\n';

    for (std::size_t i = 0; i < std::min<std::size_t>(5, samples.size()); ++i) {
        const auto& s = samples[i];
        std::cout << "  [Вибірка #" << (i + 1) << "] IP = 0x" << std::hex << s.ip
                  << std::dec << ", PID = " << s.pid << ", Time = " << s.time << " ns\n";
    }

    return 0;
}
