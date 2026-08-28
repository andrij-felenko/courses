#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <map>
#include <mutex>
#include <chrono>
#include <optional>
#include <algorithm>
#include <cstdint>

namespace eip {

using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;

struct Message {
    std::string correlation_id;
    uint64_t sequence_number{0};
    uint64_t sequence_size{0};
    bool is_last{false};
    std::string payload;
};

struct AggregationResult {
    std::string correlation_id;
    std::vector<Message> items;
    bool is_complete{false};
    std::string failure_reason;
};

class ConcurrentAggregator {
public:
    explicit ConcurrentAggregator(std::chrono::milliseconds default_timeout = std::chrono::milliseconds(3000),
                                  std::chrono::seconds tombstone_ttl = std::chrono::seconds(10))
        : default_timeout_(default_timeout), tombstone_ttl_(tombstone_ttl) {}

    // Додавання повідомлення. Якщо кошик завершено, повертає AggregationResult
    std::optional<AggregationResult> process_message(Message msg) {
        const auto now = Clock::now();
        std::lock_guard<std::mutex> lock(mutex_);

        // 1. Перевірка надгробків закритих сесій
        cleanup_tombstones(now);
        if (auto it = tombstones_.find(msg.correlation_id); it != tombstones_.end()) {
            std::cout << "[Aggregator] Відхилено запізнілий елемент для закритого ID: "
                      << msg.correlation_id << " Seq: " << msg.sequence_number << "\n";
            return std::nullopt;
        }

        // 2. Отримання або створення кошика
        auto& bucket = buckets_[msg.correlation_id];
        if (bucket.items.empty()) {
            bucket.correlation_id = msg.correlation_id;
            bucket.created_at = now;
            bucket.last_activity = now;
            bucket.expected_total = msg.sequence_size;
            bucket.timeout = default_timeout_;
        }

        // 3. Дедуплікація за Sequence Number
        for (const auto& existing : bucket.items) {
            if (existing.sequence_number == msg.sequence_number) {
                std::cout << "[Aggregator] Ігнорування дубліката для " << msg.correlation_id
                          << " Seq: " << msg.sequence_number << "\n";
                return std::nullopt;
            }
        }

        // 4. Додавання нового елемента
        bucket.last_activity = now;
        if (msg.is_last) bucket.has_fin = true;
        if (msg.sequence_size > 0) bucket.expected_total = msg.sequence_size;
        bucket.items.push_back(std::move(msg));

        // 5. Оцінка критерію завершення
        bool ready = false;
        if (bucket.expected_total > 0 && bucket.items.size() == bucket.expected_total) {
            ready = true;
        } else if (bucket.has_fin && bucket.expected_total == 0) {
            ready = true;
        }

        if (ready) {
            AggregationResult result;
            result.correlation_id = bucket.correlation_id;
            result.items = std::move(bucket.items);
            result.is_complete = true;

            // Видалення кошика та фіксація надгробка
            buckets_.erase(bucket.correlation_id);
            tombstones_[result.correlation_id] = now + tombstone_ttl_;
            return result;
        }

        return std::nullopt;
    }

    // Фонове сканування активних кошиків на сплив дедлайну
    std::vector<AggregationResult> sweep_timeouts() {
        const auto now = Clock::now();
        std::vector<AggregationResult> expired_results;
        std::lock_guard<std::mutex> lock(mutex_);

        for (auto it = buckets_.begin(); it != buckets_.end(); ) {
            auto& bucket = it->second;
            if (now - bucket.created_at >= bucket.timeout) {
                AggregationResult res;
                res.correlation_id = bucket.correlation_id;
                res.items = std::move(bucket.items);
                res.is_complete = false;
                res.failure_reason = "TIMEOUT_EXPIRED";

                tombstones_[res.correlation_id] = now + tombstone_ttl_;
                expired_results.push_back(std::move(res));
                it = buckets_.erase(it);
            } else {
                ++it;
            }
        }
        return expired_results;
    }

private:
    struct Bucket {
        std::string correlation_id;
        std::vector<Message> items;
        uint64_t expected_total{0};
        TimePoint created_at;
        TimePoint last_activity;
        std::chrono::milliseconds timeout{3000};
        bool has_fin{false};
    };

    void cleanup_tombstones(TimePoint now) {
        for (auto it = tombstones_.begin(); it != tombstones_.end(); ) {
            if (now >= it->second) {
                it = tombstones_.erase(it);
            } else {
                ++it;
            }
        }
    }

    std::mutex mutex_;
    std::chrono::milliseconds default_timeout_;
    std::chrono::seconds tombstone_ttl_;
    std::unordered_map<std::string, Bucket> buckets_;
    std::unordered_map<std::string, TimePoint> tombstones_;
};

// ── Ресеквенсер на базі std::map (Черга за порядковим номером) ─────────────
class StreamResequencer {
public:
    explicit StreamResequencer(uint64_t initial_sequence = 1)
        : next_expected_sequence_(initial_sequence) {}

    std::vector<Message> push(Message msg) {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<Message> drain_batch;

        if (msg.sequence_number >= next_expected_sequence_) {
            buffer_[msg.sequence_number] = std::move(msg);
        }

        // Послідовне вилучення елементів без розривів
        while (!buffer_.empty() && buffer_.begin()->first == next_expected_sequence_) {
            drain_batch.push_back(std::move(buffer_.begin()->second));
            buffer_.erase(buffer_.begin());
            ++next_expected_sequence_;
        }

        return drain_batch;
    }

    uint64_t next_expected() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return next_expected_sequence_;
    }

private:
    mutable std::mutex mutex_;
    uint64_t next_expected_sequence_;
    std::map<uint64_t, Message> buffer_;
};

} // namespace eip
