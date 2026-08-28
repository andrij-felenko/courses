#include <iostream>
#include <thread>
#include <string>
#include <chrono>

int main() {
    std::cout << "--- 1. Успішна передача значення ---" << std::endl;
    {
        custom::custom_promise<std::string> promise;
        custom::custom_future<std::string> future = promise.get_future();

        std::thread worker([p = std::move(promise)]() mutable {
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            p.set_value("Результат обчислень готовий!");
        });

        std::cout << "Головний потік чекає..." << std::endl;
        std::string res = future.get();
        std::cout << "Отримано: " << res << std::endl;
        worker.join();
    }

    std::cout << "\n--- 2. Передача винятку через межу потоків ---" << std::endl;
    {
        custom::custom_promise<int> promise;
        custom::custom_future<int> future = promise.get_future();

        std::thread worker([p = std::move(promise)]() mutable {
            try {
                throw std::invalid_argument("Помилка вхідних даних у фоновому потоці!");
            } catch (...) {
                p.set_exception(std::current_exception());
            }
        });

        try {
            int val = future.get();
            std::cout << "Значення: " << val << std::endl;
        } catch (const std::exception& e) {
            std::cout << "Перехоплено виняток у головному потоці: " << e.what() << std::endl;
        }
        worker.join();
    }

    return 0;
}
