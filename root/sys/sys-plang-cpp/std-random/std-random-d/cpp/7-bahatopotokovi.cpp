#include <iostream>
#include <random>
#include <thread>
#include <vector>

void worker_thread(int thread_id) {
    // thread_local ініціалізується один раз при старті кожного потоку
    thread_local std::mt19937 rng([]() {
        std::random_device rd;
        return std::mt19937(rd());
    }());

    std::uniform_int_distribution<int> dist(100, 999);
    std::cout << "Thread " << thread_id << " generated: " << dist(rng) << "\n";
}

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(worker_thread, i);
    }
    for (auto& t : threads) {
        t.join();
    }
    return 0;
}
