#include <iostream>
#include <deque>
#include <cmath>
#include <optional>
#include <iomanip>
#include <algorithm>

struct Packet {
    int id{0};
    int size_bytes{1500};
    double enqueue_time_ms{0.0};
};

class TailDropQueue {
public:
    explicit TailDropQueue(std::size_t capacity) : capacity_(capacity) {}

    bool enqueue(Packet pkt) {
        total_enqueued_++;
        if (buffer_.size() >= capacity_) {
            total_dropped_++;
            return false; // скидання з хвоста при переповненні
        }
        buffer_.push_back(pkt);
        return true;
    }

    std::optional<Packet> dequeue(double now_ms) {
        if (buffer_.empty()) return std::nullopt;
        Packet pkt = buffer_.front();
        buffer_.pop_front();

        double sojourn = now_ms - pkt.enqueue_time_ms;
        max_sojourn_ms_ = std::max(max_sojourn_ms_, sojourn);
        sum_sojourn_ms_ += sojourn;
        served_packets_++;
        return pkt;
    }

    [[nodiscard]] double average_sojourn_ms() const noexcept {
        return served_packets_ ? sum_sojourn_ms_ / static_cast<double>(served_packets_) : 0.0;
    }
    [[nodiscard]] double max_sojourn_ms() const noexcept { return max_sojourn_ms_; }
    [[nodiscard]] long total_dropped() const noexcept { return total_dropped_; }

private:
    std::size_t capacity_;
    std::deque<Packet> buffer_;
    long total_enqueued_{0};
    long total_dropped_{0};
    long served_packets_{0};
    double max_sojourn_ms_{0.0};
    double sum_sojourn_ms_{0.0};
};

class CodelQueue {
public:
    static constexpr double TargetTimeMs = 5.0;
    static constexpr double IntervalMs = 100.0;

    explicit CodelQueue(std::size_t capacity) : capacity_(capacity) {}

    bool enqueue(Packet pkt) {
        total_enqueued_++;
        if (buffer_.size() >= capacity_) {
            total_dropped_++;
            return false; // аварійне скидання
        }
        buffer_.push_back(pkt);
        return true;
    }

    std::optional<Packet> dequeue(double now_ms) {
        while (!buffer_.empty()) {
            Packet candidate = buffer_.front();
            buffer_.pop_front();

            double sojourn = now_ms - candidate.enqueue_time_ms;
            max_sojourn_ms_ = std::max(max_sojourn_ms_, sojourn);

            bool ok_to_drop = false;
            if (sojourn < TargetTimeMs || buffer_.empty()) {
                first_above_time_ms_ = 0.0;
            } else {
                if (first_above_time_ms_ == 0.0) {
                    first_above_time_ms_ = now_ms + IntervalMs;
                } else if (now_ms >= first_above_time_ms_) {
                    ok_to_drop = true;
                }
            }

            if (dropping_) {
                if (!ok_to_drop) {
                    dropping_ = false;
                } else if (now_ms >= drop_next_ms_) {
                    total_dropped_++;
                    drop_count_++;
                    drop_next_ms_ = control_law(now_ms, drop_count_);
                    continue; // активне скидання затриманого пакета
                }
            } else if (ok_to_drop) {
                dropping_ = true;
                total_dropped_++;
                drop_count_ = 1;
                drop_next_ms_ = control_law(now_ms, 1);
                continue; // перше скидання при переході в DROPPING
            }

            sum_sojourn_ms_ += sojourn;
            served_packets_++;
            return candidate;
        }
        return std::nullopt;
    }

    [[nodiscard]] double average_sojourn_ms() const noexcept {
        return served_packets_ ? sum_sojourn_ms_ / static_cast<double>(served_packets_) : 0.0;
    }
    [[nodiscard]] double max_sojourn_ms() const noexcept { return max_sojourn_ms_; }
    [[nodiscard]] long total_dropped() const noexcept { return total_dropped_; }

private:
    static double control_law(double now_ms, int count) noexcept {
        return now_ms + IntervalMs / std::sqrt(static_cast<double>(count));
    }

    std::size_t capacity_;
    std::deque<Packet> buffer_;
    bool dropping_{false};
    double first_above_time_ms_{0.0};
    double drop_next_ms_{0.0};
    int drop_count_{0};

    long total_enqueued_{0};
    long total_dropped_{0};
    long served_packets_{0};
    double max_sojourn_ms_{0.0};
    double sum_sojourn_ms_{0.0};
};

int main() {
    constexpr double LineRateMbps = 10.0;
    constexpr double BytesPerMs = (LineRateMbps * 1e6) / (8.0 * 1000.0);
    constexpr int SimPackets = 5000;

    TailDropQueue td_queue(100);
    CodelQueue codel_queue(100);

    double now_td = 0.0, next_tx_td = 0.0;
    double now_codel = 0.0, next_tx_codel = 0.0;

    for (int i = 0; i < SimPackets; ++i) {
        double delta = (i % 200 < 50) ? 0.4 : 1.5;
        now_td += delta;
        now_codel += delta;

        Packet pkt{.id = i, .size_bytes = 1500, .enqueue_time_ms = now_td};
        td_queue.enqueue(pkt);
        codel_queue.enqueue(pkt);

        while (next_tx_td <= now_td) {
            auto tx = td_queue.dequeue(next_tx_td);
            if (!tx) break;
            double tx_time = tx->size_bytes / BytesPerMs;
            next_tx_td += tx_time;
        }
        if (next_tx_td < now_td) next_tx_td = now_td;

        while (next_tx_codel <= now_codel) {
            auto tx = codel_queue.dequeue(next_tx_codel);
            if (!tx) break;
            double tx_time = tx->size_bytes / BytesPerMs;
            next_tx_codel += tx_time;
        }
        if (next_tx_codel < now_codel) next_tx_codel = now_codel;
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Результати симуляції (5000 пакетів по 1500 байтів) ===\n";
    std::cout << "Tail Drop: Сер. затримка = " << td_queue.average_sojourn_ms()
              << " мс, Макс. затримка = " << td_queue.max_sojourn_ms()
              << " мс, Скинуто = " << td_queue.total_dropped() << "\n";
    std::cout << "CoDel:     Сер. затримка = " << codel_queue.average_sojourn_ms()
              << " мс, Макс. затримка = " << codel_queue.max_sojourn_ms()
              << " мс, Скинуто = " << codel_queue.total_dropped() << "\n";

    return 0;
}
