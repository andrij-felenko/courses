#include <iostream>
#include <semaphore>
#include <thread>
#include <vector>
#include <span>
#include <chrono>

class ConnectionPoolLimiter {
public:
    explicit ConnectionPoolLimiter(ptrdiff_t max_concurrent)
        : sem_(max_concurrent) {}

    void execute_transaction(int client_id) {
        // Захоплюємо 1 дозвіл із пулу (блокується, якщо всі 4 зайняті)
        sem_.acquire();

        // Критична секція обмеженого ресурсу
        std::cout << "[Клієнт " << client_id << "] Отримав з'єднання. Виконання запиту...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        std::cout << "[Клієнт " << client_id << "] Завершив роботу. Повернення з'єднання.\n";

        // Звільняємо дозвіл для наступного очікуючого клієнта
        sem_.release();
    }

private:
    std::counting_semaphore<16> sem_;
};

int main() {
    ConnectionPoolLimiter limiter(4); // Дозволено максимум 4 одночасні з'єднання
    std::vector<std::jthread> clients;
    clients.reserve(10);

    for (int i = 1; i <= 10; ++i) {
        clients.emplace_back([&limiter, i]() {
            limiter.execute_transaction(i);
        });
    }

    return 0;
}
