#pragma once

// Демпферна черга між приймачем і воркерами: обмежена місткість, два ватерпости
// з гістерезисом і витіснення найстарішого пакета, коли місця не лишилося зовсім.

#include "wire_format.hpp"

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <mutex>
#include <utility>

namespace ingest {

// Ватерпости зашиті в саму чергу: піднімаємо тиск на 80%, знімаємо на 50%.
// Різниця між порогами і є гістерезис — без неї прапорець тремтів би на кожному пакеті.
inline constexpr double kHighRatio = 0.80;
inline constexpr double kLowRatio = 0.50;

enum class PopStatus { ok, timeout, closed };
enum class PushStatus { stored, evicted_oldest, rejected_closed };

class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity)
        : capacity_(capacity),
          high_watermark_(static_cast<std::size_t>(capacity * kHighRatio)),
          low_watermark_(static_cast<std::size_t>(capacity * kLowRatio)) {}

    BoundedQueue(const BoundedQueue&) = delete;
    BoundedQueue& operator=(const BoundedQueue&) = delete;

    PushStatus push(RawPacket packet) {
        PushStatus status = PushStatus::stored;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (closed_) {
                return PushStatus::rejected_closed;
            }
            if (items_.size() >= capacity_) {
                // Місця немає: свіжі дані цінніші за протухлі — викидаємо найстаріший.
                items_.pop_front();
                dropped_.fetch_add(1, std::memory_order_relaxed);
                status = PushStatus::evicted_oldest;
            }
            items_.push_back(std::move(packet));
            if (items_.size() >= high_watermark_) {
                backpressure_.store(true, std::memory_order_release);
            }
        }
        // Будимо воркера вже поза м'ютексом, щоб він не прокинувся на замкнені двері.
        cv_.notify_one();
        return status;
    }

    PopStatus pop(RawPacket& out, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        // Предикат обов'язковий: без нього хибне пробудження виглядало б як пакет.
        if (!cv_.wait_for(lock, timeout, [this] { return !items_.empty() || closed_; })) {
            return PopStatus::timeout;
        }
        if (items_.empty()) {
            return PopStatus::closed;  // чергу закрили і вона допита до дна
        }

        out = std::move(items_.front());
        items_.pop_front();
        if (items_.size() <= low_watermark_) {
            backpressure_.store(false, std::memory_order_release);
        }
        return PopStatus::ok;
    }

    // Закриття не рве обробку: воркери спершу допивають залишок черги.
    void close() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            closed_ = true;
        }
        cv_.notify_all();
    }

    // Приймач питає це на кожному пакеті — і жодного разу не бере м'ютекс.
    bool backpressure() const noexcept {
        return backpressure_.load(std::memory_order_acquire);
    }

    std::uint64_t dropped() const noexcept {
        return dropped_.load(std::memory_order_relaxed);
    }

    std::size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return items_.size();
    }

private:
    const std::size_t capacity_;
    const std::size_t high_watermark_;
    const std::size_t low_watermark_;

    mutable std::mutex mutex_;
    std::condition_variable cv_;
    std::deque<RawPacket> items_;
    bool closed_{false};

    // Гарячі атоміки — кожен у своїй кеш-лінії. Інакше читання прапорця приймачем
    // і запис лічильника воркером ганяли б одну лінію по шині когерентності.
    alignas(64) std::atomic<bool> backpressure_{false};
    alignas(64) std::atomic<std::uint64_t> dropped_{0};
};

}  // namespace ingest
