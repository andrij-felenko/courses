#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched/types.h>

namespace sys {
    #ifndef SYS_sched_setattr
    #define SYS_sched_setattr 314
    #endif

    #ifndef SCHED_FLAG_UTIL_CLAMP
    #define SCHED_FLAG_UTIL_CLAMP 0x60
    #endif
}

int main() {
    struct sched_attr attr{};
    attr.size = sizeof(attr);
    attr.sched_policy = SCHED_OTHER;

    attr.sched_flags = SCHED_FLAG_UTIL_CLAMP;
    attr.sched_util_min = 512;
    attr.sched_util_max = 768;

    if (::syscall(SYS_sched_setattr, 0, &attr, 0) == 0) {
        std::cout << "[C++] uclamp успішно застосовано!\n";
    }
    return 0;
}
