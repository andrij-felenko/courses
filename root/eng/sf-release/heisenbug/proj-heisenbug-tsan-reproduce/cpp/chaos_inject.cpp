// chaos_inject.cpp
#include <iostream>
#include <random>
#include <thread>
#include <chrono>
#include <dlfcn.h>
#include <pthread.h>

extern "C" int pthread_mutex_lock(pthread_mutex_t* mutex) {
    static auto real_lock = reinterpret_cast<int(*)(pthread_mutex_t*)>(
        dlsym(RTLD_NEXT, "pthread_mutex_lock")
    );

    thread_local std::mt19937 gen(std::random_device{}());
    thread_local std::uniform_int_distribution<int> dist_yield(0, 3);
    thread_local std::uniform_int_distribution<int> dist_sleep(0, 9);
    thread_local std::uniform_int_distribution<int> dist_duration(1, 50);

    if (dist_yield(gen) == 0) {
        std::this_thread::yield();
    }
    if (dist_sleep(gen) == 0) {
        std::this_thread::sleep_for(std::chrono::microseconds(dist_duration(gen)));
    }

    return real_lock(mutex);
}
