#include <iostream>
#include <thread>
#include <future>
#include <vector>

int main() {
    int input_val = 21;

    // Використання std::async та std::future для безпечної передачі результату
    std::future<int> task = std::async(std::launch::async, [input_val]() {
        std::cout << "[Потік worker] Отримано значення: " << input_val << '\n';
        return input_val * 2;
    });

    int result = task.get(); // Блокуюче очікування результату
    std::cout << "[Головний потік] Отримано результат обчислення: " << result << '\n';

    // Демонстрація std::jthread (C++20) з автоматичним join при виході з області видимості
    std::jthread auto_join_thread([](std::stop_token stoken) {
        while (!stoken.stop_requested()) {
            // Робота фонового потоку
            break;
        }
        std::cout << "[std::jthread] Фонова робота завершена коректно\n";
    });

    return 0;
}
