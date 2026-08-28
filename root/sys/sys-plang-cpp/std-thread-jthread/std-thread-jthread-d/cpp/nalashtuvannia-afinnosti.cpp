#include <thread>
#include <pthread.h>
#include <sched.h>

void bind_thread_to_core(std::jthread& th, int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);

    pthread_t handle = th.native_handle();
    int rc = pthread_setaffinity_np(handle, sizeof(cpu_set_t), &cpuset);
    if (rc != 0) {
        std::cerr << "Помилка встановлення CPU affinity\n";
    }
}
