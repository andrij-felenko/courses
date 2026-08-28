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

class ThreadPool {
public:
    explicit ThreadPool(size_t num_threads, size_t max_queue_size = 1000)
        : max_queue_size_(max_queue_size), stop_(false) {
        if (num_threads == 0) {
            throw std::invalid_argument("Кількість потоків має бути більшою за 0");
        }
        workers_.reserve(num_threads);
        for (size_t i = 0; i < num_threads; ++i) {
            workers_.emplace_back([this]() {
                while (true) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(this->queue_mutex_);
                        // Очікуємо наявності задач або сигналу зупинки (захист від хибних пробуджень)
                        this->cv_not_empty_.wait(lock, [this]() {
                            return this->stop_ || !this->tasks_.empty();
                        });

                        // Якщо надійшов сигнал зупинки і всі задачі виконано — виходимо
                        if (this->stop_ && this->tasks_.empty()) {
                            return;
                        }

                        task = std::move(this->tasks_.front());
                        this->tasks_.pop();
                        this->cv_not_full_.notify_one();
                    }
                    // Виконуємо задачу за межами блокування м'ютекса
                    task();
                }
            });
        }
    }

    // Шаблонний метод постановки завдання, що повертає std::future на результат
    template <typename F, typename... Args>
    auto submit(F&& f, Args&&... args) 
        -> std::future<typename std::invoke_result<F, Args...>::type> {
        using return_type = typename std::invoke_result<F, Args...>::type;

        // Пакуємо виклик функції з аргументами у спільний packaged_task
        auto task_ptr = std::make_shared<std::packaged_task<return_type()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );

        std::future<return_type> res = task_ptr->get_future();
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            // Зворотний тиск: очікуємо звільнення місця в черзі
            cv_not_full_.wait(lock, [this]() {
                return stop_ || tasks_.size() < max_queue_size_;
            });

            if (stop_) {
                throw std::runtime_error("Спроба додати задачу в зупинений пул потоків");
            }

            // Зберігаємо замикання, що виконує packaged_task
            tasks_.emplace([task_ptr]() { (*task_ptr)(); });
        }
        cv_not_empty_.notify_one();
        return res;
    }

    // Деструктор автоматично завершує роботу потоків (RAII)
    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            stop_ = true;
        }
        cv_not_empty_.notify_all();
        cv_not_full_.notify_all();

        for (std::thread &worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }

    // Забороняємо копіювання пулу
    ThreadPool(const ThreadPool&) = delete;
    ThreadPool& operator=(const ThreadPool&) = delete;

private:
    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    std::mutex queue_mutex_;
    std::condition_variable cv_not_empty_;
    std::condition_variable cv_not_full_;
    size_t max_queue_size_;
    bool stop_;
};
