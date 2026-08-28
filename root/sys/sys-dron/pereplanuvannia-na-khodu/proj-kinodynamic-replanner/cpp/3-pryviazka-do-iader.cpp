#include <pthread.h>
#include <sched.h>
#include <system_error>

void configure_realtime_thread(int core_id, int priority) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to set CPU affinity");
    }

    sched_param param{};
    param.sched_priority = priority;
    if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) != 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to set SCHED_FIFO");
    }
}
