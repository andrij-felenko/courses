#include <iostream>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <functional>
#include <cstdint>

// Декларативна фільтрація полів (FieldMask)
using FieldMask = uint32_t;

struct SensorReading {
    uint32_t sensor_id;
    int64_t  timestamp_ns;
    float    temperature_celsius;
    float    battery_voltage;
    uint32_t status_flags;
};

class AdaptiveMicroBatcher {
public:
    using FlushCallback = std::function<void(const std::vector<SensorReading>&, FieldMask)>;

    AdaptiveMicroBatcher(size_t capacity, size_t max_batch_size,
                         std::chrono::milliseconds timeout,
                         FieldMask field_mask, bool enable_conflation,
                         FlushCallback flush_callback)
        : capacity_(capacity),
          max_batch_size_(std::min(max_batch_size, capacity)),
          timeout_(timeout),
          field_mask_(field_mask),
          enable_conflation_(enable_conflation),
          flush_callback_(std::move(flush_callback)),
          running_(true) {
        buffer_.reserve(capacity_);
        worker_thread_ = std::thread(&AdaptiveMicroBatcher::worker_loop, this);
    }

    ~AdaptiveMicroBatcher() {
        stop();
    }

    // Додавання показника зі згортанням стану за ідентифікатором та зворотним тиском
    bool push(SensorReading reading) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!running_) return false;

        // Згортання стану (conflation) з миттєвим пошуком через хеш-таблицю O(1)
        if (enable_conflation_) {
            auto it = key_to_index_.find(reading.sensor_id);
            if (it != key_to_index_.end()) {
                buffer_[it->second] = reading;
                return true;
            }
        }

        // Реактивний зворотний тиск: виробник блокується при досягненні ємності
        cv_producer_.wait(lock, [this] {
            return !running_ || buffer_.size() < capacity_;
        });
        if (!running_) return false;

        if (enable_conflation_) {
            key_to_index_[reading.sensor_id] = buffer_.size();
        }
        buffer_.push_back(reading);

        // Будимо робочий потік при першому елементі або досягненні N_batch
        if (buffer_.size() >= max_batch_size_ || buffer_.size() == 1) {
            cv_worker_.notify_one();
        }
        return true;
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (!running_) return;
            running_ = false;
        }
        cv_worker_.notify_all();
        cv_producer_.notify_all();
        if (worker_thread_.joinable()) {
            worker_thread_.join();
        }
    }

private:
    void worker_loop() {
        std::unique_lock<std::mutex> lock(mutex_);
        while (running_) {
            // Очікуємо появи хоча б одного елемента
            cv_worker_.wait(lock, [this] {
                return !running_ || !buffer_.empty();
            });
            if (!running_ && buffer_.empty()) break;

            auto deadline = std::chrono::steady_clock::now() + timeout_;

            // Очікуємо або досягнення N_batch, або спливу таймауту T_wait
            cv_worker_.wait_until(lock, deadline, [this] {
                return !running_ || buffer_.size() >= max_batch_size_;
            });

            if (!buffer_.empty()) {
                // Швидкий обмін буферів (buffer swap) для усунення затримок виробників
                std::vector<SensorReading> batch_to_send;
                batch_to_send.swap(buffer_);
                key_to_index_.clear();

                // Сповіщаємо заблокованих виробників
                cv_producer_.notify_all();

                // Виклик відправлення виконується поза м'ютексом
                lock.unlock();
                if (flush_callback_) {
                    flush_callback_(batch_to_send, field_mask_);
                }
                lock.lock();
            }
        }
    }

    const size_t capacity_;
    const size_t max_batch_size_;
    const std::chrono::milliseconds timeout_;
    const FieldMask field_mask_;
    const bool enable_conflation_;
    const FlushCallback flush_callback_;

    bool running_;
    std::vector<SensorReading> buffer_;
    std::unordered_map<uint32_t, size_t> key_to_index_;

    std::mutex mutex_;
    std::condition_variable cv_worker_;
    std::condition_variable cv_producer_;
    std::thread worker_thread_;
};
