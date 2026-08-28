#include <thread>
#include <iostream>
#include <memory>

void worker_routine(int id) {
    std::cout << "C++ worker thread " << id << " is running\n";
}

void launch_cpp_thread(int thread_id) {
    // Ідіоматичний C++11 запуск та приєднання
    std::thread t(worker_routine, thread_id);
    t.join(); // RAII та блокуюче приєднання
}
