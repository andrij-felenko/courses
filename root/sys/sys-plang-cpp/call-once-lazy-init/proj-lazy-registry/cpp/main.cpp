#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <mutex>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <atomic>
#include <functional>

// Клас, що моделює важке мережеве з'єднання з віддаленим кластером
class DatabaseConnection {
private:
    std::string endpoint_;
    int socket_id_;

public:
    DatabaseConnection(std::string endpoint, int socket_id)
        : endpoint_(std::move(endpoint)), socket_id_(socket_id) {
        // Імітація тривалого встановлення TLS-сесії
        std::this_thread::sleep_for(std::chrono::milliseconds(40));
    }

    void execute_query(const std::string& query, int thread_id) const {
        std::cout << "[Потік " << thread_id << "] Виконано SQL: '" << query 
                  << "' через сокет #" << socket_id_ << " (" << endpoint_ << ")\n";
    }
};

// Стійкий менеджер лінивого підключення до бази даних
class ResilientConnectionManager {
private:
    std::string host_;
    int port_;
    std::unique_ptr<DatabaseConnection> connection_;
    std::once_flag init_flag_;
    
    // Лічильник для імітації первинного збою мережі
    inline static std::atomic<int> attempt_counter_{0};

    // Внутрішня функція ініціалізації
    void establish_backend_connection(int max_simulated_fails) {
        int current_attempt = ++attempt_counter_;
        std::cout << ">>> [INIT] Спроба налаштування з'єднання #" << current_attempt << "...\n";

        if (current_attempt <= max_simulated_fails) {
            std::cout << ">>> [INIT ERROR] Мережевий таймаут! Викидаємо виняток...\n";
            throw std::runtime_error("Таймаут підключення до " + host_ + ":" + std::to_string(port_));
        }

        // Успішне створення з'єднання
        connection_ = std::make_unique<DatabaseConnection>(host_ + ":" + std::to_string(port_), 2000 + current_attempt);
        std::cout << ">>> [INIT SUCCESS] Пул з'єднань успішно створено!\n";
    }

public:
    ResilientConnectionManager(std::string host, int port)
        : host_(std::move(host)), port_(port) {}

    // Заборона копіювання через наявність std::once_flag та std::unique_ptr
    ResilientConnectionManager(const ResilientConnectionManager&) = delete;
    ResilientConnectionManager& operator=(const ResilientConnectionManager&) = delete;

    void execute(const std::string& sql, int thread_id, int simulated_fail_attempts = 0) {
        // Гарантія суворо одноразового виклику з прозорою обробкою збоїв
        try {
            std::call_once(init_flag_, &ResilientConnectionManager::establish_backend_connection, 
                           this, simulated_fail_attempts);
        } catch (const std::exception& ex) {
            // Виняток перехоплюється потоком, що виконував ініціалізацію.
            // Завдяки семантиці std::call_once стан init_flag_ ЗАЛИШИВСЯ НЕІНІЦІАЛІЗОВАНИМ!
            std::cerr << "[Потік " << thread_id << "] Спіймано помилку ініціалізації: " 
                      << ex.what() << "\n";
            throw; // Ретранслюємо виняток клієнту
        }

        // Швидкий шлях: connection_ гарантовано ініціалізований для всіх потоків
        connection_->execute_query(sql, thread_id);
    }
};

int main() {
    std::cout << "=== Тестування лінивої ініціалізації з транзакційним відновленням ===\n\n";

    ResilientConnectionManager manager("db-primary.prod.network", 5432);

    // Сценарій 1: Перший потік стикається з мережевим збоєм
    std::cout << "--- Фаза 1: Перший запит зазнає невдачі через збій зв'язку ---\n";
    std::thread t1([&]() {
        try {
            manager.execute("SELECT * FROM users WHERE id = 42;", 1, /*simulated_fails=*/1);
        } catch (...) {
            std::cout << "[Клієнт 1] Запит провалився, заплановано повторну спробу пізніше.\n";
        }
    });
    t1.join();

    // Сценарій 2: Масовий запуск 6 паралельних потоків після відновлення зв'язку
    std::cout << "\n--- Фаза 2: Конкурентний запуск 6 потоків після відновлення зв'язку ---\n";
    std::vector<std::thread> workers;
    for (int i = 2; i <= 7; ++i) {
        workers.emplace_back([&manager, i]() {
            try {
                manager.execute("SELECT * FROM orders WHERE account_id = " + std::to_string(i), i, /*simulated_fails=*/1);
            } catch (const std::exception& e) {
                std::cerr << "[Потік " << i << "] Помилка: " << e.what() << "\n";
            }
        });
    }

    for (auto& w : workers) {
        w.join();
    }

    std::cout << "\n=== Всі операції завершено успішно ===\n";
    return 0;
}
