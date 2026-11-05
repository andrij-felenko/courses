#include <iostream>
#include <thread>
#include <chrono>

// Кваліфікатор volatile забороняє кешування значень у регістрах
volatile bool stop_flag = false;

void worker_thread() {
    std::cout << "[Потік виконавця]: Розпочато очікування volatile-прапорця...\n";

    // Пряме звернення до пам'яті на кожному витку циклу
    while (!stop_flag) {
        // Очікування зміни стану в RAM
    }

    std::cout << "[Потік виконавця]: Прапорець помічено у RAM! Завершення роботи.\n";
}

int main() {
    std::thread t(worker_thread);

    std::this_thread::sleep_for(std::chrono::seconds(1));

    std::cout << "[Головний потік]: Запис у volatile-змінну stop_flag = true\n";
    stop_flag = true;

    t.join();
    std::cout << "[Головний потік]: Потік успішно завершив виконання.\n";
    return 0;
}
