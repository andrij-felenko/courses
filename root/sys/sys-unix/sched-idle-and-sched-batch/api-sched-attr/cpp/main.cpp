#include <iostream>
#include <system_error>
#include <cstdint>
#include <cerrno>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched.h>

#ifndef SYS_sched_setattr
#if defined(__x86_64__)
#define SYS_sched_setattr 314
#elif defined(__aarch64__)
#define SYS_sched_setattr 274
#elif defined(__riscv)
#define SYS_sched_setattr 274
#endif
#endif

#ifndef SCHED_FLAG_RESET_ON_FORK
#define SCHED_FLAG_RESET_ON_FORK 0x01
#endif

struct local_sched_attr {
    std::uint32_t size;
    std::uint32_t sched_policy;
    std::uint64_t sched_flags;
    std::int32_t  sched_nice;
    std::uint32_t sched_priority;
    std::uint64_t sched_runtime;
    std::uint64_t sched_deadline;
    std::uint64_t sched_period;
};

class TaskScheduler {
public:
    static void set_batch(pid_t pid, int nice_val, bool reset_on_fork) {
        local_sched_attr attr{};
        attr.size = sizeof(attr);
        attr.sched_policy = SCHED_BATCH;
        attr.sched_nice = nice_val;
        attr.sched_priority = 0;
        
        if (reset_on_fork) {
            attr.sched_flags |= SCHED_FLAG_RESET_ON_FORK;
        }
        
        if (::syscall(SYS_sched_setattr, pid, &attr, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                    "Не вдалося встановити SCHED_BATCH через sched_setattr");
        }
    }

    static void set_idle(pid_t pid) {
        local_sched_attr attr{};
        attr.size = sizeof(attr);
        attr.sched_policy = SCHED_IDLE;
        attr.sched_nice = 0;
        attr.sched_priority = 0;

        if (::syscall(SYS_sched_setattr, pid, &attr, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                    "Не вдалося встановити SCHED_IDLE через sched_setattr");
        }
    }
};
