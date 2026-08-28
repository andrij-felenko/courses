#include <iostream>
#include <vector>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <stop_token>
#include <exception>
#include <stdexcept>
#include <chrono>
#include <string>

// Потокобезпечна черга з підтримкою скасування через condition_variable_any
template <typename T>
class ThreadSafeQueue {
private:
    std::queue<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable_any cv_;

public:
    void push(T item) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            queue_.push(std::move(item));
        }
        cv_.notify_one();
    }

    bool pop(T& item, std::stop_token st) {
        std::unique_lock<std::mutex> lock(mutex_);
        
        // Очікування даних або сигналу скасування
        bool acquired = cv_.wait(lock, st, [this] { 
            return !queue_.empty(); 
        });

        if (!acquired || st.stop_requested()) {
            return false; // Отримано сигнал скасування або порожня черга
        }

        item = std::move(queue_.front());
        queue_.pop();
        return true;
    }
};

// Структура результату обробки
struct PipelineTask {
    int id;
    double payload;
};

class DataPipeline {
private:
    ThreadSafeQueue<PipelineTask> queue_;
    std::vector<std::jthread> workers_;
    std::exception_ptr first_exception_{nullptr};
    std::mutex exception_mutex_;
    std::stop_source global_stop_source_;

public:
    void start(size_t worker_count) {
        for (size_t i = 0; i < worker_count; ++i) {
            // std::jthread автоматично передає stop_token першим аргументом
            workers_.emplace_back([this](std::stop_token st, size_t worker_id) {
                worker_loop(st, worker_id);
            }, i);
        }
    }

    void submit(PipelineTask task) {
        queue_.push(task);
    }

    void stop_and_join() {
        // Надіслати сигнал зупинки всім потокам
        global_stop_source_.request_stop();
        
        // Деструктори std::jthread автоматично викличуть join() при виході workers_ з області видимості
        workers_.clear();

        // Перевірка наявності збереженого винятку
        if (first_exception_) {
            std::rethrow_exception(first_exception_);
        }
    }

private:
    void worker_loop(std::stop_token st, size_t worker_id) {
        // Поєднання локального stop_token із глобальним джерелом скасування
        std::stop_callback cb(st, [this] {
            // Сповіщаємо чергу про настання сигналу зупинки
        });

        PipelineTask task;
        while (!st.stop_requested() && queue_.pop(task, st)) {
            try {
                process_single_task(task, worker_id);
            } catch (...) {
                // Зберегти перший виняток та ініціювати зупинку всього конвеєра
                std::lock_guard<std::mutex> lock(exception_mutex_);
                if (!first_exception_) {
                    first_exception_ = std::current_exception();
                    global_stop_source_.request_stop();
                }
                break;
            }
        }
    }

    void process_single_task(const PipelineTask& task, size_t worker_id) {
        if (task.payload < 0.0) {
            throw std::runtime_error("Помилка даних: від'ємне корисне навантаження у завданні #" 
                                     + std::to_string(task.id));
        }
        
        // Імітація обчислювальної роботи
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
};

int main() {
    try {
        DataPipeline pipeline;
        pipeline.start(4);

        // Відправка коректних завдань
        for (int i = 0; i < 10; ++i) {
            pipeline.submit({i, i * 1.5});
        }

        // Відправка некоректного завдання для перевірки винятку
        pipeline.submit({99, -1.0});

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        pipeline.stop_and_join();
    } catch (const std::exception& e) {
        std::cout << "Головний потік перехопив помилку конвеєра: " << e.what() << std::endl;
    }
    return 0;
}
