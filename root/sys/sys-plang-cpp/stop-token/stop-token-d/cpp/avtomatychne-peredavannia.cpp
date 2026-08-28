#include <iostream>
#include <stop_token>
#include <thread>

void background_worker(std::stop_token stoken, int multiplier) {
    int counter = 0;
    while (!stoken.stop_requested()) {
        std::cout << "Обчислення: " << (counter++ * multiplier) << "\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(40));
    }
    std::cout << "Фоновий потік завершився за сигналом stop_token.\n";
}

void run_task() {
    // jthread автоматично передає stop_token у background_worker
    std::jthread worker_thread(background_worker, 10);

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    // При виході з run_task() деструктор worker_thread:
    // 1. Автоматично викликає request_stop()
    // 2. Автоматично викликає join()
} // Жодних падінь через std::terminate(), ресурси звільняються чисто!
