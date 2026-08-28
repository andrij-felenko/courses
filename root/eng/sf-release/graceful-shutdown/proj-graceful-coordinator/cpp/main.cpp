#include <iostream>
#include <vector>
#include <thread>
#include <stop_token>
#include <future>
#include <chrono>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <csignal>
#include <functional>
#include <memory>

class GracefulShutdownCoordinator {
public:
    using CleanupHook = std::function<void()>;

    explicit GracefulShutdownCoordinator(std::chrono::seconds timeout)
        : timeout_(timeout), is_shutting_down_(false) {}

    ~GracefulShutdownCoordinator() {
        if (!is_shutting_down_.load()) {
            initiate_shutdown();
        }
    }

    std::stop_token get_stop_token() const noexcept {
        return stop_source_.get_token();
    }

    void add_cleanup_hook(CleanupHook hook) {
        std::lock_guard<std::mutex> lock(hooks_mutex_);
        hooks_.push_back(std::move(hook));
    }

    void register_active_request() {
        active_requests_.fetch_add(1, std::memory_order_relaxed);
    }

    void unregister_active_request() {
        if (active_requests_.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            cv_drain_.notify_all();
        }
    }

    void initiate_shutdown() {
        bool expected = false;
        if (!is_shutting_down_.compare_exchange_strong(expected, true)) {
            return; // Вимкнення вже запущено іншим потоком
        }

        std::cout << "[Coordinator] Початок штатного вимкнення. Сигнал усім підсистемам.\n";
        stop_source_.request_stop();

        // Запуск дренажу в окремому асинхронному завданні з контролем дедлайну
        auto drain_future = std::async(std::launch::async, [this]() {
            // Фаза 1: Дренаж активних запитів
            std::unique_lock<std::mutex> lock(drain_mutex_);
            std::cout << "[Coordinator] Очікування завершення " 
                      << active_requests_.load() << " активних запитів...\n";
            
            cv_drain_.wait(lock, [this]() {
                return active_requests_.load() == 0;
            });
            std::cout << "[Coordinator] Усі активні запити завершено успішно.\n";

            // Фаза 2: Виконання хуків очищення у зворотному порядку
            std::lock_guard<std::mutex> hook_lock(hooks_mutex_);
            for (auto it = hooks_.rbegin(); it != hooks_.rend(); ++it) {
                try {
                    (*it)();
                } catch (const std::exception& e) {
                    std::cerr << "[Coordinator] Помилка у хуку очищення: " << e.what() << "\n";
                }
            }
            std::cout << "[Coordinator] Усі хуки очищення виконано.\n";
        });

        // Контроль дедлайну (Watchdog)
        if (drain_future.wait_for(timeout_) == std::future_status::timeout) {
            std::cerr << "[Coordinator] УВАГА: Вичерпано таймаут дренажу (" 
                      << timeout_.count() << " с)! Примусове завершення.\n";
            std::quick_exit(EXIT_FAILURE);
        } else {
            std::cout << "[Coordinator] Штатне вимкнення завершено успішно.\n";
        }
    }

private:
    std::chrono::seconds timeout_;
    std::atomic<bool> is_shutting_down_;
    std::stop_source stop_source_;
    std::atomic<int> active_requests_{0};
    
    std::mutex drain_mutex_;
    std::condition_variable cv_drain_;

    std::mutex hooks_mutex_;
    std::vector<CleanupHook> hooks_;
};

// Глобальний вказівник для сигнального мосту
static std::atomic<GracefulShutdownCoordinator*> g_coordinator{nullptr};

extern "C" void signal_handler(int signo) {
    if (auto* coord = g_coordinator.load()) {
        coord->initiate_shutdown();
    }
}

int main() {
    GracefulShutdownCoordinator coordinator(std::chrono::seconds(5));
    g_coordinator.store(&coordinator);

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    // Додаємо ресурси (наприклад, пул БД та логер)
    coordinator.add_cleanup_hook([]() {
        std::cout << "[Resource] Пул з'єднань із базою даних закрито.\n";
    });
    coordinator.add_cleanup_hook([]() {
        std::cout << "[Resource] Кеш і буферизований логер змито на диск.\n";
    });

    // Запускаємо робочі потоки з підтримкою stop_token (C++20 std::jthread)
    std::vector<std::jthread> workers;
    for (int i = 0; i < 3; ++i) {
        workers.emplace_back([&coordinator, i](std::stop_token st) {
            std::cout << "[Worker " << i << "] Запущено.\n";
            while (!st.stop_requested()) {
                coordinator.register_active_request();
                
                // Імітуємо виконання роботи
                std::this_thread::sleep_for(std::chrono::milliseconds(150));
                
                coordinator.unregister_active_request();
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
            }
            std::cout << "[Worker " << i << "] Зупинився за токеном зупинки.\n";
        }, coordinator.get_stop_token());
    }

    std::cout << "[Server] Головний потік працює. Натисніть Ctrl+C для зупинки...\n";
    
    // Імітація роботи сервера до отримання сигналу
    std::this_thread::sleep_for(std::chrono::milliseconds(600));
    std::cout << "[Server] Імітуємо прихід сигналу SIGTERM...\n";
    coordinator.initiate_shutdown();

    // jthread автоматично викликають join() у своїх деструкторах
    return 0;
}
