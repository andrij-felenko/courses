#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include <system_error>

class PerfCounter {
    int fd_{-1};
public:
    PerfCounter(uint32_t type, uint64_t config) {
        struct perf_event_attr pe{};
        pe.type = type;
        pe.size = sizeof(struct perf_event_attr);
        pe.config = config;
        pe.disabled = 1;
        pe.exclude_kernel = 1;
        pe.exclude_hv = 1;

        fd_ = syscall(__NR_perf_event_open, &pe, 0, -1, -1, 0);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка perf_event_open");
        }
    }

    ~PerfCounter() {
        if (fd_ >= 0) close(fd_);
    }

    [[nodiscard]] uint64_t read_value() const {
        uint64_t val = 0;
        if (read(fd_, &val, sizeof(val)) != sizeof(val)) {
            return 0;
        }
        return val;
    }
};
