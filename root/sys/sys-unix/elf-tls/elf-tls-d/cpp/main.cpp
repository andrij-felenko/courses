#include <iostream>
#include <thread>

// Глобальна потоко-локальна змінна у C++11
thread_local int thread_counter = 0;

void increment_counter() {
    thread_counter++;
    std::cout << "Thread " << std::this_thread::get_id() 
              << ": counter = " << thread_counter << '\n';
}
