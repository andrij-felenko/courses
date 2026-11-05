#include <iostream>
#include <thread>
#include <chrono>

// Звичайна змінна прапорця без кваліфікатора volatile
bool stop_flag = false;

void worker_thread() {
    std::cout << "[Потік виконавця]: Розпочато очікування прапорця...\n";

    // Компілятор виносить читання stop_flag за межі циклу під час оптимізації
    while (!stop_flag) {
        // Порожній цикл пасивного очікування
    }

    std::cout << "[Потік виконавця]: Прапорець отримано! Завершення роботи.\n";
}

int main() {
    std::thread t(worker_thread);

    // Симуляція виконання корисного навантаження
    std::this_thread::sleep_for(std::chrono::seconds(1));

    std::cout << "[Головний потік]: Зміна прапорця stop_flag = true\n";
    stop_flag = true;

    t.join();
    std::cout << "[Головний потік]: Програму успішно завершено.\n";
    return 0;
}
