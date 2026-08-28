#include <thread>
#include <pthread.h>
#include <sched.h>
#include <system_error>
#include <iostream>

// Прив'язка потоку std::thread до конкретного логічного ядра core_id
void pin_thread_to_core(std::thread& th, int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    
    int rc = pthread_setaffinity_np(th.native_handle(), sizeof(cpu_set_t), &cpuset);
    if (rc != 0) {
        throw std::system_error(rc, std::generic_category(), "Не вдалося прив'язати потік до ядра");
    }
}
