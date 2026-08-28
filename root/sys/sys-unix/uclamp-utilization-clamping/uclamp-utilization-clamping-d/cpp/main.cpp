#include <iostream>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <cerrno>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched/types.h>

namespace sys {
    #ifndef SYS_sched_setattr
    #define SYS_sched_setattr 314
    #endif

    #ifndef SCHED_FLAG_UTIL_CLAMP_MIN
    #define SCHED_FLAG_UTIL_CLAMP_MIN 0x20
    #endif

    #ifndef SCHED_FLAG_UTIL_CLAMP_MAX
    #define SCHED_FLAG_UTIL_CLAMP_MAX 0x40
    #endif
}

class TaskUtilization {
public:
    static bool setClamp(pid_t tid, uint32_t minUtil, uint32_t maxUtil) noexcept {
        struct sched_attr attr{};
        attr.size = sizeof(attr);
        attr.sched_policy = SCHED_OTHER;

        attr.sched_flags = SCHED_FLAG_UTIL_CLAMP_MIN | SCHED_FLAG_UTIL_CLAMP_MAX;
        attr.sched_util_min = minUtil;
        attr.sched_util_max = maxUtil;

        long res = ::syscall(SYS_sched_setattr, tid, &attr, 0);
        if (res < 0) {
            std::cerr << "Помилка sched_setattr: " << std::strerror(errno) << '\n';
            return false;
        }
        return true;
    }
};

int main() {
    pid_t tid = ::gettid();
    if (TaskUtilization::setClamp(tid, 512, 768)) {
        std::cout << "[C++] uclamp встановлено для TID " << tid << ": min=512, max=768\n";
    }
    return 0;
}
