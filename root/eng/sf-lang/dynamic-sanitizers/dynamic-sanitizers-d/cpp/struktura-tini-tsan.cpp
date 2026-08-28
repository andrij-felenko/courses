#include <iostream>
#include <thread>
#include <atomic>

int g_unsynchronized_counter = 0;

void worker() {
    for (int i = 0; i < 1000; ++i) {
        // Одночасна модифікація сирого int двома потоками
        ++g_unsynchronized_counter; // TSan фіксує Data Race
    }
}

int main() {
    std::thread t1(worker);
    std::thread t2(worker);

    t1.join();
    t2.join();
    return 0;
}
