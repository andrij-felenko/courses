#include <iostream>
#include <queue>
#include <vector>
#include <string>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <utility>

// Універсальний функціональний тип завдання: поліморфне замикання без спадкування
using Task = std::function<void()>;

class ModernTaskQueue {
private:
    std::queue<Task>        m_queue;
    mutable std::mutex      m_mutex;
    std::condition_variable m_cond;
    bool                    m_shutdown{false}; // Ініціалізація полів класу у C++11

public:
    ModernTaskQueue() = default;

    // Явне блокування копіювання за стандартом C++11
    ModernTaskQueue(const ModernTaskQueue&) = delete;
    ModernTaskQueue& operator=(const ModernTaskQueue&) = delete;

    ~ModernTaskQueue() {
        stop();
    }

    // Прийом довільного виклику за допомогою Perfect Forwarding
    template<typename F>
    void push(F&& f) {
        {
            std::lock_guard<std::mutex> lock(m_mutex); // RAII захоплення м'ютекса
            m_queue.emplace(std::forward<F>(f));       // Створення замикання на місці
        }
        m_cond.notify_one(); // Пробудження одного очікуючого потоку
    }

    // Отримання завдання без сирих покажчиків та без ризику витоку
    bool pop(Task& out_task) {
        std::unique_lock<std::mutex> lock(m_mutex);
        
        // Передача лямбда-предиката для надійного захисту від хибних пробуджень
        m_cond.wait(lock, [this]() {
            return !m_queue.empty() || m_shutdown;
        });

        if (m_shutdown && m_queue.empty()) {
            return false;
        }

        // Переміщення завдання з черги у вихідну змінну за O(1)
        out_task = std::move(m_queue.front());
        m_queue.pop();
        return true;
    }

    void stop() noexcept {
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            m_shutdown = true;
        }
        m_cond.notify_all(); // Широкомовне сповіщення всіх потоків
    }
};

// Практична демонстрація роботи та перевірка відсутності копіювання
int main() {
    ModernTaskQueue queue;

    // Створення пулу фонових потоків через std::thread та лямбда-вираз
    std::thread worker([&queue]() {
        Task current_task;
        while (queue.pop(current_task)) {
            current_task(); // Безпечний виклик замикання
        }
    });

    // 1. Створення масивного корисного навантаження (100 мегабайтів)
    std::vector<char> large_payload(100 * 1024 * 1024, 'A');
    std::cout << "Розмір вихідного вектора до відправлення: " 
              << large_payload.size() / (1024 * 1024) << " МБ\n";

    // 2. Відправлення в чергу через C++14 Init-Capture (переміщення вектора)
    queue.push([tag = std::string("NETWORK_FRAME_8042"), 
                buffer = std::move(large_payload)]() {
        std::cout << "Фоновий потік обробляє [" << tag 
                  << "], обсяг буфера: " << buffer.size() / (1024 * 1024) << " МБ\n";
    });

    // 3. Перевірка стану moved-from у поточному потоці
    std::cout << "Розмір вектора після std::move: " 
              << large_payload.size() << " байтів (пам'ять миттєво передано!)\n";

    // Зупинка черги та коректне очікування завершення потоку
    queue.stop();
    worker.join();

    return 0;
}
