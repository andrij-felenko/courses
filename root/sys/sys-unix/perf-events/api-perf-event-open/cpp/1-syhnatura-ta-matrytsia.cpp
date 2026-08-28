#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>
#include <expected>

namespace sys::abi {
    inline std::expected<int, std::error_code> perf_event_open(
        struct perf_event_attr* attr, pid_t pid, int cpu, int group_fd, unsigned long flags) noexcept {
        long res = ::syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
        if (res == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<int>(res);
    }
}
