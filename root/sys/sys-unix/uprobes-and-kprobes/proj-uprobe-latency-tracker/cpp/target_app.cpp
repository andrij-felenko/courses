// target_app.cpp - Цільова програма мовою C++
#include <iostream>
#include <thread>
#include <chrono>
#include <unistd.h>

// Функція, затримку якої ми будемо інструментувати
void compute_hash(int iterations) {
    volatile long long hash = 0;
    for (int i = 0; i < iterations * 100000; ++i) {
        hash += i ^ (i >> 3);
    }
}

int main() {
    std::cout << "Target App C++ запущено (PID: " << getpid() << ")\n";
    while (true) {
        compute_hash(50);
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        compute_hash(200);
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    return 0;
}
