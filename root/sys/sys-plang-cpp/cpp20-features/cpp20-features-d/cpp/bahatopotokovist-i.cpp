#include <thread>
#include <chrono>
#include <iostream>

void worker_routine(std::stop_token stoken, int id) {
    while (!stoken.stop_requested()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    std::cout << "Потік " << id << " коректно зупинився.\n";
}

int main() {
    std::jthread worker(worker_routine, 1);
    std::this_thread::sleep_for(std::chrono::milliseconds(120));
    // Деструктор worker автоматично викличе request_stop() та join()
    return 0;
}
