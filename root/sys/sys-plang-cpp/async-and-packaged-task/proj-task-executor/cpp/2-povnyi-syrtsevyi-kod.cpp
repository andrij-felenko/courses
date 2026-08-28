#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <future>
#include <functional>
#include <memory>
#include <stdexcept>
#include <chrono>
#include <numeric>

// Клас пулу задач на основі std::packaged_task
class TaskExecutor {
public:
    // Конструктор створює вказану кількість робочих потоків (за замовчуванням — кількість ядер ЦП)
    explicit TaskExecutor(size_t threads = std::thread::hardware_concurrency())
        : stop_(false) 
    {
        if (threads == 0) {
            threads = 1; // Гарантуємо наявність щонайменше одного потоку
        }

        workers_.reserve(threads);
        for (size_t i = 0; i < threads; ++i) {
            workers_.emplace_back([this] { worker_loop(); });
        }
    }

    // Забороняємо копіювання та переміщення пулу
    TaskExecutor(const TaskExecutor&) = delete;
    TaskExecutor& operator=(const TaskExecutor&) = delete;
    TaskExecutor(TaskExecutor&&) = delete;
    TaskExecutor& operator=(TaskExecutor&&) = delete;

    // Деструктор автоматично зупиняє пул і чекає завершення виконання усіх потоків
    ~TaskExecutor() {
        shutdown();
    }

    // Основний шаблонний метод постановки задачі в чергу
    template<typename F, typename... Args>
    auto enqueue(F&& f, Args&&... args) 
        -> std::future<std::invoke_result_t<F, Args...>> 
    {
        using return_type = std::invoke_result_t<F, Args...>;

        // 1. Упаковуємо функцію та її аргументи у безпараметричний функтор packaged_task
        auto task = std::make_shared<std::packaged_task<return_type()>>(
            std::bind_front(std::forward<F>(f), std::forward<Args>(args)...)
        );

        // 2. Отримуємо future, який буде повернено клієнту
        std::future<return_type> res = task->get_future();

        {
            std::unique_lock<std::mutex> lock(queue_mutex_);

            // Забороняємо додавати нові задачі у зупинений пул
            if (stop_) {
                throw std::runtime_error("Спроба додати задачу у зупинений TaskExecutor");
            }

            // 3. Стирання типу: загортаємо виклик task у безпараметричну лямбду void()
            tasks_.emplace([task]() { 
                (*task)(); 
            });
        }

        // 4. Сповіщаємо один із вільних робочих потоків
        cv_.notify_one();
        return res;
    }

    // Ручна зупинка пулу (якщо потрібно зупинити до виклику деструктора)
    void shutdown() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            if (stop_) {
                return; // Вже зупинено
            }
            stop_ = true;
        }

        // Сповіщаємо усі потоки про необхідність виходу
        cv_.notify_all();

        // Очікуємо приєднання кожного потоку
        for (std::thread& worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
        workers_.clear();
    }

private:
    // Цикл виконання робочого потоку
    void worker_loop() {
        while (true) {
            std::function<void()> task;

            {
                std::unique_lock<std::mutex> lock(queue_mutex_);
                
                // Чекаємо появу задачі або прапора зупинки
                cv_.wait(lock, [this] {
                    return stop_ || !tasks_.empty();
                });

                // Якщо пул зупинено і черга порожня — виходимо з потоку
                if (stop_ && tasks_.empty()) {
                    return;
                }

                // Витягуємо задачу з черги
                task = std::move(tasks_.front());
                tasks_.pop();
            }

            // Виконуємо задачу поза блокуванням м'ютекса!
            task();
        }
    }

    std::vector<std::thread> workers_;          // Вектор робочих потоків
    std::queue<std::function<void()>> tasks_;  // Черга типо-стертих задач
    std::mutex queue_mutex_;                   // М'ютекс синхронізації черги
    std::condition_variable cv_;               // Умовна змінна сповіщення потоків
    bool stop_;                                // Прапор аварійної або планової зупинки
};
