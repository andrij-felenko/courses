#include <thread>
#include <stdexcept>
#include <system_error>
#include <pthread.h>
#include <sched.h>

namespace tpc {

/* Безпечна C++ обгортка над прив'язкою потоку std::jthread або native handle */
inline void set_current_thread_affinity(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);

    const int rc = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    if (rc != 0) {
        throw std::system_error(rc, std::generic_category(), "Помилка встановлення CPU affinity");
    }
}

} // namespace tpc
