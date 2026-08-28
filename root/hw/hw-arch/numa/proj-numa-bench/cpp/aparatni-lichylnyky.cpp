#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <format>

class ScopedPerfCounter {
public:
    ScopedPerfCounter(std::uint32_t type, std::uint64_t config) {
        perf_event_attr pe{};
        pe.type = type;
        pe.size = sizeof(perf_event_attr);
        pe.config = config;
        pe.disabled = 1;
        pe.exclude_kernel = 1;
        pe.exclude_hv = 1;

        fd_ = static_cast<int>(syscall(__NR_perf_event_open, &pe, 0, -1, -1, 0));
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити апаратний лічильник perf");
        }
    }

    ~ScopedPerfCounter() noexcept {
        if (fd_ >= 0) close(fd_);
    }

    ScopedPerfCounter(const ScopedPerfCounter&) = delete;
    ScopedPerfCounter& operator=(const ScopedPerfCounter&) = delete;

    void start() const noexcept {
        ioctl(fd_, PERF_EVENT_IOC_ENABLE, 0);
    }

    void stop() const noexcept {
        ioctl(fd_, PERF_EVENT_IOC_DISABLE, 0);
    }

    [[nodiscard]] std::uint64_t read_value() const {
        std::uint64_t val = 0;
        if (read(fd_, &val, sizeof(std::uint64_t)) != sizeof(std::uint64_t)) {
            throw std::runtime_error("Помилка читання значення лічильника");
        }
        return val;
    }

private:
    int fd_{-1};
};
