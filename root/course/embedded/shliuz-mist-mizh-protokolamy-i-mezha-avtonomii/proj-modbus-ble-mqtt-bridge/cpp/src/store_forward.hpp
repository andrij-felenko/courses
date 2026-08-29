#pragma once

#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <mutex>
#include <optional>
#include <string>
#include <utility>

namespace gw {

struct TelemetryMessage {
    std::string topic;
    std::string payload;
    std::uint32_t seq{};
};

// Буфер Store-and-Forward: дві черги в одному об'єкті.
//
// Свіжа черга коротка й має пріоритет; переповнившись, вона віддає найстаріше
// в архівну, а переповнена архівна витісняє найдавніше й рахує втрати. Так
// щойно зняті показники ніколи не чекають за спиною в тисяч старих записів.
//
// Знімається повідомлення не тоді, коли пішло в сокет, а тоді, коли брокер
// підтвердив: peek() видає копію в оренду, commit() забирає оригінал.
class StoreForward {
public:
    struct Lease {
        TelemetryMessage msg;
        bool fromBacklog{};
    };

    struct Stats {
        std::size_t fresh{};
        std::size_t backlog{};
        std::uint32_t dropped{};
    };

    StoreForward(std::size_t freshCapacity, std::size_t backlogCapacity)
        : freshCapacity_{freshCapacity}, backlogCapacity_{backlogCapacity} {}

    void publish(TelemetryMessage msg) {
        {
            std::lock_guard lock{mutex_};
            if (fresh_.size() >= freshCapacity_) {
                // Канал стоїть: найстаріше зі свіжого стає історією.
                auto aged = std::move(fresh_.front());
                fresh_.pop_front();
                if (backlog_.size() >= backlogCapacity_) {
                    backlog_.pop_front();
                    ++dropped_;  // розрив у seq покаже серверу масштаб втрати
                }
                backlog_.push_back(std::move(aged));
            }
            fresh_.push_back(std::move(msg));
        }
        ready_.notify_one();
    }

    [[nodiscard]] std::optional<Lease> peek(std::chrono::milliseconds wait) {
        std::unique_lock lock{mutex_};
        ready_.wait_for(lock, wait, [this] { return !fresh_.empty() || !backlog_.empty(); });

        if (!fresh_.empty()) {
            return Lease{fresh_.front(), false};
        }
        if (!backlog_.empty()) {
            return Lease{backlog_.front(), true};
        }
        return std::nullopt;
    }

    // Поки ми чекали підтвердження, витіснення могло зсунути голову черги:
    // знімаємо лише те саме повідомлення, яке справді пішло в сокет.
    void commit(const Lease& lease) {
        std::lock_guard lock{mutex_};
        auto& queue = lease.fromBacklog ? backlog_ : fresh_;
        if (!queue.empty() && queue.front().seq == lease.msg.seq) {
            queue.pop_front();
        }
    }

    [[nodiscard]] Stats stats() const {
        std::lock_guard lock{mutex_};
        return Stats{fresh_.size(), backlog_.size(), dropped_};
    }

private:
    const std::size_t freshCapacity_;
    const std::size_t backlogCapacity_;
    std::deque<TelemetryMessage> fresh_;
    std::deque<TelemetryMessage> backlog_;
    std::uint32_t dropped_{0};
    mutable std::mutex mutex_;
    std::condition_variable ready_;
};

}  // namespace gw
