#define _GNU_SOURCE
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <sched.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef SCHED_DEADLINE
#define SCHED_DEADLINE 6
#endif
#ifndef SCHED_FLAG_DL_OVERRUN
#define SCHED_FLAG_DL_OVERRUN 0x04
#endif

struct sched_attr {
    uint32_t size{}, sched_policy{};
    uint64_t sched_flags{};
    int32_t  sched_nice{};
    uint32_t sched_priority{};
    uint64_t sched_runtime{}, sched_deadline{}, sched_period{};
};

static void do_one_job() {
    auto start = std::chrono::steady_clock::now();
    while (std::chrono::steady_clock::now() - start < std::chrono::microseconds(800)) {}
}

int main() {
    sched_attr a{};
    a.size           = sizeof(a);
    a.sched_policy   = SCHED_DEADLINE;
    a.sched_flags    = SCHED_FLAG_DL_OVERRUN;
    a.sched_runtime  = 1200 * 1000;
    a.sched_deadline = 2500 * 1000;
    a.sched_period   = 5000 * 1000;

    if (syscall(SYS_sched_setattr, 0, &a, 0u) != 0) {
        switch (errno) {
        case EPERM:  std::cerr << "немає CAP_SYS_NICE або звужена маска ядер\n"; break;
        case EBUSY:  std::cerr << "смуга вичерпана: сума часток не влазить\n";   break;
        case EINVAL: std::cerr << "порушено runtime ≤ deadline ≤ period\n";      break;
        default:     std::perror("sched_setattr");
        }
        return 1;
    }

    for (int i = 0; i < 10; ++i) {
        do_one_job();
        sched_yield();
    }
    return 0;
}
